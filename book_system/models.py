from sqlmodel import Field, SQLModel
from pydantic import BaseModel
from typing import Optional


class BookCreate(BaseModel):
    title: str = Field(min_length=1,max_length=50)
    price: float = Field(gt=0)

class Book(SQLModel,table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    title: str
    price: float
    description: Optional[str] = Field(default=None)
    author: str = Field(default="未知作者")
    is_borrowed: bool = Field(default=False)

    #外键，连接User表，作为所有者id
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

class UserCreate(BaseModel):
    username: str
    password: str = Field(...,min_length=6,max_length=72)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str