"""
API router for API key generation.
Simple free tier - users generate their own keys.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import secrets

router = APIRouter()  # No prefix, path defined in main


class GenerateKeyResponse(BaseModel):
    api_key: str
    created_at: str


@router.post("/keys/generate")
async def generate_api_key():
    """
    Generate a new API key for the user.

    Simple free tier - users generate their own keys.
    No database, just returns a random key.
    """
    from datetime import datetime

    # Generate a random API key
    # Format: docg_ + random hex
    api_key = f"docg_{secrets.token_hex(12)}"

    return GenerateKeyResponse(
        api_key=api_key,
        created_at=datetime.utcnow().isoformat()
    )
