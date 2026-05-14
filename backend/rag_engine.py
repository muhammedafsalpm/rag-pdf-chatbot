from typing import List, Dict, Tuple
import openai
import ollama
from config import Config

class RAGEngine:
    """RAG pipeline with LLM integration"""
    
    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        
        if self.provider == "openai":
            openai.api_key = Config.OPENAI_API_KEY
            self.model = Config.OPENAI_MODEL
        else:  # ollama
            self.model = Config.OLLAMA_MODEL
            ollama_client = ollama.Client(host=Config.OLLAMA_BASE_URL)
    
    def create_prompt(self, question: str, context_chunks: List, chat_history: List = None) -> str:
        """Create prompt with context and history"""
        
        # Format context with citations
        context_text = ""
        for chunk_text, metadata, score in context_chunks:
            context_text += f"[Source: {metadata['citation']}]\n{chunk_text}\n\n"
        
        # Format chat history
        history_text = ""
        if chat_history:
            history_text = "Previous conversation:\n"
            for msg in chat_history[-6:]:  # Last 3 exchanges
                history_text += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n\n"
        
        prompt = f"""You are a helpful assistant answering questions based ONLY on the provided document context.

{history_text}
CONTEXT FROM DOCUMENT:
{context_text}

QUESTION: {question}

INSTRUCTIONS:
1. Answer based ONLY on the context above
2. If answer not in context, say "I cannot find this information in the document"
3. Always cite sources using [Page X]
4. Be concise but complete

ANSWER:"""
        
        return prompt
    
    def generate_answer(self, prompt: str) -> str:
        """Generate answer using configured LLM"""
        
        if self.provider == "openai":
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise document QA assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        
        else:  # ollama
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise document QA assistant."},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": 0.3,
                    "num_predict": 500
                }
            )
            return response['message']['content']
