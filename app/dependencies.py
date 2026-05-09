from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import Depends
from passlib.context import CryptContext
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.schemas.auth import UserRead
from app.database import get_session
from sqlmodel import Session, select
import jwt
from app.redis_client import r
from app.config import SECRET_KEY, ALGORITHM
from enum import Enum
from typing import Any



pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class TOKEN_TYPE(Enum):
    REFRESH = "refresh"
    ACCESS = "access"



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_token(payload: dict[str, Any], token_type: TOKEN_TYPE = TOKEN_TYPE.ACCESS) -> str:
    to_encode = payload.copy()
    if token_type == TOKEN_TYPE.ACCESS:
        to_encode["exp"] = datetime.now(tz=timezone.utc) + timedelta(minutes=30)
        to_encode["type"] = "access"
    else:
        to_encode["exp"] = datetime.now(tz=timezone.utc) + timedelta(days=7)
        to_encode["type"] = "refresh"

    token = jwt.encode(
        payload=to_encode,
        key=SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return token

def verify_token(token: str):
    try:
        decoded = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=ALGORITHM)
        jti = decoded["jti"]
        if r.exists(f"blacklist_{jti}"):
            raise HTTPException(detail="Token expired", status_code=400)
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(detail="Token expired", status_code=400)
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)

async def blacklist_token(token: str = Depends(oauth2_scheme)):
    decoded = verify_token(token)
    jti = decoded["jti"]
    exp = decoded["exp"]
    now = datetime.now(tz=timezone.utc).timestamp()
    ttl = int(exp - now)
    r.setex(
        name=f"blacklist_{jti}",
        time=ttl,
        value="blacklisted"
    )
    
    return None

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> UserRead:
    payload = verify_token(token)
    result = await session.exec(select(User).where(User.id == payload["id"]))
    user = result.first()
    if not user:
        raise HTTPException(detail="user not found", status_code=404)
    return user

async def user_role(user: UserRead = Depends(get_current_user)) -> str:
    return user.role
