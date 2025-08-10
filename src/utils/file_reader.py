"""
file_reader.py
Responsible for reading resume files (.pdf or .docx) and extracting raw text.
"""

import pdfplumber
from docx import Document

def read_pdf(file_path):
    """Extract text from a PDF file."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # Prevent NoneType errors
                text += page_text + "\n"
    return text

def read_docx(file_path):
    """Extract text from a DOCX file."""
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])
