from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import os
import tempfile

from services.document_loader import DocumentLoader
from services.text_splitter import TextSplitter
from services.vector_store import VectorStore
from config import settings

router = APIRouter()


class ProcessingResponse(BaseModel):
    filename: str
    chunks_created: int
    chunks_stored: int
    file_size: int


class StatsResponse(BaseModel):
    total_chunks: int


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename

    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=os.path.splitext(filename)[1]) as f:
        f.write(content)
        path = f.name

    try:
        documents = DocumentLoader.load_document(path)
        chunks = TextSplitter.split_documents(documents)
        for chunk in chunks:
            chunk.metadata["source_file"] = filename
        count = VectorStore.add_documents(chunks)
        return ProcessingResponse(filename=filename, chunks_created=len(chunks), chunks_stored=count, file_size=len(content))
    finally:
        if os.path.exists(path):
            os.remove(path)


@router.post("/upload-multiple")
async def upload_multiple_documents(files: List[UploadFile] = File(...)):
    results = []
    total_chunks = 0
    total_stored = 0

    for file in files:
        content = await file.read()
        filename = file.filename

        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=os.path.splitext(filename)[1]) as f:
            f.write(content)
            path = f.name

        try:
            documents = DocumentLoader.load_document(path)
            chunks = TextSplitter.split_documents(documents)
            for chunk in chunks:
                chunk.metadata["source_file"] = filename
            count = VectorStore.add_documents(chunks)
            total_chunks += len(chunks)
            total_stored += count
            results.append({"filename": filename, "chunks_created": len(chunks), "chunks_stored": count})
        finally:
            if os.path.exists(path):
                os.remove(path)

    return {"message": "Documents processed", "total_files": len(files), "total_chunks_created": total_chunks, "total_chunks_stored": total_stored, "files": results}


@router.get("/stats")
async def get_document_stats():
    import chromadb
    client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
    try:
        collection = client.get_collection(name=settings.COLLECTION_NAME)
        return StatsResponse(total_chunks=collection.count())
    except Exception:
        return StatsResponse(total_chunks=0)


@router.delete("/clear")
async def clear_documents():
    VectorStore.delete_collection()
    return {"message": "Documents cleared"}
