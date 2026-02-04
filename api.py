"""
RAG AI Chat App - REST API.
Run: uvicorn api:app --reload --host 0.0.0.0 --port 8193
Ensure vector_db/ exists (run python ingest.py first) and GROQ_API_KEY is set.
"""
import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel, Field

# Chain loaded at startup and held here; reloaded after on-demand ingest
_chain = None


def reload_rag_chain():
    """Reload the RAG chain from disk (e.g. after ingest). Updates the global _chain."""
    global _chain
    from rag_chain import get_rag_chain
    _chain = get_rag_chain()


class ChatRequest(BaseModel):
    """Request body for POST /AIAgentChat."""
    message: str = Field(..., min_length=1, description="User question text")


class ChatResponse(BaseModel):
    """Response body for POST /AIAgentChat."""
    answer: str = Field(..., description="RAG response text")


class IngestRequest(BaseModel):
    """Request body for POST /AIAgentIngest. Optional; omit or empty paths = full re-ingest."""
    paths: list[str] | None = Field(default=None, description="File paths for incremental add (e.g. data/file.pdf)")


class IngestResponse(BaseModel):
    """Response body for POST /AIAgentIngest."""
    message: str = Field(..., description="Status message")
    chunks: int | None = Field(default=None, description="Total chunks after full ingest")
    chunks_added: int | None = Field(default=None, description="Chunks added in incremental ingest")


def check_setup():
    """Return (ok, error_message)."""
    if not os.getenv("GROQ_API_KEY"):
        return False, "GROQ_API_KEY is not set. Copy .env.example to .env and add your Groq API key, or set the environment variable."
    if not os.path.isdir("vector_db"):
        return False, "vector_db/ not found. Run 'python ingest.py' once to index your documents in data/."
    return True, None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load RAG chain once at startup."""
    global _chain
    try:
        ok, _ = check_setup()
        if ok:
            from rag_chain import get_rag_chain
            _chain = get_rag_chain()
    except Exception:
        _chain = None
    yield
    _chain = None


app = FastAPI(
    title="RAG AI Chat API",
    description="REST API for RAG-based question answering over indexed documents.",
    lifespan=lifespan,
)


@app.get("/AIAgentHealth")
async def ai_agent_health():
    """Liveness/readiness: 200 when server and RAG setup are OK, 503 otherwise."""
    ok, error_message = check_setup()
    if not ok:
        raise HTTPException(status_code=503, detail=error_message)
    if _chain is None:
        raise HTTPException(
            status_code=503,
            detail="RAG chain failed to load at startup. Check logs and configuration.",
        )
    return {"status": "ok"}


@app.post("/AIAgentChat", response_model=ChatResponse)
async def ai_agent_chat(body: ChatRequest):
    """Send one message, get one RAG answer."""
    message = body.message.strip()
    if not message:
        raise HTTPException(
            status_code=400,
            detail="'message' cannot be blank.",
        )

    if _chain is None:
        ok, error_message = check_setup()
        raise HTTPException(
            status_code=503,
            detail=error_message or "RAG chain not available. Run 'python ingest.py' and ensure GROQ_API_KEY is set.",
        )

    try:
        result = _chain.invoke({"query": message})["result"]
        return ChatResponse(answer=result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}",
        )


@app.post("/AIAgentIngest", response_model=IngestResponse)
async def ai_agent_ingest(body: IngestRequest | None = Body(None)):
    """
    Run ingestion without restarting the server. Full re-ingest or incremental add.
    Omit body or pass empty paths for full re-ingest from data/. Pass paths for incremental add.
    On success, the RAG chain is reloaded so new documents are used immediately.
    """
    paths = body.paths if body else None
    full = not paths

    def do_ingest():
        from ingest import run_ingest
        return run_ingest(full=full, paths=paths)

    try:
        result = await asyncio.to_thread(do_ingest)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}",
        )

    reload_rag_chain()

    return IngestResponse(
        message=result["message"],
        chunks=result.get("chunks"),
        chunks_added=result.get("chunks_added"),
    )
