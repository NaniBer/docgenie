from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.chat_service import ChatService

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    api_key: Optional[str] = None
    k: Optional[int] = None

class SourceDocument(BaseModel):
    content: str
    metadata: dict
    source: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    customer_id: str
    query_time_ms: Optional[float] = None

@router.post("/query")
async def query_chat(request: ChatRequest):
    """
    Query the chatbot and get an answer with sources.
    
    Args:
        request: ChatRequest with query and API keys
    
    Returns:
        ChatResponse with answer, sources, and metadata
    """
    import time
    import os
    from dotenv import load_dotenv
    from config import settings
    
    # Load environment variables
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path)
    
    # Validate API key if set in config
    if settings.API_KEY and request.api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Validate at least one API key is provided for LLM
    if not request.google_api_key and not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(status_code=400, detail="Google AI API key is required")
    
    # Validate at least one API key is provided for embeddings
    if not request.cohere_api_key and not os.getenv("COHERE_API_KEY"):
        raise HTTPException(status_code=400, detail="Cohere API key is required")
    
    start_time = time.time()
        
        try:
            # Use api_key as customer_id
            response = await ChatService.query(
                customer_id=request.api_key or "default",
                question=request.query,
                api_key=request.api_key,
                k=request.k
            )
        
        end_time = time.time()
        query_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return ChatResponse(
            answer=response.get("answer", ""),
            sources=[SourceDocument(**s) for s in response.get("sources", [])],
            customer_id=customer_id,
            query_time_ms=query_time
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint for chat service."""
    return {"status": "healthy", "service": "chat"}
