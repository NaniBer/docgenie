from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload

app = FastAPI(
    title="DocGenie API",
    description="Turnkey AI Chatbot API for document Q&A",
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

@app.get("/")
async def root():
    return {"message": "DocGenie API - Turnkey AI Chatbot Service"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
