from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel , Field

# T = TypeVar('T')

class UserSchema(BaseModel):
    # id: int = Field(default=None)
    username: str = Field(default=None)
    email: str = Field(default=None)
    password: str = Field(default=None)

    class Config:
        from_attributes = True

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

class SystemUser(UserLoginSchema):
    password: str

class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
