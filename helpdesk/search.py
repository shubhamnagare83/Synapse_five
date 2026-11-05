import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from helpdesk.ingest import load_ingested_chunks

def search(question: str, k: int = 3) -> list:
    """
    Searches extracted document chunks for relevant passages.
    Prioritizes ChromaDB vector search if available, and seamlessly falls back
    to robust keyword-matching on extracted chunks from rhd_ingestion/output/chunks.json.
    """
    # 1. Try vector similarity search with ChromaDB if available
    try:
        from rhd_ingestion.chroma_store import search_chroma
        chroma_res = search_chroma(question, k=k)
        if chroma_res and "documents" in chroma_res and chroma_res["documents"] and chroma_res["documents"][0]:
            matched = []
            docs = chroma_res["documents"][0]
            metas = chroma_res["metadatas"][0] if "metadatas" in chroma_res and chroma_res["metadatas"] else [{}] * len(docs)
            for text, meta in zip(docs, metas):
                matched.append({
                    "doc": meta.get("source", "railway_policy"),
                    "source": meta.get("source", "railway_policy"),
                    "page": meta.get("page"),
                    "text": text
                })
            if matched:
                return matched
    except Exception:
        pass

    # 2. Fallback / direct search on extracted chunks
    chunks = load_ingested_chunks()
    q_words = [w.lower() for w in question.split() if len(w) > 2]
    scored_chunks = []

    for chunk in chunks:
        text_lower = chunk["text"].lower()
        score = sum(1 for word in q_words if word in text_lower)
        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_chunks[:k]]
