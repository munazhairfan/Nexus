from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime

class CollaborationRequest(BaseModel):
    id: str = Field(alias="_id")
    sender_id: str
    receiver_id: str
    status: Literal['pending', 'accepted', 'rejected']
    pitch_message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
