from typing import Literal
from pydantic import BaseModel, Field

class CreateCollaborationRequest(BaseModel):
    receiver_id: str
    pitch_message: str

class UpdateRequestStatus(BaseModel):
    status: Literal['accepted', 'rejected']
