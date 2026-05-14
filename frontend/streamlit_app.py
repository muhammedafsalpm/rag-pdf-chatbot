import streamlit as st
import requests
import uuid

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False

st.set_page_config(
    page_title="PDF RAG Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("PDF RAG Assistant with Citations")
st.markdown("Ask questions about your PDF documents and get grounded answers with source citations")

# Sidebar
with st.sidebar:
    st.header("Upload Document")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file:
        if st.button("Process PDF", type="primary"):
            with st.spinner("Processing PDF... This may take a moment..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=120)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ Processed: {data['pages']} pages, {data['chunks']} chunks")
                        st.session_state.pdf_processed = True
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend. Make sure backend is running on port 8000")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat"):
            try:
                requests.post(f"{API_BASE_URL}/clear", params={"session_id": st.session_state.session_id})
            except:
                pass
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All"):
            try:
                requests.post(f"{API_BASE_URL}/clear_all")
            except:
                pass
            st.session_state.messages = []
            st.session_state.pdf_processed = False
            st.rerun()
    
    st.divider()
    
    # Status display
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health.status_code == 200:
            data = health.json()
            st.info(f"""
            **Status:** ✅ Connected
            **LLM:** {data['llm_provider']}
            **Model:** {data['model']}
            **Session:** {st.session_state.session_id[:8]}...
            **Messages:** {len(st.session_state.messages)}
            """)
        else:
            st.warning("⚠️ Backend not responding")
    except:
        st.error("❌ Backend not reachable")

# Main chat interface
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
    
    if not st.session_state.pdf_processed:
        with st.chat_message("assistant"):
            error_msg = "⚠️ Please upload and process a PDF first using the sidebar."
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
    else:
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching document and generating answer..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/ask",
                        json={
                            "question": prompt,
                            "session_id": st.session_state.session_id
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.markdown(data["answer"])
                        if data["citations"]:
                            st.caption(f"📌 Sources: {', '.join(data['citations'])}")
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": data["answer"],
                            "citations": data["citations"]
                        })
                    else:
                        error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
                except requests.exceptions.Timeout:
                    error_msg = "Request timed out. The document might be large or the LLM is slow."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                except requests.exceptions.ConnectionError:
                    error_msg = "Cannot connect to backend. Make sure backend is running on port 8000"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
