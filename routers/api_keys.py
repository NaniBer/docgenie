from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
import secrets
from config import settings

router = APIRouter()

class GenerateAPIKeyRequest(BaseModel):
    customer_name: str

class APIKeyResponse(BaseModel):
    api_key: str
    customer_name: str
    customer_id: str
    created_at: str

class ListAPIKeysResponse(BaseModel):
    api_keys: List[dict]
    total_count: int

def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """
    Dependency to verify API key from header.
    
    Args:
        x_api_key: API key from X-API-Key header
    
    Returns:
        API key string or None
    """
    return x_api_key

@router.post("/keys/generate", response_model=APIKeyResponse)
async def generate_api_key(request: GenerateAPIKeyRequest):
    """
    Generate a new API key for a customer.
    
    This creates a unique customer ID and returns an API key.
    API key will be used as customer identifier.
    """
    # Generate unique customer ID (for demo purposes)
    # In production, use a proper ID generation system
    customer_id = f"customer_{secrets.token_hex(8)}"
    
    # Generate API key from customer ID
    api_key = f"docgenie_{customer_id}"
    
    # In production, save this mapping to database
    # For now, we return it directly
    
    from datetime import datetime
    created_at = datetime.utcnow().isoformat()
    
    return APIKeyResponse(
        api_key=api_key,
        customer_name=request.customer_name,
        customer_id=customer_id,
        created_at=created_at
    )

@router.get("/keys/list", response_model=ListAPIKeysResponse)
async def list_api_keys(x_api_key: str = Depends(verify_api_key)):
    """
    List all API keys (for admin/debugging).
    
    Requires admin API key (from config) to access.
    """
    # For security, only allow admin to list all keys
    admin_key = settings.API_KEY
    
    if not admin_key:
        raise HTTPException(
            status_code=403,
            detail="Admin API key required to list all keys"
        )
    
    # Check if the requesting API key is valid admin key
    if x_api_key != admin_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin API key"
        )
    
    # In production, this would return all keys from database
    # For now, return empty list
    return ListAPIKeysResponse(
        api_keys=[],
        total_count=0
    )

@router.delete("/keys/{api_key}")
async def delete_api_key(api_key: str, x_api_key: str = Depends(verify_api_key)):
    """
    Delete an API key (disable customer).
    
    Only the owner/admin can delete their API key.
    """
    # In production, this would delete the key from database
    # For now, just return success message
    
    admin_key = settings.API_KEY
    
    if not admin_key:
        raise HTTPException(
            status_code=403,
            detail="Admin API key required to delete keys"
        )
    
    if x_api_key != admin_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin API key"
        )
    
    # Validate that the key being deleted belongs to the customer
    # In production, check ownership before deleting
    
    return {
        "message": f"API key {api_key} deleted successfully",
        "api_key": api_key
    }

@router.get("/keys/validate/{api_key}")
async def validate_api_key(api_key: str):
    """
    Validate if an API key exists and is active.
    
    Returns customer information if key is valid.
    """
    # In production, this would check database
    # For now, assume all keys we generate are valid
    
    # Extract customer ID from API key format
    # Format: docgenie_customer_{customer_id}
    
    if api_key.startswith("docgenie_"):
        customer_id = api_key.replace("docgenie_customer_", "", 1)
    else:
        customer_id = "unknown"
    
    return {
        "valid": True,
        "customer_id": customer_id,
        "api_key": api_key
    }
