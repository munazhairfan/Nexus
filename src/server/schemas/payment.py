from pydantic import BaseModel, Field

class PaymentAction(BaseModel):
    amount: float = Field(gt=0.0)

class TransferAction(BaseModel):
    recipient_id: str
    amount: float = Field(gt=0.0)
