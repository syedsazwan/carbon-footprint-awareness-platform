from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta, timezone
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS
import database as db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    # Store essential user data in payload
    payload = {
        "id": to_encode.get("id"),
        "username": to_encode.get("username"),
        "role": to_encode.get("role"),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    encoded_jwt = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: int = payload.get("id")
        username: str = payload.get("username")
        if user_id is None or username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user
