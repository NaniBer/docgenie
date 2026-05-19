from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.chat_service import ChatService
import time

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    k: Optional[int] = None


class SourceDocument(BaseModel):
    content: str
    metadata: dict
    source: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    query_time_ms: Optional[float] = None


@router.post("/query")
async def query_chat(request: ChatRequest):
    start = time.time()
    try:
        response = await ChatService.query(question=request.query, k=request.k)
        return ChatResponse(
            answer=response["answer"],
            sources=[SourceDocument(**s) for s in response.get("sources", [])],
            query_time_ms=(time.time() - start) * 1000
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
