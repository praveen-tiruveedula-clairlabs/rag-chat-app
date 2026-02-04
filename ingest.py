"""
Ingest HTML, PDF, and JSON documents from data/ into a FAISS vector store.
Run once (or when data/ changes): python ingest.py
"""
import os
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredHTMLLoader,
    JSONLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_DIR = "data/"
VECTOR_DB_PATH = "vector_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SUPPORTED_EXTENSIONS = (".pdf", ".html", ".json")


def _get_allowed_root():
    """Return the allowed root directory for path validation (project root)."""
    return os.path.abspath(os.getcwd())


def _is_path_allowed(filepath: str) -> bool:
    """Return True if path is under project root and has a supported extension."""
    root = _get_allowed_root()
    abs_path = os.path.abspath(filepath)
    if not abs_path.startswith(root):
        return False
    return any(abs_path.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS)


def _load_one_document(filepath: str):
    """Load a single document by path; return list of LangChain Documents."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    if not _is_path_allowed(filepath):
        raise ValueError(
            f"Path not allowed (must be under project root and end with .pdf, .html, or .json): {filepath}"
        )
    filename = os.path.basename(filepath)
    if filename.lower().endswith(".pdf"):
        loader = PyPDFLoader(file_path=filepath)
    elif filename.lower().endswith(".html"):
        loader = UnstructuredHTMLLoader(file_path=filepath)
    elif filename.lower().endswith(".json"):
        loader = JSONLoader(
            file_path=filepath,
            jq_schema=".",
            text_content=False,
        )
    else:
        raise ValueError(f"Unsupported extension: {filepath}")
    return loader.load()


def load_documents_from_paths(paths: list[str]):
    """Load documents from a list of file paths. Paths must be under project root; only .pdf, .html, .json."""
    documents = []
    for path in paths:
        try:
            docs = _load_one_document(path)
            documents.extend(docs)
        except Exception as e:
            raise ValueError(f"Failed to load {path}: {e}") from e
    return documents


def load_documents():
    """Load all supported documents from DATA_DIR."""
    if not os.path.isdir(DATA_DIR):
        print(f"Error: {DATA_DIR} does not exist. Create it and add .html, .pdf, or .json files.")
        return []

    files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    if not files:
        print(f"Error: No .html, .pdf, or .json files found in {DATA_DIR}. Add at least one document.")
        return []

    documents = []
    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        try:
            if filename.lower().endswith(".pdf"):
                loader = PyPDFLoader(file_path=filepath)
            elif filename.lower().endswith(".html"):
                loader = UnstructuredHTMLLoader(file_path=filepath)
            elif filename.lower().endswith(".json"):
                loader = JSONLoader(
                    file_path=filepath,
                    jq_schema=".",
                    text_content=False,
                )
            else:
                continue
            documents.extend(loader.load())
        except Exception as e:
            print(f"Warning: Skipping {filename}: {e}")

    return documents


def _get_text_splitter():
    """Return the shared text splitter for consistent chunking."""
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )


def ingest():
    """Load documents, split, embed, and save to FAISS. Returns number of chunks or None if no docs."""
    documents = load_documents()
    if not documents:
        print("No documents loaded. Exiting.")
        return None

    text_splitter = _get_text_splitter()
    chunks = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTOR_DB_PATH)
    print("Ingestion complete!")
    return len(chunks)


def ingest_incremental(paths: list[str]):
    """Add documents from the given paths to the existing FAISS index (or create one if missing)."""
    if not paths:
        raise ValueError("paths must be a non-empty list of file paths")

    documents = load_documents_from_paths(paths)
    if not documents:
        raise ValueError("No documents loaded from the given paths")

    text_splitter = _get_text_splitter()
    chunks = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    if os.path.isdir(VECTOR_DB_PATH):
        vectorstore = FAISS.load_local(
            VECTOR_DB_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        vectorstore.add_documents(chunks)
    else:
        vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(VECTOR_DB_PATH)
    return len(chunks)


def run_ingest(full: bool = True, paths: list[str] | None = None) -> dict:
    """
    Run ingestion for API use. Full re-ingest or incremental add.
    Returns {"success": True, "message": "..."}. Raises ValueError on validation/load errors.
    """
    if full or not paths:
        count = ingest()
        if count is None:
            raise ValueError("No documents found in data/. Add .html, .pdf, or .json files.")
        return {"success": True, "message": "Ingestion complete.", "chunks": count}
    count = ingest_incremental(paths)
    return {"success": True, "message": "Incremental ingestion complete.", "chunks_added": count}


if __name__ == "__main__":
    ingest()
