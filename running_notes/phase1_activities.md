# Phase 1 Activities — RAG Chat App

Documentation of Phase 1 scope, setup, and session activities for the RAG AI Chat App.

---

## Phase 1 Scope

Phase 1 delivered a working RAG chat application with:

- **Document ingestion:** HTML, PDF, and JSON from `data/` → chunked, embedded (HuggingFace), stored in a local FAISS vector store.
- **RAG chain:** FAISS retriever + Groq (Llama) for question answering; built in `rag_chain.py`.
- **Chat UI:** Streamlit app (`app.py`) with a simple chat interface; run once `python ingest.py`, then `streamlit run app.py`.

**Project layout (Phase 1):**

| Component    | Purpose |
|-------------|---------|
| `ingest.py` | Loads documents from `data/`, splits, embeds, saves to FAISS (`vector_db/`). |
| `rag_chain.py` | Loads FAISS, builds Groq RAG (RetrievalQA) chain. |
| `app.py` | Streamlit chat UI; uses cached RAG chain. |
| `data/` | Source documents (`.html`, `.pdf`, `.json`). |
| `vector_db/` | FAISS index; created by `ingest.py`. |

**Limitations (addressed in Phase 2):**

- No REST API; only the Streamlit UI can use the RAG chain. (REST API added separately; see [api_style_feature plan](../.cursor/plans/api_style_feature_e1524165.plan.md).)
- Ingestion is manual: run `python ingest.py` and restart the server to pick up new data. (Phase 2 adds on-demand ingestion; see [phase2_activities.md](phase2_activities.md).)

---

## First Steps on a New Clone

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   ```
   - Windows: `venv\Scripts\activate` (or `.\venv\Scripts\Activate.ps1`)
   - macOS/Linux: `source venv/bin/activate`

2. **Install dependencies:** `pip install -r requirements.txt`

3. **Set Groq API key:** Copy `.env.example` to `.env` and set `GROQ_API_KEY=your_key_here` (get a key at [console.groq.com](https://console.groq.com/)).

4. **Index documents:** `python ingest.py` (creates `vector_db/`).

5. **Run the app:** `streamlit run app.py` → open the URL (e.g. http://localhost:8501).

**Optional:** If you see a torch DLL error on Windows, install [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe).

---

## Session Activities — 04 Feb 2025

Summary of changes and fixes made during this session (from [running_notes/04FEB2025/session_activities.md](04FEB2025/session_activities.md)).

---

### 1. Groq model decommission fix

**Problem:** `streamlit run app.py` failed with:
```text
groq.BadRequestError: Error code: 400 - The model `llama3-8b-8192` has been decommissioned and is no longer supported.
```

**Change:** Updated `rag_chain.py` to use Groq’s recommended replacement model.

| Before                 | After                    |
|------------------------|--------------------------|
| `llama3-8b-8192`       | `llama-3.1-8b-instant`   |

**Reference:** [Groq deprecations](https://console.groq.com/docs/deprecations) — `llama3-8b-8192` deprecated as of 30 Aug 2025; replacement: `llama-3.1-8b-instant`.

---

### 2. LangChain deprecation (HuggingFaceEmbeddings)

**Problem:** `LangChainDeprecationWarning` for `HuggingFaceEmbeddings` from `langchain_community` (deprecated in LangChain 0.2.2, removal in 1.0).

**Changes:**
- **ingest.py:** Switched import from `langchain_community.embeddings` to `langchain_huggingface`.
- **rag_chain.py:** Same import change.
- **requirements.txt:** Added `langchain-huggingface>=0.0.0`.

**Action required after pull:** Run `pip install -U langchain-huggingface` or `pip install -r requirements.txt`.

---

### 3. HF Hub and symlinks (documentation only)

**Issues:** 
- Unauthenticated requests to Hugging Face Hub (lower rate limits, slower downloads).
- Windows symlinks warning from `huggingface_hub` cache.

**Change:** **.env.example** updated with optional variables and comments:

- `HF_TOKEN` — optional; set for higher rate limits and faster downloads. Get a token at https://huggingface.co/settings/tokens.
- `HF_HUB_DISABLE_SYMLINKS_WARNING=1` — optional; set to hide the Windows symlinks warning.

No code changes; behavior is controlled via environment (e.g. copy into `.env` and set as needed).

---

### 4. BertModel LOAD REPORT (embeddings.position_ids UNEXPECTED)

**Observation:** When loading `sentence-transformers/all-MiniLM-L6-v2`, the loader reports an UNEXPECTED key `embeddings.position_ids`.

**Conclusion:** Informational only; safe to ignore when loading from a different task/architecture. No code or config change; the model loads and runs correctly.

---

### Files modified this session

| File               | Changes                                                                 |
|--------------------|-------------------------------------------------------------------------|
| `rag_chain.py`     | `GROQ_MODEL` → `llama-3.1-8b-instant`; HuggingFaceEmbeddings import    |
| `ingest.py`        | HuggingFaceEmbeddings import → `langchain_huggingface`                  |
| `requirements.txt` | Added `langchain-huggingface>=0.0.0`                                   |
| `.env.example`     | Optional `HF_TOKEN` and `HF_HUB_DISABLE_SYMLINKS_WARNING` with comments |

---

### Manual run instructions (for reference)

1. **Activate venv:** `.\venv\Scripts\Activate.ps1` (from project root).
2. **Ensure `.env`** has `GROQ_API_KEY=...`.
3. **Install deps (if needed):** `pip install -r requirements.txt`.
4. **Ingest (if data changed):** `python ingest.py`.
5. **Run app:** `streamlit run app.py`.
6. Open the Local URL (e.g. http://localhost:8501) in the browser.

---

## Related notes

- **Design and discussion:** [running_notes/rag-chat-app-discussion.md](rag-chat-app-discussion.md)
- **Session log (04 Feb 2025):** [running_notes/04FEB2025/session_activities.md](04FEB2025/session_activities.md)
- **Phase 2 (implemented):** On-demand ingestion via POST /AIAgentIngest; Streamlit "Reload index". See [phase2_activities.md](phase2_activities.md).
