from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import sys

# Add parent directory to path for importing services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.document_loader import DocumentLoader
from services.text_splitter import TextSplitter
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), api_key: str = None):
    """
    Upload and process a document.
    
    This endpoint performs the complete RAG pipeline:
    1. Load document
    2. Split into chunks
    3. Embed chunks
    4. Store in ChromaDB
    """
    try:
        # Read file content
        content = await file.read()
        filename = file.filename
        
        # Get customer ID from API key (or use default)
        customer_id = api_key or "default"
        
        # Step 1: Load document
        # Create temporary file for DocumentLoader
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            documents = DocumentLoader.load_document(temp_file_path)
            
            # Step 2: Split into chunks
            chunks = TextSplitter.split_documents(documents)
            
            # Step 3: Embed chunks
            texts = [chunk.page_content for chunk in chunks]
            embeddings = EmbeddingService.embed_documents(texts)
            
            # Step 4: Store in ChromaDB
            count = VectorStore.add_documents(customer_id, chunks)
            
            return {
                "message": "Document processed and stored successfully",
                "filename": filename,
                "customer_id": customer_id,
                "chunks_created": len(chunks),
                "chunks_stored": count,
                "file_size": len(content),
                "processing_time": "completed"
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.post("/upload-multiple")
async def upload_multiple_documents(files: List[UploadFile] = File(...), api_key: str = None):
    """
    Upload and process multiple documents.
    
    This endpoint performs the complete RAG pipeline for multiple files:
    1. Load documents
    2. Split into chunks
    3. Embed chunks
    4. Store in ChromaDB
    """
    try:
        # Get customer ID from API key (or use default)
        customer_id = api_key or "default"
        
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
                total_chunks += len(chunks)
                
                # Step 3: Embed chunks
                texts = [chunk.page_content for chunk in chunks]
                embeddings = EmbeddingService.embed_documents(texts)
                
                # Step 4: Store in ChromaDB
                count = VectorStore.add_documents(customer_id, chunks)
                total_stored += count
                
                results.append({
                    "filename": filename,
                    "status": "processed",
                    "chunks_created": len(chunks),
                    "chunks_stored": count,
                    "file_size": len(content)
                })
            
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        
        return {
            "message": "Documents processed and stored successfully",
            "customer_id": customer_id,
            "total_files": len(files),
            "total_chunks_created": total_chunks,
            "total_chunks_stored": total_stored,
            "files": results
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

@router.delete("/clear")
async def clear_documents(api_key: str = None):
    """
    Clear all documents for a customer.
    
    Deletes the entire vector collection for a customer.
    """
    try:
        customer_id = api_key or "default"
        
        VectorStore.delete_collection(customer_id)
        
        return {
            "message": "Documents cleared successfully",
            "customer_id": customer_id
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")

@router.get("/stats")
async def get_document_stats(api_key: str = None):
    """
    Get statistics about documents in the vector store.
    
    Returns information about the number of chunks stored.
    """
    try:
        customer_id = api_key or "default"
        
        from collections import Counter
        import chromadb
        from config import settings
        
        client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
        collection_name = VectorStore.get_collection_name(customer_id)
        
        try:
            collection = client.get_collection(name=collection_name)
            
            if collection:
                count = collection.count()
                
                # Get chunk size distribution
                # Note: This is a simplified approach
                return {
                    "message": "Document statistics retrieved",
                    "customer_id": customer_id,
                    "collection_name": collection_name,
                    "total_chunks": count,
                    "chunk_size_setting": settings.CHUNK_SIZE,
                    "chunk_overlap_setting": settings.CHUNK_OVERLAP
                }
            else:
                return {
                    "message": "No documents found for this customer",
                    "customer_id": customer_id,
                    "collection_name": collection_name,
                    "total_chunks": 0
                }
        except Exception:
            return {
                "message": "Error retrieving statistics",
                "customer_id": customer_id,
                "error": "Collection not accessible"
            }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

@router.post("/upload-multiple")
async def upload_multiple_documents(files: List[UploadFile] = File(...)):
    try:
        results = []
        for file in files:
            content = await file.read()
            results.append({
                "filename": file.filename,
                "size": len(content),
                "content_type": file.content_type
            })
        
        return {
            "message": "Files uploaded successfully",
            "count": len(files),
            "files": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
