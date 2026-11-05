import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

def get_gemini_client():
    """
    Initializes and returns the official Gemini API client.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from environment variables or .env file.")
    return genai.Client(api_key=api_key)

def generate_content_with_retry(prompt: str, model: str = "gemini-3.5-flash-lite", max_retries: int = 2, backoff_factor: float = 1.5):
    """
    Calls Gemini API with quick retry logic.
    Falls back gracefully across active models in Google GenAI (gemini-3.5-flash-lite, gemini-3.8-flash, gemini-3-flash-preview).
    """
    client = get_gemini_client()
    delay = 1.0
    
    candidate_models = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3-flash-preview"]
    if model in candidate_models:
        candidate_models.remove(model)
        candidate_models.insert(0, model)
    else:
        candidate_models.insert(0, model)

    last_exception = None
    for target_model in candidate_models:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=target_model,
                    contents=prompt
                )
                return response
            except Exception as e:
                last_exception = e
                err_msg = str(e)
                if ("503" in err_msg or "UNAVAILABLE" in err_msg or "RESOURCE_EXHAUSTED" in err_msg) and attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= backoff_factor
                elif "404" in err_msg or "NOT_FOUND" in err_msg:
                    break
                else:
                    break

    raise last_exception

