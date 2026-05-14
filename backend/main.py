from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import tempfile
import os

from pdf_processor import PDFProcessor
from chunker import DocumentChunker
from embeddings import EmbeddingModel
from vector_store import VectorStore
from rag_engine import RAGEngine

app = FastAPI(title="PDF RAG API", version="1.0")

# CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
embedding_model = EmbeddingModel()
vector_store = VectorStore(embedding_model)
rag_engine = RAGEngine()
pdf_processor = PDFProcessor()
chunker = DocumentChunker()

# In-memory chat history storage (per session)
chat_sessions = {}

class QuestionRequest(BaseModel):
    question: str
    session_id: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[str]
    sources: List[Dict]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "llm_provider": rag_engine.provider}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    
    try:
        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Process PDF
        with open(tmp_path, 'rb') as f:
            pages = pdf_processor.extract_pages(f)
        
        # Create chunks
        chunks = chunker.create_chunks(pages)
        
        # Add to vector store
        num_chunks = vector_store.add_documents(chunks)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return {
            "status": "success",
            "filename": file.filename,
            "pages": len(pages),
            "chunks": num_chunks
        }
    
    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")

@app.post("/ask", response_model=ChatResponse)
async def ask_question(request: QuestionRequest):
    """Ask question with RAG"""
    
    # Search for relevant chunks
    retrieved_chunks = vector_store.search(request.question)
    
    if not retrieved_chunks:
        return ChatResponse(
            answer="No documents uploaded. Please upload a PDF first.",
            citations=[],
            sources=[]
        )
    
    # Get chat history for this session
    session_history = chat_sessions.get(request.session_id, [])
    
    # Generate answer
    prompt = rag_engine.create_prompt(
        request.question, 
        retrieved_chunks,
        session_history
    )
    answer = rag_engine.generate_answer(prompt)
    
    # Extract citations
    citations = list(set([meta['citation'] for _, meta, _ in retrieved_chunks]))
    
    # Update chat history
    if request.session_id not in chat_sessions:
        chat_sessions[request.session_id] = []
    
    chat_sessions[request.session_id].append({
        "user": request.question,
        "assistant": answer
    })
    
    # Keep only last 10 exchanges
    if len(chat_sessions[request.session_id]) > 10:
        chat_sessions[request.session_id] = chat_sessions[request.session_id][-10:]
    
    sources = [
        {"page": meta['page'], "citation": meta['citation'], "relevance_score": score}
        for _, meta, score in retrieved_chunks
    ]
    
    return ChatResponse(
        answer=answer,
        citations=citations,
        sources=sources
    )

@app.post("/clear")
async def clear_session(session_id: str):
    """Clear chat history for a session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return {"status": "cleared"}

@app.post("/clear_all")
async def clear_all():
    """Clear all documents and history"""
    vector_store.clear_all()
    chat_sessions.clear()
    return {"status": "all data cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
