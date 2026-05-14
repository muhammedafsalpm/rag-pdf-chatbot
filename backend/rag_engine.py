from typing import List, Dict, Tuple
import openai
import requests
import json
from config import Config

class RAGEngine:
    """RAG pipeline with LLM integration"""
    
    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        
        if self.provider == "openai":
            openai.api_key = Config.OPENAI_API_KEY
            self.model = Config.OPENAI_MODEL
            print(f"Using OpenAI with model: {self.model}")
        else:
            self.model = Config.OLLAMA_MODEL
            self.ollama_url = Config.OLLAMA_BASE_URL
            print(f"Using Ollama with model: {self.model} at {self.ollama_url}")
    
    def create_prompt(self, question: str, context_chunks: List, chat_history: List = None) -> str:
        """Create prompt with context and history"""
        
        # Format context with citations
        context_text = ""
        for chunk_text, metadata, score in context_chunks:
            context_text += f"[Source: {metadata['citation']}]\n{chunk_text}\n\n"
        
        # Format chat history
        history_text = ""
        if chat_history and len(chat_history) > 0:
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
            try:
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a precise document QA assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Error with OpenAI: {str(e)}"
        
        else:  # ollama
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 500
                        }
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', 'No response generated')
                else:
                    return f"Ollama error: {response.status_code} - Make sure Ollama is running with 'ollama serve'"
            except requests.exceptions.ConnectionError:
                return "Cannot connect to Ollama. Please run 'ollama serve' in terminal"
            except Exception as e:
                return f"Error with Ollama: {str(e)}"
