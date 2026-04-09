"""
main.py — FastAPI Application

This is your web server. It:
  1. Starts up and loads the RAG query engine into memory
  2. Exposes HTTP endpoints that React can call
  3. Routes each request to the right handler function
  4. Returns JSON responses

To run:
  uvicorn backend.main:app --reload --port 8000

Then visit http://localhost:8000/docs to test all endpoints.
"""

import os
import uuid
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import (
    get_all_programs,
    get_program_by_id,
    save_chat_history,
    get_chat_stats
)
from rag.query import load_query_engine, ask

load_dotenv()

# -------------------------------------------------------
# Global query engine — loaded once at startup
# -------------------------------------------------------
query_engine = None


# -------------------------------------------------------
# Startup / shutdown lifecycle
# -------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global query_engine

    print("=" * 50)
    print("USDA RD Chatbot API — Starting up...")
    print("=" * 50)

    faiss_index_path = "./faiss_index"

    if not os.path.exists(faiss_index_path):
        print("ERROR: FAISS index not found!")
        print("Please run: python backend/rag/ingest.py")
    else:
        print("Loading RAG query engine...")
        try:
            query_engine = load_query_engine()
            print("RAG engine loaded successfully!")
        except Exception as e:
            print(f"Failed to load RAG engine: {e}")
            print("Make sure Ollama is running: ollama serve")

    print("Server ready! Visit http://localhost:8000/docs")
    print("=" * 50)

    yield

    print("Server shutting down...")


# -------------------------------------------------------
# FastAPI app
# -------------------------------------------------------
app = FastAPI(
    title="USDA Rural Development Chatbot API",
    description=(
        "AI-powered chatbot for USDA Rural Development programs. "
        "Powered by Mistral + LlamaIndex + FAISS."
    ),
    version="1.0.0",
    lifespan=lifespan
)


# -------------------------------------------------------
# CORS — allows React (localhost:5173) to call this API
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# Pydantic models — request and response shapes
# -------------------------------------------------------
class ChatRequest(BaseModel):
    message:    str
    session_id: str = ""

    class Config:
        json_schema_extra = {
            "example": {
                "message": "My rural community water system was damaged in a flood. What USDA programs can help?",
                "session_id": ""
            }
        }


class SourceProgram(BaseModel):
    program_name:    str
    category:        str
    source_url:      str
    contact:         str
    relevance_score: float | None = None


class ChatResponse(BaseModel):
    answer:     str
    sources:    list[SourceProgram]
    session_id: str
    off_topic:  bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Your community may be eligible for the Emergency Community Water Assistance Grant...",
                "sources": [{
                    "program_name":    "Emergency Community Water Assistance Grants",
                    "category":        "Water & Environmental",
                    "source_url":      "https://www.rd.usda.gov/...",
                    "contact":         "Contact your local USDA RD office",
                    "relevance_score": 0.92
                }],
                "session_id": "abc-123",
                "off_topic":  False
            }
        }


# -------------------------------------------------------
# Endpoints
# -------------------------------------------------------

@app.get("/health")
async def health_check():
    """
    Health check — returns server and RAG engine status.
    React calls this on load to verify the backend is alive.
    """
    return {
        "status":            "ok",
        "rag_engine_loaded": query_engine is not None,
        "message":           "USDA RD Chatbot API is running"
    }


@app.get("/api/programs")
async def get_programs():
    """
    Returns all 73 USDA programs from PostgreSQL.
    Used by the React sidebar to show the program browser.
    """
    try:
        programs = get_all_programs()
        return {
            "programs": programs,
            "total":    len(programs)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch programs: {str(e)}"
        )


@app.get("/api/programs/{program_id}")
async def get_program(program_id: int):
    """
    Returns a single program by its database ID.
    """
    try:
        program = get_program_by_id(program_id)
        if not program:
            raise HTTPException(
                status_code=404,
                detail=f"Program with ID {program_id} not found"
            )
        return program
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main endpoint — takes a user question and returns an AI answer.

    Pipeline:
      1. Validate the request (Pydantic)
      2. Check RAG engine is loaded
      3. Generate or use the session ID
      4. Run question through relevance filter (keyword check)
      5. Search FAISS for relevant programs
      6. Check similarity scores (off-topic detection)
      7. Generate answer with Mistral (if on-topic)
      8. Save conversation to PostgreSQL
      9. Return answer + source programs to React
    """

    if query_engine is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "RAG engine is not loaded. "
                "Make sure Ollama is running and FAISS index exists. "
                "Run: python backend/rag/ingest.py"
            )
        )

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    session_id = request.session_id or str(uuid.uuid4())

    try:
        result = ask(query_engine, request.message)

        programs_cited = [
            src["program_name"]
            for src in result["sources"]
        ]

        # Save to chat history (do not crash if DB write fails)
        try:
            save_chat_history(
                session_id=session_id,
                user_message=request.message,
                bot_response=result["answer"],
                programs_cited=programs_cited
            )
        except Exception as db_error:
            print(f"Warning: Could not save chat history: {db_error}")

        return ChatResponse(
            answer=result["answer"],
            sources=[SourceProgram(**src) for src in result["sources"]],
            session_id=session_id,
            off_topic=result.get("off_topic", False)
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your question: {str(e)}"
        )


@app.get("/api/stats")
async def get_stats():
    """
    Returns usage statistics — total conversations, sessions, programs.
    """
    try:
        return get_chat_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/categories")
async def get_categories():
    """
    Returns all unique program categories.
    React uses this to populate the sidebar filter buttons.
    """
    try:
        programs = get_all_programs()
        categories = sorted(list(set(
            p["category"] for p in programs if p.get("category")
        )))
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))