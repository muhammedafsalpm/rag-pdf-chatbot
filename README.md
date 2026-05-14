# PDF RAG Assistant - Production Ready (Fixed)

## Complete RAG System with BGE Embeddings & Multi-LLM Support

### Features Implemented ✅
- PDF upload and processing with page citations
- BGE-small embedding model (384 dimensions) - **Fixed for compatibility**
- Chroma vector database for retrieval
- Multi-LLM support (Ollama local + OpenAI)
- Conversation history tracking
- Grounded answers with source citations
- FastAPI backend + Streamlit frontend

## Quick Start

### 1. Fix Dependencies (CRITICAL)
```bash
# Uninstall conflicting packages
pip uninstall sentence-transformers huggingface-hub chromadb langchain -y

# Install fresh
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
Set `LLM_PROVIDER=ollama` or `openai` in `.env`.

### 3. Start Backend Server
```bash
cd backend
python main.py
# Server runs on http://localhost:8000
```

### 4. Start Frontend (new terminal)
```bash
cd frontend
streamlit run streamlit_app.py
# App opens on http://localhost:8501
```

### 5. For Ollama Users
```bash
ollama pull llama2
ollama serve
```

## Models Used

**Embedding:** BAAI/bge-small-en-v1.5
- Dimensions: 384
- High performance, faster than large versions

**LLM Options:**
- Ollama: llama3.2 (free, local)
- OpenAI: gpt-3.5-turbo (API key required)
