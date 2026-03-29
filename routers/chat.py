from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from services.chat_service import ChatService
from routers.auth import get_api_key, get_collection_name

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
    api_key: str
    query_time_ms: Optional[float] = None


@router.post("/query")
async def query_chat(
    request: ChatRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Query the chatbot and get an answer with sources.

    Requires valid API key via X-API-Key header.
    Searches ChromaDB using the API key - only returns documents
    that were uploaded with this API key.
    """
    import time

    start_time = time.time()

    try:
        # Use API key as customer_id for collection naming
        collection_name = get_collection_name(api_key)

        # Query the chat service
        response = await ChatService.query(
            customer_id=api_key,  # Use API key as collection identifier
            question=request.query,
            api_key=api_key,
            k=request.k
        )

        end_time = time.time()
        query_time = (end_time - start_time) * 1000  # Convert to milliseconds

        return ChatResponse(
            answer=response.get("answer", ""),
            sources=[SourceDocument(**s) for s in response.get("sources", [])],
            api_key=api_key,
            query_time_ms=query_time
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for chat service."""
    return {"status": "healthy", "service": "chat"}
