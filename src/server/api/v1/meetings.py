from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime
from src.server.core.database import get_db
from src.server.api.v1.auth import get_current_user
from src.server.schemas.meeting import CreateMeeting, UpdateMeetingStatus

router = APIRouter()

async def check_for_conflicts(db, host_id: str, invitee_id: str, start: datetime, end: datetime, exclude_meeting_id: str = None):
    query = {
        "status": {"$in": ["pending", "accepted"]},
        "$or": [
            {"host_id": host_id}, {"invitee_id": host_id},
            {"host_id": invitee_id}, {"invitee_id": invitee_id}
        ],
        "start_time": {"$lt": end},
        "end_time": {"$gt": start}
    }
    if exclude_meeting_id:
        query["_id"] = {"$ne": ObjectId(exclude_meeting_id)}
    
    conflict = await db.meetings.find_one(query)
    if conflict:
        raise HTTPException(
            status_code=400,
            detail="Time slot conflict detected. One of the participants is already booked during this window."
        )

@router.post("/")
async def schedule_meeting(
    meeting_data: CreateMeeting,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    if meeting_data.end_time <= meeting_data.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    await check_for_conflicts(
        db, 
        str(current_user["_id"]), 
        meeting_data.invitee_id, 
        meeting_data.start_time, 
        meeting_data.end_time
    )
    
    new_meeting = {
        "title": meeting_data.title,
        "description": meeting_data.description,
        "host_id": str(current_user["_id"]),
        "invitee_id": meeting_data.invitee_id,
        "start_time": meeting_data.start_time,
        "end_time": meeting_data.end_time,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    result = await db.meetings.insert_one(new_meeting)
    new_meeting["_id"] = str(result.inserted_id)
    return new_meeting

@router.patch("/{meeting_id}/status")
async def update_meeting_status(
    meeting_id: str,
    status_data: UpdateMeetingStatus,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    meeting = await db.meetings.find_one({"_id": ObjectId(meeting_id)})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting["invitee_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Only the invitee can update meeting status")
    
    if status_data.status == "accepted":
        await check_for_conflicts(
            db,
            meeting["host_id"],
            meeting["invitee_id"],
            meeting["start_time"],
            meeting["end_time"],
            exclude_meeting_id=meeting_id
        )
    
    await db.meetings.update_one(
        {"_id": ObjectId(meeting_id)},
        {"$set": {"status": status_data.status}}
    )
    return {"message": f"Meeting status updated to {status_data.status}"}

@router.get("/my-calendar")
async def get_my_calendar(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    user_id = str(current_user["_id"])
    pipeline = [
        {"$match": {"$or": [{"host_id": user_id}, {"invitee_id": user_id}]}},
        {"$addFields": {
            "participant_id": {
                "$cond": [{"$eq": ["$host_id", user_id]}, "$invitee_id", "$host_id"]
            }
        }},
        {"$addFields": {"participant_obj_id": {"$toObjectId": "$participant_id"}}},
        {"$lookup": {
            "from": "users",
            "localField": "participant_obj_id",
            "foreignField": "_id",
            "as": "participant_profile"
        }},
        {"$unwind": "$participant_profile"}
    ]
    cursor = db.meetings.aggregate(pipeline)
    meetings = await cursor.to_list(length=100)
    for m in meetings:
        m["_id"] = str(m["_id"])
        m["participant_profile"]["_id"] = str(m["participant_profile"]["_id"])
    return meetings
