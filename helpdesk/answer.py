import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_grounded_answer(question: str, context_chunks: list):
    """
    Generates an answer using Gemini based strictly on the provided context chunks.
    """
    if not context_chunks:
        return {
            "answer": "I don't know based on the provided documents.",
            "sources": [],
            "dont_know": True
        }
        
    context_text = ""
    sources = []
    for chunk in context_chunks:
        doc = chunk.get("doc")
        page = chunk.get("page")
        context_text += f"\n--- Source: {doc} (Page: {page}) ---\n{chunk.get('content')}\n"
        sources.append({"doc": doc, "page": page})

    prompt = f"""You are an official Indian Railways passenger help desk assistant.
Answer the user's question accurately using ONLY the provided official documents below. 
If the documents disagree because rules changed over time, the newer document wins.
If the answer is not present in the documents, state "I don't know".

Question: {question}

Context Documents:
{context_text}

Answer in plain words:"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    answer_text = response.text.strip()
    if "i don't know" in answer_text.lower():
        return {"answer": answer_text, "sources": [], "dont_know": True}

    return {
        "answer": answer_text,
        "sources": sources,
        "dont_know": False
    }