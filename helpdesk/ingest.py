import json
import os
from pathlib import Path

# Look for chunks file with multiple fallback paths
BASE_DIR = Path(__file__).resolve().parent.parent

CANDIDATE_PATHS = [
    BASE_DIR / "rhd_ingestion" / "output" / "chunks.json",
    BASE_DIR / "rhd_ingestion" / "output" / "final_chunks.json",
    BASE_DIR / "index" / "chunks.json",
    Path("rhd_ingestion/output/chunks.json"),
    Path("rhd_ingestion/output/final_chunks.json"),
    Path("index/chunks.json")
]

def load_and_chunk_documents():
    """
    Alias for load_ingested_chunks() to ensure full backward compatibility.
    """
    return load_ingested_chunks()

def load_ingested_chunks():
    """
    Directly loads extracted chunks from rhd_ingestion/output/chunks.json (or final_chunks.json).
    Normalizes chunk schema so fields 'doc' (or 'source'), 'page', and 'text' are always accessible.
    """
    chunks_file = None
    for p in CANDIDATE_PATHS:
        if p.exists():
            chunks_file = p
            break

    if not chunks_file:
        raise FileNotFoundError(
            f"Pre-saved chunks not found at any of: {[str(p) for p in CANDIDATE_PATHS]}. "
            "Please ensure chunks.json exists."
        )

    with open(chunks_file, "r", encoding="utf-8") as f:
        raw_chunks = json.load(f)

    # Normalize fields: ensure both 'doc' and 'source', 'page', 'text' exist
    normalized = []
    for c in raw_chunks:
        doc = c.get("doc") or c.get("source") or (c.get("metadata", {}).get("source") if isinstance(c.get("metadata"), dict) else "unknown")
        page = c.get("page")
        if page is None and isinstance(c.get("metadata"), dict):
            page = c["metadata"].get("page")
        text = c.get("text", "")
        
        chunk_entry = dict(c)
        chunk_entry["doc"] = doc
        chunk_entry["source"] = doc
        chunk_entry["page"] = page
        chunk_entry["text"] = text
        normalized.append(chunk_entry)

    return normalized

if __name__ == "__main__":
    chunks = load_ingested_chunks()
    print(f"Successfully loaded {len(chunks)} chunks!")
