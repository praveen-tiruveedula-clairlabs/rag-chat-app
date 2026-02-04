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


def load_documents():
    """Load all supported documents from DATA_DIR."""
    if not os.path.isdir(DATA_DIR):
        print(f"Error: {DATA_DIR} does not exist. Create it and add .html, .pdf, or .json files.")
        return []

    supported = (".pdf", ".html", ".json")
    files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(supported)]
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


def ingest():
    """Load documents, split, embed, and save to FAISS."""
    documents = load_documents()
    if not documents:
        print("No documents loaded. Exiting.")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTOR_DB_PATH)
    print("Ingestion complete!")


if __name__ == "__main__":
    ingest()
