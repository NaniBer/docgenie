from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename
        
        return {
            "message": "File uploaded successfully",
            "filename": filename,
            "size": len(content),
            "content_type": file.content_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
