from typing import List, Optional, Literal
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

UserRole = Literal['entrepreneur', 'investor']

class BaseUser(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: EmailStr
    password_hash: str
    role: Literal['entrepreneur', 'investor']
    avatarUrl: str
    bio: str
    is_online: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

class EntrepreneurProfile(BaseUser):
    role: Literal['entrepreneur'] = 'entrepreneur'
    startupName: str
    pitchSummary: str
    fundingNeeded: float
    industry: str
    location: str
    foundedYear: int
    teamSize: int

class InvestorProfile(BaseUser):
    role: Literal['investor'] = 'investor'
    investmentInterests: List[str]
    investmentStage: List[str]
    portfolioCompanies: List[str]
    totalInvestments: int
    minimumInvestment: float
    maximumInvestment: float
