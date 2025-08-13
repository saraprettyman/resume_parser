"""
file_reader.py

Utility functions for reading resumes from various file formats 
(.pdf, .docx, .doc, .rtf, .odt, .md, .html, .txt).
Supports both text-based extraction and OCR fallback for scanned PDFs.
"""

import os
import pdfplumber
from docx import Document
import mammoth
import pypandoc
from pdf2image import convert_from_path
import pytesseract


def read_pdf(file_path: str) -> str:
    """
    Reads a PDF file and extracts text.

    Attempts text extraction via `pdfplumber`.  
    If no text is found (e.g., scanned PDF), falls back to OCR using `pytesseract`.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text as a single string.
    """
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    if not text.strip():  # OCR fallback
        images = convert_from_path(file_path)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"

    return text.strip()


def read_docx(file_path: str) -> str:
    """
    Reads a .docx file and extracts text.

    Args:
        file_path: Path to the DOCX file.

    Returns:
        Extracted text as a single string.
    """
    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


def read_doc(file_path: str) -> str:
    """
    Reads a legacy .doc file using `mammoth` for text extraction.

    Args:
        file_path: Path to the DOC file.

    Returns:
        Extracted text as a single string.
    """
    with open(file_path, "rb") as doc_file:
        result = mammoth.extract_raw_text(doc_file)
    return result.value.strip()


def read_with_pandoc(file_path: str) -> str:
    """
    Reads various file formats using Pandoc as a converter.

    Supported extensions: .rtf, .odt, .md, .html, .htm.

    Falls back to plain text reading if Pandoc is unavailable or fails.

    Args:
        file_path: Path to the file.

    Returns:
        Extracted text as a single string.
    """
    try:
        return pypandoc.convert_file(file_path, "plain").strip()
    except (OSError, RuntimeError):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()


def read_txt(file_path: str) -> str:
    """
    Reads a plain text file.

    Args:
        file_path: Path to the TXT file.

    Returns:
        File contents as a string.
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()


def read_resume(file_path: str) -> str:
    """
    Reads a resume file of various supported formats and returns its text content.

    Supported extensions:
        - .pdf  (with OCR fallback)
        - .docx
        - .doc
        - .rtf
        - .odt
        - .md
        - .html / .htm
        - .txt

    Args:
        file_path: Path to the resume file.

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If the file extension is unsupported.
    """
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
