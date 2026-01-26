from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, Any


T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None



class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    author: str
    description: str
    count: int = Field(gt=0, default=0)


class UserCreate(BaseModel):
    username: str
    password: str = Field(..., min_length=6, max_length=72)


class Token(BaseModel):
    access_token: str
    token_type: str