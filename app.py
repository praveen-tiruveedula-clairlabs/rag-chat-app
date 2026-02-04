"""
RAG AI Chat App - Streamlit UI.
Run: streamlit run app.py
Ensure vector_db/ exists (run python ingest.py first) and GROQ_API_KEY is set.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

st.title("RAG AI Chat App")

@st.cache_resource
def load_chain():
    return get_rag_chain()

def check_setup():
    """Return (ok, error_message)."""
    if not os.getenv("GROQ_API_KEY"):
        return False, "GROQ_API_KEY is not set. Copy .env.example to .env and add your Groq API key, or set the environment variable."
    if not os.path.isdir("vector_db"):
        return False, "vector_db/ not found. Run 'python ingest.py' once to index your documents in data/."
    return True, None

try:
    ok, err = check_setup()
    if not ok:
        st.error(err)
        st.stop()
    from rag_chain import get_rag_chain
    chain = load_chain()
except Exception as e:
    st.error(f"Failed to load RAG chain: {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about the documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chain.invoke({"query": prompt})["result"]
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
