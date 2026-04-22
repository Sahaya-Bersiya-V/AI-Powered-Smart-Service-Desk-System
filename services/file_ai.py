import pytesseract
from PIL import Image
import pdfplumber
import fitz

def extract_image_text(file_path):
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)

def extract_pdf_text(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text(file_path, filename):
    try:
        text = ""

        # IMAGE FILE
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)

        # PDF FILE
        elif filename.lower().endswith(".pdf"):
            pdf = fitz.open(file_path)

            for page in pdf:
                page_text = page.get_text()

            
                if page_text.strip():
                    text += page_text

                
                else:
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    text += pytesseract.image_to_string(img)

        print("FINAL TEXT LENGTH:", len(text))  

        return text.strip()

    except Exception as e:
        print("OCR ERROR:", e)
        return ""