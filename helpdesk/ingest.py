import json
import os


CHUNKS_FILE_PATH = os.path.join("rhd_ingestion", "output", "final_chunks.json")

def load_ingested_chunks():
    """
    Directly loads pre-processed chunks from your teammate's chunks.json file.
    """
    if not os.path.exists(CHUNKS_FILE_PATH):
        raise FileNotFoundError(
            f"Pre-saved chunks not found at {CHUNKS_FILE_PATH}. "
            "Please ensure your teammate's chunks.json file is placed in the correct directory."
        )

    with open(CHUNKS_FILE_PATH, "r", encoding="utf-8") as f:
        chunks_data = json.load(f)
        
    return chunks_data

if __name__ == "__main__":
    chunks = load_ingested_chunks()
    print(f"Successfully loaded {len(chunks)} chunks from teammate's chunks.json!")