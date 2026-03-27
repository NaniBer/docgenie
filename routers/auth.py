"""
Simple authentication middleware.
Validates API key format - no database needed.
"""
from fastapi import Depends, HTTPException, Header


async def get_api_key(
    x_api_key: str = Header(None, alias="X-API-Key")
) -> str:
    """
    Get and validate API key from header.

    Simple validation - just check key exists and has reasonable format.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Include X-API-Key header."
        )

    # Simple format validation
    if len(x_api_key) < 5:
        raise HTTPException(
            status_code=400,
            detail="API key too short (minimum 5 characters)"
        )

    return x_api_key


def get_collection_name(api_key: str) -> str:
    """
    Get ChromaDB collection name for an API key.

    Uses API key directly as collection name.
    """
    return f"customer_{api_key}"
