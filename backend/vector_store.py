import chromadb
from chromadb.config import Settings
from typing import List, Dict, Tuple
import uuid
import os
from config import Config

class VectorStore:
    """ChromaDB vector store for document retrieval"""
    
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        
        # Create storage directory if not exists
        os.makedirs(Config.VECTOR_DB_PATH, exist_ok=True)
        
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=Config.VECTOR_DB_PATH,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="pdf_documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[Dict]) -> int:
        """Add chunks to vector store"""
        ids = [str(uuid.uuid4()) for _ in chunks]
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_model.embed_documents(texts)
        
        # Add to Chroma
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        return len(chunks)
    
    def search(self, query: str, k: int = None) -> List[Tuple[str, Dict, float]]:
        """Search for relevant chunks"""
        if k is None:
            k = Config.TOP_K_RESULTS
        
        query_embedding = self.embedding_model.embed_query(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        retrieved = []
        for doc, meta, dist in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            retrieved.append((doc, meta, dist))
        
        return retrieved
    
    def clear_all(self):
        """Clear all documents"""
        self.client.delete_collection("pdf_documents")
        self.collection = self.client.create_collection("pdf_documents")
