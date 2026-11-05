# Railway Passenger Help Desk — Capstone Project

Welcome to the Railway Passenger Help Desk Capstone Project repository. This system integrates official railway rules, live timetable data, and policy documents to provide accurate, context-aware answers to passenger queries.

---

## 1. System Architecture

The project combines a Retrieval-Augmented Generation (RAG) pipeline with a relational database query engine to handle both policy lookups and real-time train schedule details.
[Official Circulars & Web Pages]
├── Native & Scanned PDFs (ARP, Refund Rules, Tatkal)
└── HTML Circulars & PIB Announcements
│
▼
[rhd_ingestion Package]
├── [extractor.py] (pypdf + RapidOCR Fallback)
├── [chunker.py] (Hierarchical & Purna-Viram Splitting)
└── [chroma_store.py] (384-d ONNX Embeddings + ChromaDB)
│
▼
+-------------------------------------------------------+
|             RAILWAY CAPSTONE CORE PIPELINE            |
|                                                       |
|  [User Query / CLI] ---> [helpdesk/pipeline.py]       |
|                               ├── SQL Engine          |
|                               │   (helpdesk/sql.py)   |
|                               │   (Read-only SQLite)  |
|                               │                       |
|                               └── Vector Retrieval    |
|                                   (ChromaDB HNSW)     |
|                                         │             |
|                                         ▼             |
|                              [helpdesk/answer.py]     |
|                            (Gemini LLM Synthesis)     |
|                                         │             |
|                                         ▼             |
|                              [Grounded Response]      |
+-------------------------------------------------------+

## 2. Repository Structure

```text
├── database/
│   └── rail_timetable.db        # SQLite timetable database (2016 snapshot)
├── helpdesk/
│   ├── __init__.py
│   ├── ingest.py                # Loads pre-processed chunks from rhd_ingestion
│   ├── sql.py                   # Strict read-only Text-to-SQL execution module
│   ├── search.py                # Vector search retriever module
│   ├── answer.py                # LLM response generation with grounding
│   └── pipeline.py              # Central ask(question) query router
├── rhd_ingestion/
│   └── output/
│       └── chunks.json          # Pre-generated document chunks
├── ask.py                       # Command-line interface entry point
├── requirements.txt             # Project Python dependencies
└── README.md                    # Project documentation

3. Installation & Setup
Prerequisites

    Python 3.10 or higher

    A free Gemini API key

3. Installation & Setup
Prerequisites

    Python 3.10 or higher

    A free Gemini API key

Steps

    1.Clone the repository and navigate to the project directory:

    Bash

    git clone [https://github.com/shubhamnagare83/Synapse_five.git](https://github.com/shubhamnagare83/Synapse_five.git)
    cd Railway_Capstone

    2.Create and activate a virtual environment:

    Bash

    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate

    3.Install the required dependencies:

    Bash

    pip install -r requirements.txt

    4.Set up your environment variables by creating a .env file in the root directory:

    Code snippet

    GEMINI_API_KEY=your_api_key_here   


4. Running Queries

You can test queries directly from the command line using the ask.py runner script:

Bash

python ask.py "What are the rules for booking Tatkal tickets?"

Bash

python ask.py "Which trains run from New Delhi to Mumbai Central?"


---

### How to commit this README:
Once you save the file in your root folder, run these commands in your terminal:
```bash
git add README.md
git commit -m "docs: add project README.md architecture and setup guide"
git push origin main