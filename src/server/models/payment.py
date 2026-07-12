from typing import Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Transaction(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    recipient_id: Optional[str] = None
    amount: float
    currency: str = 'USD'
    transaction_type: Literal['deposit', 'withdraw', 'transfer']
    status: Literal['Pending', 'Completed', 'Failed']
    reference_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
