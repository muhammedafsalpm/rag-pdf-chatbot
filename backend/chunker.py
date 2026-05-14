from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
from config import Config

class DocumentChunker:
    """Intelligent chunking with citation preservation"""
    
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
    
    def create_chunks(self, pages: List[Dict]) -> List[Dict]:
        """Create chunks with page citations"""
        chunks = []
        
        for page in pages:
            # Split page text into chunks
            chunk_texts = self.splitter.split_text(page['text'])
            
            for chunk_id, chunk_text in enumerate(chunk_texts):
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'page': page['page_number'],
                        'chunk_id': chunk_id,
                        'citation': f"Page {page['page_number']}"
                    }
                })
        
        return chunks
