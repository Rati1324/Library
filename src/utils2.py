import os, time
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from decouple import config

ACCESS_TOKEN_EXPIRE_MINUTES = 30 
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 

ALGORITHM = config('ALGORITHM')
JWT_SECRET_KEY = config('SECRET_KEY')
JWT_REFRESH_SECRET_KEY = config('REFRESH_SECRET_KEY')

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
