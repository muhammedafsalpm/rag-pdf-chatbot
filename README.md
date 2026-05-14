# PDF RAG Assistant - Production Ready

## Complete RAG System with BGE Embeddings & Multi-LLM Support

### Features Implemented ✅
- PDF upload and processing with page citations
- BGE-large embedding model (1024 dimensions)
- Chroma vector database for retrieval
- Multi-LLM support (Ollama local + OpenAI)
- Conversation history tracking
- Grounded answers with source citations
- FastAPI backend + Streamlit frontend

## Quick Start

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env` to root directory and set:
- `LLM_PROVIDER=ollama` or `openai`
- API keys if using OpenAI

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

### 5. For Ollama Users (Optional)
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2
ollama serve
```

## Models Used

**Embedding:** BAAI/bge-large-en-v1.5
- Dimensions: 1024
- Best open-source embedding for RAG
- Normalized embeddings for cosine similarity

**LLM Options:**
- Ollama: llama3.2 (free, local)
- OpenAI: gpt-4o-mini (API key required)

## Chunking Strategy
- Size: 1000 characters
- Overlap: 200 characters
- Preserves semantic boundaries

## Retrieval Strategy
- Cosine similarity search
- Top K: 5 chunks
- BGE normalized embeddings

## Testing the Application

1. Upload any PDF document
2. Ask questions like:
   - "What is the main topic of this document?"
   - "Summarize page 3"
   - "What are the key findings?"
3. Answers include page citations
4. Follow-up questions maintain context

## Known Limitations
- First query after upload takes 2-3 seconds (embedding generation)
- Large PDFs (>100 pages) may take 30+ seconds to process
- Complex tables/columns may have extraction issues

## Architecture Decisions

**Why BGE embeddings?**
- Top performer on MTEB leaderboard
- Optimized for information retrieval
- 1024 dimensions balance accuracy/speed

**Why ChromaDB?**
- Persistent local storage
- HNSW indexing for fast search
- No external dependencies

**Why FastAPI + Streamlit?**
- Clear separation of concerns
- Easy to scale backend
- Simple interactive frontend
