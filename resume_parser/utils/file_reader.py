# utils/file_reader.py
import os
import pdfplumber
from docx import Document
import mammoth
import pypandoc
from pdf2image import convert_from_path
import pytesseract

def read_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    if not text.strip():
        # Use OCR
        images = convert_from_path(file_path)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
    return text.strip()

def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

def read_doc(file_path):
    with open(file_path, "rb") as doc_file:
        result = mammoth.extract_raw_text(doc_file)
    return result.value.strip()

def read_with_pandoc(file_path):
    try:
        return pypandoc.convert_file(file_path, "plain").strip()
    except (OSError, RuntimeError):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()

def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()

def read_resume(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return read_pdf(file_path)
    elif ext == ".docx":
        return read_docx(file_path)
    elif ext == ".doc":
        return read_doc(file_path)
    elif ext in [".rtf", ".odt", ".md", ".html", ".htm"]:
        return read_with_pandoc(file_path)
    elif ext == ".txt":
        return read_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
