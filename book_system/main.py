from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from database import engine
from routers import books, auth
import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 数据库表结构同步中...")
    SQLModel.metadata.create_all(engine)
    yield
    print("🛑 应用结束")

app = FastAPI(lifespan=lifespan)

app.include_router(books.router)
app.include_router(auth.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)