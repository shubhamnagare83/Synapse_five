import os
from helpdesk.llm import generate_content_with_retry

def generate_grounded_answer(question: str, chunks: list) -> dict:
    """
    Generates a grounded answer from retrieved chunks using Gemini with retry handling.
    """
    if not chunks:
        return {
            "answer": "I don't know based on the provided documents.",
            "sources": [],
            "dont_know": True
        }

    context_text = "\n\n".join([f"Source: {c['doc']} (Page {c['page']})\n{c['text']}" for c in chunks])
    
    prompt = f"""You are an expert Indian Railways help desk assistant. Answer the user's question using ONLY the provided document chunks below. 
If the information is not present, respond with "I don't know". Note that newer circulars override older rules if they conflict.

Context:
{context_text}

Question: {question}

Return your response clearly addressing the question, and list the exact sources used."""

    try:
        response = generate_content_with_retry(prompt, model='gemini-3.8-flash')
        answer_text = response.text
    except Exception as e:
        answer_text = f"Error generating answer after retries: {str(e)}"

    sources = [{"doc": c["doc"], "page": c["page"]} for c in chunks]
    is_dont_know = "i don't know" in answer_text.lower() or not answer_text.strip()

    return {
        "answer": answer_text,
        "sources": sources if not is_dont_know else [],
        "dont_know": is_dont_know
    }