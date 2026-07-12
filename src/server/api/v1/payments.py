import asyncio
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from src.server.core.database import get_db
from src.server.api.v1.auth import get_current_user, require_role
from src.server.schemas.payment import PaymentAction, TransferAction

router = APIRouter()

async def create_transaction_record(db, transaction_data: dict):
    # Simulate network latency
    await asyncio.sleep(1.5)
    result = await db.transactions.insert_one(transaction_data)
    transaction_data["_id"] = str(result.inserted_id)
    return transaction_data

@router.post("/deposit")
async def deposit(
    action: PaymentAction,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    txn = {
        "user_id": str(current_user["_id"]),
        "amount": action.amount,
        "transaction_type": "deposit",
        "status": "Completed",
        "reference_id": f"txn_{uuid.uuid4()}",
        "created_at": datetime.utcnow()
    }
    return await create_transaction_record(db, txn)

@router.post("/withdraw")
async def withdraw(
    action: PaymentAction,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    txn = {
        "user_id": str(current_user["_id"]),
        "amount": action.amount,
        "transaction_type": "withdraw",
        "status": "Completed",
        "reference_id": f"txn_{uuid.uuid4()}",
        "created_at": datetime.utcnow()
    }
    return await create_transaction_record(db, txn)

@router.post("/transfer")
async def transfer(
    action: TransferAction,
    current_user: dict = Depends(require_role(["investor"])),
    db = Depends(get_db)
):
    recipient = await db.users.find_one({"_id": ObjectId(action.recipient_id), "role": "entrepreneur"})
    if not recipient:
        raise HTTPException(status_code=404, detail="Entrepreneur recipient not found")

    # Mock fault for specific amount
    status_val = "Failed" if action.amount == 999.0 else "Completed"
    
    txn = {
        "user_id": str(current_user["_id"]),
        "recipient_id": action.recipient_id,
        "amount": action.amount,
        "transaction_type": "transfer",
        "status": status_val,
        "reference_id": f"txn_{uuid.uuid4()}",
        "created_at": datetime.utcnow()
    }
    return await create_transaction_record(db, txn)

@router.get("/history")
async def get_history(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    user_id = str(current_user["_id"])
    cursor = db.transactions.find(
        {"$or": [{"user_id": user_id}, {"recipient_id": user_id}]}
    ).sort("created_at", -1)
    
    txns = await cursor.to_list(length=100)
    for t in txns:
        t["_id"] = str(t["_id"])
    return txns
