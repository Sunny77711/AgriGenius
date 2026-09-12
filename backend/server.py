import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from sse_starlette.sse import EventSourceResponse

from rag_pipeline import AgriGeniusRAG, RetrievedSource

app = FastAPI(title="AgriGenius API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = AgriGeniusRAG()

class ChatRequest(BaseModel):
    query: str
    language: Optional[str] = "auto"
    top_k: Optional[int] = 5
    crop: Optional[str] = None
    state: Optional[str] = None

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "collection_count": rag.collection_count(),
        "model": rag.embed_model_name,
        "llm_model": rag.llm_model_name
    }

@app.post("/api/chat")
def chat(request: ChatRequest):
    filters = []
    if request.crop:
        filters.append({"Crop": request.crop})
    if request.state:
        filters.append({"StateName": request.state})
    
    where = None
    if filters:
        if len(filters) == 1:
            where = filters[0]
        else:
            where = {"$and": filters}

    result = rag.answer_query(
        query=request.query,
        top_k=request.top_k,
        where=where,
        generate=True
    )
    
    # serialize sources
    sources = []
    for src in result["sources"]:
        sources.append({
            "rank": src.rank,
            "text": src.text,
            "similarity": src.similarity,
            "metadata": src.metadata
        })
        
    result["sources"] = sources
    return result

@app.post("/api/chat/stream")
def chat_stream(request: ChatRequest):
    filters = []
    if request.crop:
        filters.append({"Crop": request.crop})
    if request.state:
        filters.append({"StateName": request.state})
    
    where = None
    if filters:
        if len(filters) == 1:
            where = filters[0]
        else:
            where = {"$and": filters}

    def generate():
        stream_generator = rag.answer_query_stream(
            query=request.query,
            top_k=request.top_k,
            where=where
        )
        for chunk in stream_generator:
            if chunk["type"] == "metadata":
                # serialize sources
                sources = []
                for src in chunk["sources"]:
                    sources.append({
                        "rank": src.rank,
                        "text": src.text,
                        "similarity": src.similarity,
                        "metadata": src.metadata
                    })
                yield json.dumps({"type": "metadata", "sources": sources})
            elif chunk["type"] == "chunk":
                yield json.dumps({"type": "chunk", "content": chunk["content"]})
    
    return EventSourceResponse(generate())
