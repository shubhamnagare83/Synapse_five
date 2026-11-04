import os
import pypdf
from pdf2image import convert_from_path
import pytesseract

def load_and_chunk_documents(data_dir="data/documents"):
    """
    Loads text and scanned PDFs from the documents folder, 
    applies OCR where necessary, and chunks them for search.
    """
    chunks = []
    
    # Example structure to parse files in your data pack
    if not os.path.exists(data_dir):
        print(f"Directory {data_dir} not found. Ensure rail_capstone_pack is extracted.")
        return chunks

    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)
        
        if filename.endswith(".pdf"):
            # Check for scanned PDFs (like circulars 10/2024, 08/2025, 10/2025)
            reader = pypdf.PdfReader(filepath)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                
                # Fallback to OCR if page text is empty or sparse (scanned PDF)
                if not text or len(text.strip()) < 50:
                    images = convert_from_path(filepath, first_page=page_num, last_page=page_num)
                    if images:
                        text = pytesseract.image_to_string(images[0])
                
                chunks.append({
                    "doc": filename,
                    "page": page_num,
                    "content": text.strip()
                })
                
        elif filename.endswith(".html"):
            with open(filepath, "r", encoding="utf-8") as f:
                html_text = f.read()
                chunks.append({
                    "doc": filename,
                    "page": None, # HTML files have no page numbers
                    "content": html_text.strip()
                })
                
    return chunks