from PyPDF2 import PdfReader
from typing import List, Dict
import re

class PDFProcessor:
    """Extract text from PDF with page tracking"""
    
    @staticmethod
    def extract_pages(pdf_file) -> List[Dict]:
        """Extract text per page"""
        reader = PdfReader(pdf_file)
        pages = []
        
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            # Clean text
            text = re.sub(r'\n+', '\n', text)
            text = re.sub(r'\s+', ' ', text)
            
            pages.append({
                'page_number': page_num,
                'text': text,
                'total_pages': len(reader.pages)
            })
        
        return pages
