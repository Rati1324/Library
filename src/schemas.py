from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel , Field
from pydantic.generics import GenericModel

# T = TypeVar('T')

class UserSchema(BaseModel):
    # id: int = Field(default=None)
    username: str = Field(default=None)
    email: str = Field(default=None)
    password: str = Field(default=None)

    class Config:
        from_attributes = True