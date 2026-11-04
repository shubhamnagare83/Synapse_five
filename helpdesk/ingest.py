import os
import pymupdf  # Updated from fitz to avoid future deprecation warnings
from bs4 import BeautifulSoup

DOCS_DIR = "data/documents"

def load_and_chunk_documents():
    """
    Parses all PDFs and HTML files in data/documents/ 
    and returns a list of chunks containing text, document filename, and page number.
    """
    chunks = []
    if not os.path.exists(DOCS_DIR):
        return chunks

    for filename in sorted(os.listdir(DOCS_DIR)):
        file_path = os.path.join(DOCS_DIR, filename)
        
        if filename.endswith(".pdf"):
            try:
                doc = pymupdf.open(file_path)
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text()
                    
                    if not text.strip():
                        text = f"[Scanned Page content on page {page_num + 1} of {filename}]"
                        
                    chunks.append({
                        "doc": filename,
                        "page": page_num + 1,
                        "text": text.strip()
                    })
            except Exception as e:
                print(f"Error reading PDF {filename}: {e}")
                
        elif filename.endswith(".html"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    text = soup.get_text()
                    chunks.append({
                        "doc": filename,
                        "page": None,  # HTML files have no page numbers
                        "text": text.strip()
                    })
            except Exception as e:
                print(f"Error reading HTML {filename}: {e}")
                
    return chunks