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

def generate_content_with_retry(prompt: str, model: str = "gemini-2.5-flash", max_retries: int = 3, backoff_factor: float = 2.0):
    """
    Calls Gemini API with built-in wait-and-retry logic for 503 / temporary unavailability.
    """
    client = get_gemini_client()
    delay = 2.0
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response
        except Exception as e:
            err_msg = str(e)
            # Check if it's a temporary 503 UNAVAILABLE or high demand error
            if ("503" in err_msg or "UNAVAILABLE" in err_msg or "RESOURCE_EXHAUSTED" in err_msg) and attempt < max_retries - 1:
                print(f"[Warning] Gemini API unavailable/busy (Attempt {attempt + 1}/{max_retries}). Retrying in {delay}s...")
                time.sleep(delay)
                delay *= backoff_factor
            else:
                raise e