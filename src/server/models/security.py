from pydantic import BaseModel, Field
from datetime import datetime

class OTPRecord(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    otp_code: str
    expires_at: datetime
    is_used: bool = False

    class Config:
        populate_by_name = True
