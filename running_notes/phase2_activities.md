# Phase 2 Activities — On-Demand Ingestion

Phase 2 adds on-demand ingestion so documents can be (re)indexed without restarting the server.

## Phase 2 Scope (implemented)

- **POST /AIAgentIngest** — Trigger full re-ingest (omit body or empty `paths`) or incremental add (pass `paths: ["data/file.pdf", ...]`). The API reloads the RAG chain after ingest so new documents are used immediately.
- **ingest.py** — `load_documents_from_paths(paths)`, `ingest_incremental(paths)`, and `run_ingest(full, paths)` for API use. Paths must be under project root; only `.pdf`, `.html`, `.json`.
- **Streamlit** — "Reload index" button in the sidebar clears the RAG chain cache and reruns so the app uses the updated index after ingestion (via API or `python ingest.py`).

## Reference

- **README:** [README.md](../README.md) — setup, REST API, on-demand ingestion examples.
- **Phase 1:** [phase1_activities.md](phase1_activities.md).
