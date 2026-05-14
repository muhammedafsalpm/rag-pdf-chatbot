import streamlit as st
import requests
import uuid
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False

# Page config
st.set_page_config(
    page_title="PDF RAG Assistant",
    page_icon="📚",
    layout="wide"
)

# Title
st.title("📚 PDF RAG Assistant with Citations")
st.markdown("Ask questions about your PDF documents and get grounded answers with source citations")

# Sidebar
with st.sidebar:
    st.header("📄 Upload Document")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file:
        if st.button("Process PDF"):
            with st.spinner("Processing PDF..."):
                files = {"file": uploaded_file}
                response = requests.post(f"{API_BASE_URL}/upload", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"✅ Processed: {data['pages']} pages, {data['chunks']} chunks")
                    st.session_state.pdf_processed = True
                else:
                    st.error(f"Error: {response.json()}")
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History"):
        requests.post(f"{API_BASE_URL}/clear", params={"session_id": st.session_state.session_id})
        st.session_state.messages = []
        st.rerun()
    
    if st.button("🗑️ Clear All Data"):
        requests.post(f"{API_BASE_URL}/clear_all")
        st.session_state.messages = []
        st.session_state.pdf_processed = False
        st.rerun()
    
    st.divider()
    st.info(f"""
    **Status:**
    - LLM Provider: {requests.get(f"{API_BASE_URL}/health").json().get('llm_provider', 'unknown') if st.session_state.pdf_processed else 'Not connected'}
    - Session ID: {st.session_state.session_id[:8]}...
    - Messages: {len(st.session_state.messages)}
    """)

# Main chat interface
chat_container = st.container()

with chat_container:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "citations" in message and message["citations"]:
                st.caption(f"📌 Sources: {', '.join(message['citations'])}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your PDF..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Check if PDF is processed
        if not st.session_state.pdf_processed:
            with st.chat_message("assistant"):
                error_msg = "Please upload and process a PDF first."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            # Get answer from backend
            with st.chat_message("assistant"):
                with st.spinner("Retrieving information..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/ask",
                            json={
                                "question": prompt,
                                "session_id": st.session_state.session_id
                            }
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Display answer
                            st.markdown(data["answer"])
                            if data["citations"]:
                                st.caption(f"📌 Sources: {', '.join(data['citations'])}")
                            
                            # Add to history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": data["answer"],
                                "citations": data["citations"]
                            })
                        else:
                            st.error("Error getting response")
                    
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to backend. Make sure backend is running on port 8000")
