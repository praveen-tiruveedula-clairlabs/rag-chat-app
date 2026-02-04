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
   Open the URL shown (e.g. http://localhost:8501) and ask questions about your documents. Use **Reload index** in the sidebar after you trigger ingestion (e.g. via the API or after running `python ingest.py`) so the Streamlit app uses the updated index without restarting.

## REST API

The app can be run as a REST API so other applications (e.g. a chat UI) can send messages and receive RAG answers.

**Start the API server:**
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8193
```

- **OpenAPI docs:** http://localhost:8193/docs
- **Endpoints:**
  - `GET /AIAgentHealth` — Liveness/readiness; returns 200 when server and RAG setup are OK.
  - `POST /AIAgentChat` — Send one message, get one RAG answer.
  - `POST /AIAgentIngest` — On-demand ingestion; no server restart needed.

**On-demand ingestion (POST /AIAgentIngest):**
- Omit the body or send `{}` for **full re-ingest** (all files in `data/`). The RAG chain is reloaded after ingest.
- Send `{ "paths": ["data/file.pdf", "data/other.html"] }` for **incremental add**: only those files are loaded and added to the existing index. Paths must be under the project root and use `.pdf`, `.html`, or `.json`.
- Example (full): `curl -X POST http://localhost:8193/AIAgentIngest -H "Content-Type: application/json" -d "{}"`
- Example (incremental): `curl -X POST http://localhost:8193/AIAgentIngest -H "Content-Type: application/json" -d "{\"paths\": [\"data/new.pdf\"]}"`

**Example (chat):**
```bash
curl -X POST http://localhost:8193/AIAgentChat -H "Content-Type: application/json" -d "{\"message\": \"What is this document about?\"}"
```
Response: `{ "answer": "..." }`.

Ensure `.env` has `GROQ_API_KEY` and run `python ingest.py` before starting the API so `vector_db/` exists.

## Project layout

- `ingest.py` – Loads documents from `data/`, chunks, embeds, and saves to FAISS.
- `rag_chain.py` – Loads FAISS and builds the Groq RAG chain.
- `app.py` – Streamlit chat UI.
- `api.py` – REST API (FastAPI); endpoints `AIAgentHealth`, `AIAgentChat`, `AIAgentIngest` (on-demand ingestion).
- `data/` – Place your HTML, PDF, and JSON files here.
- `vector_db/` – Created by `ingest.py`; do not edit manually.

## Reference

See [running_notes/rag-chat-app-discussion.md](running_notes/rag-chat-app-discussion.md) for the full discussion and design notes.
