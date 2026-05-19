from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, chat

app = FastAPI(
    title="DocGenie",
    description="Self-hosted RAG chatbot for document Q&A",
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


@app.get("/")
async def root():
    return {
        "message": "DocGenie - Self-hosted RAG Chatbot",
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /api/v1/upload",
            "upload_multiple": "POST /api/v1/upload-multiple",
            "chat": "POST /api/v1/query",
            "stats": "GET /api/v1/stats",
            "clear": "DELETE /api/v1/clear",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
