import os
import json

def search(question: str, k: int = 3):
    """
    Searches the ingested document chunks for the given question.
    Returns top k chunks with document name and page number.
    """
    # Simple keyword or index-based matching placeholder 
    # (Integrate your team's vector search / TF-IDF / BM25 index here)
    index_path = "index/chunks.json"
    if not os.path.exists(index_path):
        return []
        
    with open(index_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        
    # Basic keyword overlap scoring as a baseline
    q_words = set(question.lower().split())
    scored = []
    for chunk in chunks:
        content = chunk.get("content", "").lower()
        score = sum(1 for word in q_words if word in content)
        if score > 0:
            scored.append((score, chunk))
            
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:k]]