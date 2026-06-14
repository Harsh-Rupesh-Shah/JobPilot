"""
resume_parser.py
Extracts plain text from PDF and DOCX files.
"""

import fitz  # PyMuPDF
import docx

async def extract_text_from_file(file_path: str, ext: str) -> str:
    """
    Extracts text from a given file path based on its extension.
    Supported extensions: pdf, docx
    """
    if ext == "pdf":
        return _extract_from_pdf(file_path)
    elif ext == "docx":
        return _extract_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

def _extract_from_pdf(file_path: str) -> str:
    """Extracts text from a PDF file using PyMuPDF."""
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
    except Exception as e:
        raise RuntimeError(f"Error parsing PDF: {e}")
    return text.strip()

def _extract_from_docx(file_path: str) -> str:
    """Extracts text from a DOCX file using python-docx."""
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        raise RuntimeError(f"Error parsing DOCX: {e}")
    return text.strip()
