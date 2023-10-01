from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordRequestForm 

# T = TypeVar('T')

class UserSchema(BaseModel):
    # id: int = Field(default=None)
    username: str = Field(default=None)
    email: str = Field(default=None)
    password: str = Field(default=None)

    class Config:
        from_attributes = True

# create a book schema, based on the model Book in models.py
class BookSchema(BaseModel):
    title: str = Field(default=None)
    genre: str = Field(default=None)
    condition: str = Field(default=None)
    author: str = Field(default=None)

class UserLoginSchema(BaseModel):
    email: str = Field(default=None)
    password: str = Field(default=None)

    class Config:
        from_attributes = True

class TokenSchema(BaseModel):
    access_token: str = Field(default=None)
    refresh_token: str = Field(default=None)

    class Config:
        from_attributes = True

class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None

class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    email: str = Field(default=None)

class Token(BaseModel):
    access_token: str
    token_type: str

class BookRequestSchema(BaseModel):
    book_id: int = Field(default=None)

    class Config:
        from_attributes = True

class BookRequestAcceptSchema(BaseModel):
    location: str = Field(default=None)

    class Config:
        from_attributes = True