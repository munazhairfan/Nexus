import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from src.server.core.database import get_db
from src.server.api.v1.auth import get_current_user
from src.server.schemas.security import VerifyOTP

router = APIRouter()

@router.post("/2fa/enable")
async def enable_2fa(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"is_2fa_enabled": True}}
    )
    return {"status": "2FA enabled"}

@router.post("/2fa/generate")
async def generate_2fa(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    otp_code = "".join([str(random.randint(0, 9)) for _ in range(6)])
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    otp_record = {
        "user_id": str(current_user["_id"]),
        "otp_code": otp_code,
        "expires_at": expires_at,
        "is_used": False
    }
    await db.otp_records.insert_one(otp_record)
    
    # Mock email logging
    print(f"[SECURITY NOTICE - MOCK EMAIL SENT TO {current_user['email']}] Your Nexus 2FA Verification Code is: {otp_code}")
    
    return {"status": "OTP sent"}

@router.post("/2fa/verify")
async def verify_2fa(
    otp_data: VerifyOTP,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    otp_record = await db.otp_records.find_one({
        "user_id": str(current_user["_id"]),
        "otp_code": otp_data.code,
        "is_used": False,
        "expires_at": {"$gt": datetime.utcnow()}
    }, sort=[("expires_at", -1)])
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification OTP code."
        )
        
    await db.otp_records.update_one(
        {"_id": otp_record["_id"]},
        {"$set": {"is_used": True}}
    )
    
    return {"status": "2FA verified successfully"}
