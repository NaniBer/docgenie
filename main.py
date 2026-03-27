from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, chat, api_keys

app = FastAPI(
    title="DocGenie API",
    description="Turnkey AI Chatbot API for document Q&A - Free Tier",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(api_keys.router, prefix="/api/v1", tags=["api_keys"])

@app.get("/")
async def root():
    return {
        "message": "DocGenie API - Free Tier AI Chatbot Service",
        "docs": "/docs",
        "endpoints": {
            "generate_key": "POST /api/v1/keys/generate",
            "upload": "POST /api/v1/documents/upload",
            "chat": "POST /api/v1/chat/query",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
