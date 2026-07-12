import os
import shutil
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from bson import ObjectId
from src.server.core.database import get_db
from src.server.api.v1.auth import get_current_user
from src.server.models.document import STORAGE_DIR
from src.server.schemas.document import CreateSignature

router = APIRouter()

async def verify_collaboration(db, user_id: str, document_owner_id: str):
    if user_id == document_owner_id:
        return True
    
    # Check for accepted collaboration request
    request = await db.collaboration_requests.find_one({
        "$or": [
            {"sender_id": user_id, "entrepreneurId": document_owner_id},
            {"sender_id": document_owner_id, "entrepreneurId": user_id}
        ],
        "status": "accepted"
    })
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied. You must have an accepted collaboration request to view this document."
        )
    return True

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")

    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(STORAGE_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc_entry = {
        "title": os.path.basename(file.filename),
        "file_path": file_path,
        "uploaded_by": str(current_user["_id"]),
        "version": 1,
        "status": "active",
        "signatures": [],
        "created_at": datetime.utcnow()
    }
    
    result = await db.documents.insert_one(doc_entry)
    doc_entry["_id"] = str(result.inserted_id)
    return doc_entry

@router.get("/view/{document_id}")
async def view_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    doc = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    await verify_collaboration(db, str(current_user["_id"]), doc["uploaded_by"])
    
    return FileResponse(doc["file_path"])

@router.post("/{document_id}/sign")
async def sign_document(
    document_id: str,
    signature_data: CreateSignature,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    doc = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    await verify_collaboration(db, str(current_user["_id"]), doc["uploaded_by"])
    
    new_signature = {
        "user_id": str(current_user["_id"]),
        "signature_data": signature_data.signature_base64,
        "signed_at": datetime.utcnow()
    }
    
    await db.documents.update_one(
        {"_id": ObjectId(document_id)},
        {"$push": {"signatures": new_signature}}
    )
    
    return {"message": "Signature appended successfully"}
