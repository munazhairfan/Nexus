from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime
from src.server.core.database import get_db
from src.server.api.v1.auth import get_current_user, require_role
from src.server.schemas.collaboration import CreateCollaborationRequest, UpdateRequestStatus

router = APIRouter()

@router.post("/request")
async def send_collaboration_request(
    request_data: CreateCollaborationRequest,
    current_user: dict = Depends(require_role(["investor"])),
    db = Depends(get_db)
):
    # Verify receiver exists and is an entrepreneur
    receiver = await db.users.find_one({"_id": ObjectId(request_data.receiver_id), "role": "entrepreneur"})
    if not receiver:
        raise HTTPException(status_code=404, detail="Entrepreneur not found")
    
    # Check for existing request
    existing = await db.collaboration_requests.find_one({
        "sender_id": str(current_user["_id"]),
        "receiver_id": request_data.receiver_id,
        "status": {"$in": ["pending", "accepted"]}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Connection request already exists or is active")
    
    new_request = {
        "sender_id": str(current_user["_id"]),
        "receiver_id": request_data.receiver_id,
        "status": "pending",
        "pitch_message": request_data.pitch_message,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.collaboration_requests.insert_one(new_request)
    new_request["_id"] = str(result.inserted_id)
    return new_request

@router.patch("/request/{request_id}/status")
async def update_request_status(
    request_id: str,
    status_data: UpdateRequestStatus,
    current_user: dict = Depends(require_role(["entrepreneur"])),
    db = Depends(get_db)
):
    req = await db.collaboration_requests.find_one({"_id": ObjectId(request_id)})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if req["receiver_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to modify this request")
    
    await db.collaboration_requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"status": status_data.status, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": f"Request {status_data.status} successfully"}

@router.get("/requests/incoming")
async def get_incoming_requests(
    current_user: dict = Depends(require_role(["entrepreneur"])),
    db = Depends(get_db)
):
    pipeline = [
        {"$match": {"receiver_id": str(current_user["_id"])}},
        {"$addFields": {"sender_obj_id": {"$toObjectId": "$sender_id"}}},
        {"$lookup": {
            "from": "users",
            "localField": "sender_obj_id",
            "foreignField": "_id",
            "as": "sender_profile"
        }},
        {"$unwind": "$sender_profile"}
    ]
    cursor = db.collaboration_requests.aggregate(pipeline)
    requests = await cursor.to_list(length=100)
    for r in requests:
        r["_id"] = str(r["_id"])
        r["sender_profile"]["_id"] = str(r["sender_profile"]["_id"])
    return requests

@router.get("/requests/outgoing")
async def get_outgoing_requests(
    current_user: dict = Depends(require_role(["investor"])),
    db = Depends(get_db)
):
    pipeline = [
        {"$match": {"sender_id": str(current_user["_id"])}},
        {"$addFields": {"receiver_obj_id": {"$toObjectId": "$receiver_id"}}},
        {"$lookup": {
            "from": "users",
            "localField": "receiver_obj_id",
            "foreignField": "_id",
            "as": "receiver_profile"
        }},
        {"$unwind": "$receiver_profile"}
    ]
    cursor = db.collaboration_requests.aggregate(pipeline)
    requests = await cursor.to_list(length=100)
    for r in requests:
        r["_id"] = str(r["_id"])
        r["receiver_profile"]["_id"] = str(r["receiver_profile"]["_id"])
    return requests
