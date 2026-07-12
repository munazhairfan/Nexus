import os
from typing import List, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# Initialize storage directory
STORAGE_DIR = "src/server/storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

class Signature(BaseModel):
    user_id: str
    signature_data: str
    signed_at: datetime

class Document(BaseModel):
    id: str = Field(alias="_id")
    title: str
    file_path: str
    uploaded_by: str
    version: int = 1
    status: Literal['active', 'archived'] = 'active'
    signatures: List[Signature] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
