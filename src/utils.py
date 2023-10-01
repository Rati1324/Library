import os, time
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
from decouple import config
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .schemas import TokenSchema
from sqlalchemy.orm import Session
from .config import SessionLocal
from src.models import User

oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

ALGORITHM = config('ALGORITHM')
JWT_SECRET_KEY = config('SECRET_KEY')
JWT_REFRESH_SECRET_KEY = config('REFRESH_SECRET_KEY')

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_hashed_password(password: str) -> str:
    return hash_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return hash_context.verify(password, hashed_pass)

def create_access_token(subject: str, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def decode_jwt(token: str):
    # try:
    decode_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    return decode_token if decode_token["exp"] >= time.time() else False
    # except:
    #     return {}

# receives token and decodes it, returns user
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
