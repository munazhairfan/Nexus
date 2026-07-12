from pydantic import BaseModel

class CreateSignature(BaseModel):
    signature_base64: str
