"""PDF text extraction module."""

import fitz  # PyMuPDF
from typing import List, Tuple
import re


def extract_text_from_pdf(pdf_bytes: bytes) -> List[Tuple[int, str]]:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_bytes: The PDF file as bytes.
        
    Returns:
        List of tuples containing (page_number, page_text).
    """
    pages = []
    
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Clean up the text
            text = clean_text(text)
            
            if text.strip():
                pages.append((page_num + 1, text))
        
        doc.close()
        
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    return pages


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text.
    
    Args:
        text: Raw text from PDF.
        
    Returns:
        Cleaned text.
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might cause issues
    text = text.replace('\x00', '')
    
    # Normalize line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def get_full_text(pdf_bytes: bytes) -> str:
    """
    Get the full text content of a PDF as a single string.
    
    Args:
        pdf_bytes: The PDF file as bytes.
        
    Returns:
        Full text content.
    """
    pages = extract_text_from_pdf(pdf_bytes)
    return "\n\n".join([text for _, text in pages])
