from sqlmodel import Field, SQLModel
from typing import Optional



class Book(SQLModel,table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    title: str
    price: float
    description: Optional[str] = Field(default=None)
    author: str = Field(default="未知作者")
    is_borrowed: bool = Field(default=False)

    #外键，连接User表，作为所有者id
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")



class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str

