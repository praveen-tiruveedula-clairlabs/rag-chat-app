# RAG AI Chat App

A simple Retrieval-Augmented Generation (RAG) chat application that indexes HTML, PDF, and JSON documents and answers questions using Groq (Llama) and a local FAISS vector store.

## Prerequisites

- **Python 3.9+** (3.10 or 3.12 recommended)
- **Groq API key** (free tier at [groq.com](https://console.groq.com/))
- **Windows:** If you see a torch DLL error when running ingest or the app, install [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe).

## Setup

1. **Clone or open the project** and go to the project root.

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   ```
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare documents:** Put your `.html`, `.pdf`, or `.json` files in the `data/` folder. Sample files are included.

5. **Set your Groq API key:**
   - Copy `.env.example` to `.env`
   - Edit `.env` and set `GROQ_API_KEY=your_key_here`
   - Or set the environment variable: `set GROQ_API_KEY=your_key` (Windows) / `export GROQ_API_KEY=your_key` (macOS/Linux)

6. **Index documents (run once, or when you add/change files in data/):**
   ```bash
   python ingest.py
   ```
   This creates the `vector_db/` folder.

7. **Run the chat app:**
   ```bash
   streamlit run app.py
   ```
   Open the URL shown (e.g. http://localhost:8501) and ask questions about your documents.

## Project layout

- `ingest.py` – Loads documents from `data/`, chunks, embeds, and saves to FAISS.
- `rag_chain.py` – Loads FAISS and builds the Groq RAG chain.
- `app.py` – Streamlit chat UI.
- `data/` – Place your HTML, PDF, and JSON files here.
- `vector_db/` – Created by `ingest.py`; do not edit manually.

## Reference

See [running_notes/rag-chat-app-discussion.md](running_notes/rag-chat-app-discussion.md) for the full discussion and design notes.
