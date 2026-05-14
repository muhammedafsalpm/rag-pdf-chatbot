import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM Provider Selection
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    
    # OpenAI Config
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Ollama Config
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # Embedding Config
    EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
    EMBEDDING_DIMENSION = 1024
    
    # Chunking Config
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Retrieval Config
    TOP_K_RESULTS = 5
    
    # Vector DB Path
    VECTOR_DB_PATH = "./storage/chroma_db"
