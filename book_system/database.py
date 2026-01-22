from sqlmodel import create_engine, Session
from sqlalchemy.exc import OperationalError
import os, time

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:root@127.0.0.1:3306/book_system"
    )

def get_engine_with_retry():
    while True:
        try:
            engine = create_engine(DATABASE_URL, echo=True)
            with engine.connect() as conn:
                print("✅ 数据库连接成功！")
                return engine
        except OperationalError:
            print("⏳ 数据库正在启动中... 等待 3 秒后重试...")
            time.sleep(3)

engine = get_engine_with_retry()

def get_session():
    with Session(engine) as session:
        yield session