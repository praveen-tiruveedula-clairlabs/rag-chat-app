# Building a Simple RAG AI Chat Application

**Date of conversation**: ~ February 2026  
**User**: @SrivariVeedhi (Bengaluru, India)  
**Topic**: Creating a RAG chat app using HTML, PDF, and JSON files with Python + Cursor IDE

## Original User Question

> How can i build a simple RAG AI Chat application , the content will be html , pdf and json files .. using cursor IDE and python

## Grok's Response (Complete Guide)

### Overview
Building a simple Retrieval-Augmented Generation (RAG) AI chat application in Python is straightforward, especially using libraries like LangChain...

### Prerequisites
1. Set up in Cursor IDE:
   - Create a new Python project folder (e.g., `rag-chat-app`).
   - Create virtual environment: `python -m venv venv`
   - Activate it
   - Install dependencies:

   ```bash
   pip install langchain langchain-community langchain-groq sentence-transformers faiss-cpu streamlit pypdf unstructured jsonlines beautifulsoup4
   ```


2. Get Groq API key (free tier available at groq.com)

3. Create `data/` folder with your .html, .pdf, .json files

### 1. Ingest and Embed Documents (`ingest.py`)

```python
import os
from langchain.document_loaders import PyPDFLoader, UnstructuredHTMLLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

DATA_DIR = "data/"
VECTOR_DB_PATH = "vector_db"

def load_documents():
    documents = []
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
        elif filename.endswith(".html"):
            loader = UnstructuredHTMLLoader(filepath)
        elif filename.endswith(".json"):
            loader = JSONLoader(filepath, jq_schema=".", text_content=False)
        else:
            continue
        documents.extend(loader.load())
    return documents

def ingest():
    documents = load_documents()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTOR_DB_PATH)
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest()
```

Run once: `python ingest.py`

```python
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os

VECTOR_DB_PATH = "vector_db"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_rag_chain():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
    
    llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name="llama3-8b-8192")
    
    prompt_template = """Use the following context to answer the question. If you don't know, say so.
    Context: {context}
    Question: {question}
    Answer:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": PROMPT}
    )
    return chain
```

### 2. RAG Chain (`rag_chain.py`)

*(Code block above is the RAG chain.)*

### 3. Streamlit Chat UI (`app.py`)

```python
import streamlit as st
from rag_chain import get_rag_chain

st.title("RAG AI Chat App")

@st.cache_resource
def load_chain():
    return get_rag_chain()

chain = load_chain()

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
```

Run the app:

```bash
streamlit run app.py
```

---

## Extended Guide (Detailed Steps)

This section repeats the same content in more detail.

### Prerequisites (detailed)

- **Set up in Cursor IDE:**
  - Create a new Python project folder (e.g., `rag-chat-app`).
  - Open the folder in Cursor.
  - Create a virtual environment: Run `python -m venv venv` in the terminal, then activate it (`source venv/bin/activate` on macOS/Linux or `venv\Scripts\activate` on Windows).
  - Install dependencies: `pip install langchain langchain-community langchain-groq sentence-transformers faiss-cpu streamlit pypdf unstructured jsonlines beautifulsoup4`.
- **API Key:** Sign up at groq.com for a free API key (supports models like Llama). Set it as an environment variable: `export GROQ_API_KEY=your_key_here` (or add it in code for testing).
- **Prepare Content:** Create a `data/` folder in your project with sample files (e.g., `example.html`, `report.pdf`, `data.json`). The app will load all files from there.

### Step 1: Ingest and Embed Documents

We'll load files, split them into chunks, embed them, and store in FAISS. Create `ingest.py` in your project:

```python
import os
from langchain.document_loaders import PyPDFLoader, UnstructuredHTMLLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# Directory with your files
DATA_DIR = "data/"
VECTOR_DB_PATH = "vector_db"

def load_documents():
    documents = []
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
        elif filename.endswith(".html"):
            loader = UnstructuredHTMLLoader(filepath)
        elif filename.endswith(".json"):
            loader = JSONLoader(filepath, jq_schema=".", text_content=False)  # Adjust jq_schema if your JSON structure differs
        else:
            continue
        documents.extend(loader.load())
    return documents

def ingest():
    documents = load_documents()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTOR_DB_PATH)
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest()

Explanation:
Loaders handle file types: PyPDFLoader for PDFs, UnstructuredHTMLLoader for HTML (extracts text), JSONLoader for JSON (flattens to text).
Split into chunks to fit embedding limits.
Embed with a lightweight model.
Save to FAISS for persistence.


Run this script once:

```bash
python ingest.py
```

It creates `vector_db/` for reuse.

### Step 2: Build the RAG Chain

This retrieves relevant chunks and generates responses. Create `rag_chain.py`:

```python
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

VECTOR_DB_PATH = "vector_db"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Or hardcode for testing

