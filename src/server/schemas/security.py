from pydantic import BaseModel

class VerifyOTP(BaseModel):
    code: str
