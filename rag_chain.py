"""
RAG chain: load FAISS vector store and expose a retrieval + Groq QA chain.
Set GROQ_API_KEY in environment or .env before running the app.
"""
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate

VECTOR_DB_PATH = "vector_db"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.1-8b-instant"


def get_rag_chain():
    """Build and return the RAG QA chain (FAISS + Groq)."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    llm = ChatGroq(
        temperature=0,
        groq_api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
    )
    prompt_template = """Use the following context to answer the question. If you don't know, say so.
Context: {context}
Question: {question}
Answer:"""
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"],
    )
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt},
    )
    return chain
