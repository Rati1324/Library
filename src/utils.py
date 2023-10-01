import os, time
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .schemas import TokenSchema
from sqlalchemy.orm import Session
from .config import SessionLocal
from src.models import User
from .config import get_db
from decouple import config
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ALGORITHM = config('ALGORITHM')
JWT_SECRET_KEY = config('SECRET_KEY')

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return hash_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return hash_context.verify(password, hashed_pass)

def create_access_token(subject: str, expires_delta: int = None) -> str:
    to_encode = {"sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
       
        token_data = TokenSchema(username=username)

    except JWTError:
        raise credential_exception
    
    user = db.query(User).filter_by(username=username).first()
    if user is None:
        raise credential_exception
       
    return user
