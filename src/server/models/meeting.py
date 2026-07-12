from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime

class Meeting(BaseModel):
    id: str = Field(alias="_id")
    title: str
    description: str | None = None
    host_id: str
    invitee_id: str
    start_time: datetime
    end_time: datetime
    status: Literal['pending', 'accepted', 'rejected', 'cancelled']
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
