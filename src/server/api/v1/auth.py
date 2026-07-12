from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from src.server.core.database import get_db
from src.server.core.security import get_password_hash, verify_password, create_access_token, verify_access_token
from src.server.schemas.auth import UserRegister, UserLogin, Token
from src.server.models.user import BaseUser, EntrepreneurProfile, InvestorProfile, UserRole
from src.server.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    payload = verify_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def require_role(allowed_roles: list[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not authorized")
        return current_user
    return role_checker

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db = Depends(get_db)):
    if await db.users.find_one({"email": user_data.email}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.model_dump(exclude={"password"})
    user_dict["password_hash"] = hashed_password
    user_dict["_id"] = ObjectId()
    
    await db.users.insert_one(user_dict)
    
    token = create_access_token(data={"sub": str(user_dict["_id"]), "role": user_dict["role"]})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db = Depends(get_db)):
    user = await db.users.find_one({"email": user_data.email, "role": user_data.role})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"is_online": True}})
    
    token = create_access_token(data={"sub": str(user["_id"]), "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    user_response = current_user.copy()
    user_response["id"] = str(user_response.pop("_id"))
    user_response.pop("password_hash", None)
    return user_response

@router.get("/users")
async def get_users(role: UserRole, db = Depends(get_db)):
    users = await db.users.find({"role": role}).to_list(length=100)
    user_list = []
    for u in users:
        u["id"] = str(u.pop("_id"))
        u.pop("password_hash", None)
        user_list.append(u)
    return user_list
