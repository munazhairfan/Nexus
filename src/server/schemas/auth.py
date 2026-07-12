from typing import List, Optional, Literal
from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal['entrepreneur', 'investor']
    # Profile extensions
    startupName: Optional[str] = None
    pitchSummary: Optional[str] = None
    fundingNeeded: Optional[float] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    foundedYear: Optional[int] = None
    teamSize: Optional[int] = None
    investmentInterests: Optional[List[str]] = None
    investmentStage: Optional[List[str]] = None
    portfolioCompanies: Optional[List[str]] = None
    totalInvestments: Optional[int] = None
    minimumInvestment: Optional[float] = None
    maximumInvestment: Optional[float] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: Literal['entrepreneur', 'investor']

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
