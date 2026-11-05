# Railway Passenger Help Desk — Capstone Project (Synapse Five)

An end-to-end, multi-lingual AI Help Desk for Indian Railways passengers. The system blends a **Retrieval-Augmented Generation (RAG)** pipeline over official Ministry circulars with an intelligent **Text-to-SQL Engine** querying real railway timetables to answer both policy/rule questions and operational train schedule inquiries.

---

## 1. System Architecture

```text
                                  [Passenger Inquiry via ask.py]
                                                │
                                                ▼
                                     [helpdesk/pipeline.py]
                                  (Intelligent Intent Router)
                                          ╱            ╲
                Timetable / Train Timings               Policy / Circular / Booking
                        │                                           │
                        ▼                                           ▼
                 [Text-to-SQL Engine]                     [ChromaDB Vector Store]
                 - Strict Read-Only Check                 - 145 Extracted Chunks
                 - LLM Generates SELECT SQL               - Cosine Similarity (384-d)
                        │                                           │
                        ▼                                           ▼
              [SQLite: rail_timetable.db]                 [helpdesk/answer.py]
              - stations, trains, schedules, stops         - Grounded LLM Generation
                        │                                           │
                        └───────────────────┬───────────────────────┘
                                            ▼
                                 [Structured JSON Output]
                                 - answer
                                 - sources (if policy query)
                                 - sql_query (if timetable query)
                                 - dont_know (boolean flag)
```

---

## 2. Concepts Used in Each Phase

### Phase 1: Ingestion & Document Processing (`rhd_ingestion/`)
* **Multi-format Document Extraction**: Scrapes official HTML circulars, native PDFs, and scanned notifications using `pypdf`, `beautifulsoup4`, and `RapidOCR` fallbacks.
* **Hierarchical Chunking**: Respects boundary structures, legal sub-clauses, and Hindi Devanagari full stops (*Purna Viram - ।*) to preserve context.
* **Vector Embeddings & Storage**: Produces 384-dimensional dense vector embeddings using local ONNX `all-MiniLM-L6-v2` and persists them into **ChromaDB** (`railway_passenger_rules` collection).

### Phase 2: Intent Routing & Pipeline Core (`helpdesk/`)
* **Hybrid Query Routing**: Differentiates operational timetable requests from regulatory/circular questions using keyword patterns, token heuristics, and 5-digit train number regex matching.
* **Multi-lingual Query Support**: Transparently processes Hindi and Hinglish passenger inquiries (e.g., *"वंदे भारत स्लीपर एक्सप्रेस के लिए नियम"*, *"mai ticket 1 hour pehle book kar sakthe kya?"*).
* **Strict Read-Only Text-to-SQL Engine**:
  * Targets SQLite database at `helpdesk/database/rail_timetable.db` (5,208 trains, 8,990 stations, 417,080 schedules).
  * Enforces `is_safe_readonly_sql()`: permits only `SELECT` and `WITH` statements.
  * Blocks any mutation keyword (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `EXEC`, `PRAGMA`).
  * Connects using SQLite URI read-only flag (`?mode=ro`).
* **Grounded Answer Generation**: Ensures LLM responses are strictly grounded in retrieved circular chunks, explicitly admitting *"I don't know based on the provided documents"* when information is out of scope.

### Phase 3: Comprehensive Evaluation Suite (`eval/`)
Measures retrieval performance, generation quality, and grounding using standard Information Retrieval (IR) metrics and Ragas compatibility:

| Metric | Category | Formula / Definition | Purpose |
| :--- | :--- | :--- | :--- |
| **Hit Rate @ K** (`Hit@3`) | Retrieval | $\text{Hit@K} = \begin{cases} 1 & \text{if relevant doc in top } K \\ 0 & \text{otherwise} \end{cases}$ | Verifies if at least one authoritative circular appears in top $K$. |
| **Mean Reciprocal Rank (MRR)** | Retrieval | $\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$ | Measures how early the first relevant source appears in search results. |
| **Precision @ K** (`Precision@3`) | Retrieval | $\frac{|\text{Relevant Retrieved Documents in Top } K|}{K}$ | Evaluates retrieval purity and noise minimization. |
| **Recall @ K** (`Recall@3`) | Retrieval | $\frac{|\text{Relevant Retrieved Documents in Top } K|}{|\text{Total Expected Documents}|}$ | Measures coverage of all necessary ground-truth circulars. |
| **Context Recall** | Context Grounding | Overlap between retrieved contexts and ground-truth statements. | Ensures retrieved context contains all required facts to formulate the answer. |
| **Context Precision** | Context Grounding | Mean average precision of relevant chunks within the retrieved context. | Evaluates whether relevant signal chunks rank higher than irrelevant context. |
| **Ragas Integration** | RAG Assessment | `context_precision`, `context_recall`, `faithfulness`, `answer_relevancy`. | Native evaluation pipeline with fallback execution when system DLL restrictions prevent PyArrow loading. |

---

## 3. Repository Structure