def get_rag_chain():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
    
    llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name="llama3-8b-8192")
    
    prompt_template = """Use the following context to answer the question. If you don't know, say so.
    Context: {context}
    Question: {question}
    Answer:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),  # Retrieve top 3 chunks
        chain_type_kwargs={"prompt": PROMPT}
    )
    return chain
```
Explanation:
Load the vector store.
Use Groq's LLM for generation.
Custom prompt ensures the LLM uses retrieved context.
RetrievalQA chain handles retrieval + generation.


### Step 3: Create the Chat UI with Streamlit

For a simple chat interface. Create `app.py`:

```python
import streamlit as st
from rag_chain import get_rag_chain

st.title("RAG AI Chat App")

# Load the chain
@st.cache_resource
def load_chain():
    return get_rag_chain()

chain = load_chain()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask a question about the documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chain.invoke({"query": prompt})["result"]
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

Explanation:
Streamlit provides a web UI with chat input.
Caches the chain for efficiency.
Maintains conversation history.
Invokes the RAG chain on each query.


Run the app:

```bash
streamlit run app.py
```

Open in browser (localhost:8501).

### Usage and Tips

- **Ingest Data:** Run `ingest.py` whenever you add/update files in `data/`.
- **Chat:** Ask questions like "What does the PDF say about X?" or "Summarize the JSON data." The app retrieves relevant chunks from HTML/PDF/JSON and generates answers.
- **Customization in Cursor IDE:**
  - Use Cursor's AI completions (Ctrl+K) to expand code or fix bugs.
  - For better embeddings, try "BAAI/bge-large-en" (install via pip if needed).
  - Scale up: Add more file types or use a persistent DB like Pinecone.
- **Limitations:** This is local and simple—embeddings are on CPU (slow for large docs). For production, use GPU or cloud services.
- **Debugging:** If errors occur (e.g., with JSON schema), adjust loaders. Test small: Start with 1-2 files.

This should get you a working prototype in under an hour. If you hit issues, share error logs!

---

## Export Request & Response

**User:** Is it possible for you to give this entire discussion as a .md file, so that I can download it?

**Response:** Yes, I can help with that! Here's the entire discussion reformatted as clean Markdown content. You can copy-paste the text below into a new file (e.g. `rag-chat-app-discussion.md`) and save it — or if you're viewing this in a browser/interface that supports it, many platforms let you right-click → "Save as…" or copy → paste into a Markdown editor.

---

*(Below is the Markdown content that was provided for download.)*

# Building a Simple RAG AI Chat Application

**Date of conversation**: ~ February 2026  
**User**: @SrivariVeedhi (Bengaluru, India)  
**Topic**: Creating a RAG chat app using HTML, PDF, and JSON files with Python + Cursor IDE

## Original User Question

> How can i build a simple RAG AI Chat application , the content will be html , pdf and json files .. using cursor IDE and python

## Grok's Response (Complete Guide)

### Overview
Building a simple Retrieval-Augmented Generation (RAG) AI chat application in Python is straightforward, especially using libraries like LangChain...

### Prerequisites
1. Set up in Cursor IDE:
   - Create a new Python project folder (e.g., `rag-chat-app`).
   - Create virtual environment: `python -m venv venv`
   - Activate it
   - Install dependencies:

   ```bash
   pip install langchain langchain-community langchain-groq sentence-transformers faiss-cpu streamlit pypdf unstructured jsonlines beautifulsoup4
   ```

2. Get Groq API key (free tier available at groq.com)

3. Create `data/` folder with your .html, .pdf, .json files

### 1. Ingest and Embed Documents (`ingest.py`)

```python
import os
from langchain.document_loaders import PyPDFLoader, UnstructuredHTMLLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

DATA_DIR = "data/"
VECTOR_DB_PATH = "vector_db"

def load_documents():
    documents = []
    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
        elif filename.endswith(".html"):
            loader = UnstructuredHTMLLoader(filepath)
        elif filename.endswith(".json"):
            loader = JSONLoader(filepath, jq_schema=".", text_content=False)
        else:
            continue
        documents.extend(loader.load())
    return documents

def ingest():
    documents = load_documents()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTOR_DB_PATH)
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest()
```

Run once: `python ingest.py`

### 2. RAG Chain (rag_chain.py)

```python
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os

VECTOR_DB_PATH = "vector_db"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_rag_chain():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
    
    llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name="llama3-8b-8192")
    
    prompt_template = """Use the following context to answer the question. If you don't know, say so.
    Context: {context}
    Question: {question}
    Answer:"""
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": PROMPT}
    )
    return chain
```

### 3. Streamlit Chat UI (app.py)

```python
import streamlit as st
from rag_chain import get_rag_chain

st.title("RAG AI Chat App")

@st.cache_resource
def load_chain():
    return get_rag_chain()

chain = load_chain()

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
```

Run: `streamlit run app.py`

## Summary of Tips from Response

- Ingest once (or when files change)
- Uses local FAISS vector store
- Free/local embeddings (MiniLM)
- Fast LLM via Groq (Llama-3-8B)
- Supports PDF, HTML, JSON
- Easy to extend in Cursor IDE (use Ctrl+K for AI help)
- Possible improvements: better embeddings, larger chunks, conversation memory, etc.