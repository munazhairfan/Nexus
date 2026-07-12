from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime

class CreateMeeting(BaseModel):
    title: str
    description: str | None = None
    invitee_id: str
    start_time: datetime
    end_time: datetime

class UpdateMeetingStatus(BaseModel):
    status: Literal['accepted', 'rejected', 'cancelled']
