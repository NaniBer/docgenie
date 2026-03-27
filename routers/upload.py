# API Router for document upload and management

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import os
from routers.auth import get_api_key, get_collection_name

from services.document_loader import DocumentLoader
from services.text_splitter import TextSplitter
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore

router = APIRouter()


class DocumentProcessingResponse(BaseModel):
    filename: str
    api_key: str
    chunks_created: int
    chunks_stored: int
    file_size: int
    processing_time: str


class UploadStatsResponse(BaseModel):
    api_key: str
    collection_name: str
    total_chunks: int


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    """
    Upload and process a document.

    This endpoint performs the complete RAG pipeline:
    1. Load document
    2. Split into chunks
    3. Embed chunks
    4. Store in ChromaDB with API key in metadata

    Requires valid API key via X-API-Key header.
    """
    try:
        # Read file content
        content = await file.read()
        filename = file.filename

        # Get collection name for this API key
        collection_name = get_collection_name(api_key)

        # Step 1: Load document
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Load document
            documents = DocumentLoader.load_document(temp_file_path)

            # Step 2: Split into chunks
            chunks = TextSplitter.split_documents(documents)

            # Step 3: Add API key to metadata
            for chunk in chunks:
                if chunk.metadata is None:
                    chunk.metadata = {}
                chunk.metadata["api_key"] = api_key
                chunk.metadata["source_file"] = filename

            # Step 4: Embed chunks
            texts = [chunk.page_content for chunk in chunks]
            embeddings = EmbeddingService.embed_documents(texts)

            # Step 5: Store in ChromaDB
            # Use VectorStore static method to add documents
            count = VectorStore.add_documents(api_key, chunks)

            return DocumentProcessingResponse(
                filename=filename,
                api_key=api_key,
                chunks_created=len(chunks),
                chunks_stored=count,
                file_size=len(content),
                processing_time="completed"
            )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.post("/upload-multiple")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    api_key: str = Depends(get_api_key)
):
    """
    Upload and process multiple documents.

    Requires valid API key via X-API-Key header.
    """
    try:
        results = []
        total_chunks = 0
        total_stored = 0
        import tempfile

        for file in files:
            # Read file content
            content = await file.read()
            filename = file.filename

            # Create temporary file for DocumentLoader
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            try:
                # Step 1: Load document
                documents = DocumentLoader.load_document(temp_file_path)

                # Step 2: Split into chunks
                chunks = TextSplitter.split_documents(documents)

                # Step 3: Add API key to metadata
                for chunk in chunks:
                    if chunk.metadata is None:
                        chunk.metadata = {}
                    chunk.metadata["api_key"] = api_key
                    chunk.metadata["source_file"] = filename

                # Step 4: Embed chunks
                texts = [chunk.page_content for chunk in chunks]
                embeddings = EmbeddingService.embed_documents(texts)

                # Step 5: Store in ChromaDB
                collection_name = get_collection_name(api_key)
                vector_store = VectorStore.get_collection(api_key)
                count = vector_store.add_documents(chunks)

                total_chunks += len(chunks)
                total_stored += count

                results.append({
                    "filename": filename,
                    "status": "processed",
                    "chunks_created": len(chunks),
                    "chunks_stored": count
                })

            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        return {
            "message": "Documents processed and stored successfully",
            "api_key": api_key,
            "total_files": len(files),
            "total_chunks_created": total_chunks,
            "total_chunks_stored": total_stored,
            "files": results
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")


@router.get("/stats")
async def get_document_stats(api_key: str = Depends(get_api_key)):
    """
    Get statistics about documents in the vector store.

    Requires valid API key via X-API-Key header.
    """
    try:
        collection_name = get_collection_name(api_key)

        import chromadb
        from config import settings

        client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)

        try:
            collection = client.get_collection(name=collection_name)

            if collection:
                count = collection.count()

                return UploadStatsResponse(
                    api_key=api_key,
                    collection_name=collection_name,
                    total_chunks=count
                )
            else:
                return {
                    "message": "No documents found for this API key",
                    "api_key": api_key,
                    "collection_name": collection_name,
                    "total_chunks": 0
                }
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")


@router.delete("/clear")
async def clear_documents(api_key: str = Depends(get_api_key)):
    """
    Clear all documents for an API key.

    Requires valid API key via X-API-Key header.
    """
    try:
        VectorStore.delete_collection(api_key)

        return {
            "message": "Documents cleared successfully",
            "api_key": api_key
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")