```text
Synapse_five/
├── ask.py                       # Single unified entry point for queries
├── requirements.txt             # Project dependencies
├── .env.example                 # Template for API credentials
├── README.md                    # Project documentation
│
├── helpdesk/                    # Core Help Desk application
│   ├── answer.py                # LLM answer synthesis with strict grounding
│   ├── ingest.py                # Normalized loader for extracted document chunks
│   ├── llm.py                   # Gemini client with retry & model fallback
│   ├── pipeline.py              # Central query router (RAG vs Text-to-SQL)
│   ├── search.py                # Vector search retriever (ChromaDB + fallback)
│   ├── sql.py                   # Strict read-only Text-to-SQL executor
│   └── database/
│       ├── rail_timetable.db    # SQLite database (2016 snapshot)
│       └── schema.md            # Database documentation & table schemas
│
├── rhd_ingestion/               # Document ingestion & vector indexing
│   ├── chroma_store.py          # ChromaDB persistent collection manager
│   ├── chunker.py               # Rule-aware chunking pipeline
│   ├── extractor.py             # PDF & HTML parser
│   ├── documents/               # Official PDF & HTML circulars
│   └── output/
│       ├── chunks.json          # Pre-saved document chunks
│       └── final_chunks.json    # Complete extracted chunks (145 items)
│
└── eval/                        # Evaluation Suite
    ├── evaluate.py              # Metrics evaluation script (Hit Rate, MRR, Context)
    ├── test_set.json            # 10 ground-truth evaluation test cases
    ├── sample_questions.json    # Reference validation dataset
    └── experiments.md           # Benchmark experiment logs and performance
```

---

## 4. Installation & Setup

### Prerequisites
* Python 3.10, 3.11, or higher
* Google Gemini API Key

### Steps

1. **Clone the repository and enter directory**:
   ```bash
   git clone https://github.com/shubhamnagare83/Synapse_five.git
   cd Synapse_five
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows:
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API Key**:
   Create a `.env` file in the `Synapse_five` root:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

---

## 5. How to Run

### Interactive Mode
Run `ask.py` without arguments:
```bash
python ask.py
```
You will be prompted:
```text
Railway Help Desk (Synapse Five)
================================
Enter your railway inquiry: 
```

### Direct CLI Query Mode

#### 1. Train Schedule / Timings Query (Text-to-SQL)
```bash
python ask.py "train timings from chennai to banglore"
```
**Output:**
```json
{
  "answer": "Train Number | Train Name | Departure | Arrival | Duration Min | Distance Km\n----------------------------------------------------------------------------\n12027 | CHENNAI CENT - BANGALORE CITY Shatabdi Exp | 17:30 | 22:30 | 300 | 362\n12607 | CHENNAI CENTRAL - BANGALORE Lalbagh Exp | 15:35 | 21:35 | 360 | 358\n12609 | CHENNAI CENT - BANGALORE SF Intercity Exp | 13:35 | 20:05 | 390 | 362\n12639 | CHENNAI CENT - BANGALORE Brindavan Exp | 07:15 | 13:20 | 365 | 362\n12657 | CHENNAI - BANGALORE Mail | 23:15 | 05:10 | 355 | 362",
  "sources": [],
  "sql_query": "SELECT t.number AS train_number, t.name AS train_name, t.departure, t.arrival, t.duration_min, t.distance_km \nFROM trains t\nJOIN stations s1 ON t.from_station_code = s1.code\nJOIN stations s2 ON t.to_station_code = s2.code\nWHERE (s1.name LIKE '%CHENNAI%' OR s1.name LIKE '%MADRAS%')\n  AND (s2.name LIKE '%BANGALORE%' OR s2.name LIKE '%BENGALURU%');",
  "dont_know": false
}
```

#### 2. Specific Train Departure / Arrival Query
```bash
python ask.py "What is the departure and arrival time of train 12951?"
```
**Output:**
```json
{
  "answer": "• Departure: 16:40\n• Arrival: 08:30",
  "sources": [],
  "sql_query": "SELECT departure, arrival FROM trains WHERE number = '12951';",
  "dont_know": false
}
```

#### 3. Policy / Circular Query (Document RAG)
```bash
python ask.py "What is the advance reservation period for train tickets?"
```
**Output:**
```json
{
  "answer": "Based on the provided documents, with effect from 01.11.2024, the time limit for advance reservations (Advance Reservation Period / ARP) by trains has been reduced from 120 days to 60 days (excluding the date/day of journey)...",
  "sources": [
    {
      "doc": "rb_cc10_2024_advance_reservation.pdf",
      "page": 1
    }
  ],
  "dont_know": false,
  "sql_query": null
}
```

#### 4. Multi-lingual Query
```bash
python ask.py "वंदे भारत स्लीपर एक्सप्रेस के लिए टिकट रद्दीकरण प्रभार क्या हैं?"
```
**Output:**
```json
{
  "answer": "वंदे भारत स्लीपर एक्सप्रेस के लिए यदि टिकट 72 घंटे से अधिक पहले रद्द किया जाता है, तो प्रभार 25% है। 72 घंटे से 8 घंटे के बीच 50% प्रभार है...",
  "sources": [
    {
      "doc": "rb_cc08_2026_vande_bharat_sleeper_refund.pdf",
      "page": 5
    }
  ],
  "dont_know": false,
  "sql_query": null
}
```

---

## 6. Running the Evaluation Suite

Run the evaluation script to calculate all retrieval and context metrics across the test dataset:

```bash
python eval/evaluate.py
```

### Benchmark Results

```text
=======================================================
           EVALUATION SUMMARY RESULTS
=======================================================
  Hit Rate @ 3          : 1.0000 (100.0%)
  MRR                   : 1.0000
  Precision @ 3         : 0.9667 (96.67%)
  Recall @ 3            : 1.0000 (100.0%)
  Context Recall        : 0.8631 (86.31%)
  Context Precision     : 1.0000 (100.0%)
=======================================================
```
Detailed experiment documentation can be viewed in [eval/experiments.md](eval/experiments.md).
