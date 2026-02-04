# Data folder

Place documents here for the RAG chat app to index.

**Supported formats:** `.html`, `.pdf`, `.json`

- **HTML:** Use any valid HTML file; text content will be extracted.
- **PDF:** Use standard PDFs; text will be extracted per page.
- **JSON:** Use `jq_schema="."` for whole-document indexing, or a custom jq path for nested structures.

After adding or updating files, run `python ingest.py` from the project root to rebuild the vector index.
