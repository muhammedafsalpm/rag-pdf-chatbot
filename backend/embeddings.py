from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from config import Config

class EmbeddingModel:
    """BGE embedding model - production ready"""
    
    def __init__(self):
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.dimension = Config.EMBEDDING_DIMENSION
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """Embed single query"""
        embedding = self.model.encode([query], normalize_embeddings=True)
        return embedding[0].tolist()
