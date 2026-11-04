import json
import os

INDEX_PATH = "index/chunks.json"

def search(question: str, k: int = 3) -> list:
    """
    Searches the built chunk index for relevant document passages.
    """
    if not os.path.exists(INDEX_PATH):
        from helpdesk.ingest import load_and_chunk_documents
        chunks = load_and_chunk_documents()
    else:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            chunks = json.load(f)

    q_lower = question.lower()
    scored_chunks = []

    for chunk in chunks:
        text_lower = chunk["text"].lower()
        score = sum(1 for word in q_lower.split() if word in text_lower)
        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_chunks[:k]]