import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM Provider Selection
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    
    # OpenAI Config
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Ollama Config
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    
    # Embedding Config - Using smaller model for compatibility
    EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # Smaller, faster, still good
    EMBEDDING_DIMENSION = 384
    
    # Chunking Config
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Retrieval Config
    TOP_K_RESULTS = 5
    
    # Vector DB Path
    VECTOR_DB_PATH = "./storage/chroma_db"
