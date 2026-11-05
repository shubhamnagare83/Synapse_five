Railway Passenger Help Desk — Capstone Project

Welcome to the Railway Passenger Help Desk Capstone Project repository. This system integrates official railway rules, live timetable data, and policy documents to provide accurate, context-aware answers to passenger queries in English and Hindi.
1. System Architecture

The project combines a robust Retrieval-Augmented Generation (RAG) pipeline with a relational database query engine to handle both policy lookup and real-time train status information.

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

2. Project Directory Structure

railway_capstone/
├── ask.py                  # Main CLI entry point for passenger queries
├── build_index.py          # Script to build or refresh indexes
├── documents/              # Official PDF circulars, gazettes, and HTML files
├── helpdesk/               # Core application package
│   ├── __init__.py
│   ├── answer.py           # Gemini LLM response synthesis
│   ├── ingest.py           # Document ingestion handler
│   ├── llm.py              # LLM client configuration (Gemini endpoint)
│   ├── pipeline.py         # End-to-end orchestration (SQL + Vector)
│   ├── search.py           # Search utilities
│   └── sql.py              # Secure read-only SQLite execution (?mode=ro)
├── rhd_ingestion/          # Teammate's ingestion & vectorization module
│   ├── __init__.py
│   ├── extractor.py        # Bilingual text & OCR extraction
│   ├── chunker.py          # Semantic & sliding-window chunker
│   ├── chroma_store.py     # ChromaDB vector indexer & query utility
│   ├── run_pipeline.py     # Orchestrator producing final_chunks.json
│   ├── test_search.py      # Benchmark and interactive retrieval tests
│   ├── output/             # Generated structured chunks (final_chunks.json)
│   └── chroma_db/          # Persistent local ChromaDB vector store
└── README.md

3. Installation & Setup
Prerequisites

    Python 3.10 or higher

    Virtual environment recommended

1. Clone and Install Dependencies

Install all required libraries for both the core pipeline and the ingestion module:
Bash

# Install core and ingestion dependencies
pip install pypdf>=6.17.0 pypdfium2>=5.14.0 beautifulsoup4>=4.14.3 rapidocr>=3.10.0 onnxruntime>=1.20.0 chromadb>=1.5.0 numpy>=1.22.5 pillow>=10.0.0

4. Running the Ingestion & Vector Pipeline

If you need to re-process the raw official documents and update the vector database from scratch:
Bash

# Step 1: Run text extraction and chunking
python rhd_ingestion/run_pipeline.py

# Step 2: Generate embeddings and populate ChromaDB
python rhd_ingestion/chroma_store.py

5. Testing & Verification

You can verify retrieval accuracy across both English and Hindi rules (such as Advance Reservation Period changes, cancellation charges, and Tatkal authentication) by running the benchmark suite:
Bash

# Run predefined benchmark tests
python rhd_ingestion/test_search.py

# Launch interactive terminal query mode
python rhd_ingestion/test_search.py --interactive

6. Querying the Helpdesk

To ask a question through the main entry point:
Bash

python ask.py "What is the advance reservation period for booking train tickets?"