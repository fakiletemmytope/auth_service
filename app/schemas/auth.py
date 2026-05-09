from typing import Optional
from pydantic import BaseModel
from app.models.user import Role
from datetime import datetime



class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[Role] = None

class UserRead(BaseModel):
    id: int
    email: str
    role: Role
    is_active: bool
    date_created: datetime
    date_updated: datetime = None

class UserUpdate(BaseModel):
    is_active: bool = None
    
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    refresh_token: Optional[str] = None
    user_details: UserRead
