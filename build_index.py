from helpdesk.ingest import load_and_chunk_documents
import json
import os

if __name__ == "__main__":
    os.makedirs("index", exist_ok=True)
    chunks = load_and_chunk_documents()
    with open("index/chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
    print(f"Index built successfully with {len(chunks)} chunks.")