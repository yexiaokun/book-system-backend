from logging.config import fileConfig
import asyncio
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context


import sys, os
sys.path.append(os.getcwd())
from sqlmodel import SQLModel
from models import Book, User, BorrowHistory

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    # 优先从环境变量获取 (适配 Docker)
    url = os.getenv("DATABASE_URL")
    if not url:
        # 如果环境变量没取到，试图读 alembic.ini (兜底)
        url = config.get_main_option("sqlalchemy.url")
    if url and "pymysql" in url:
        url = url.replace("pymysql", "aiomysql")
    
    if not url:
        raise ValueError("❌ 错误: 未找到 DATABASE_URL 环境变量！")
    return url


def run_migrations_offline() -> None:
    """离线模式 (一般不用)"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """在线模式 (简化版)"""
    
    # 👇👇👇 核心修改：直接拿 URL，不绕弯子 👇👇👇
    db_url = get_url()
    
    # 🐛 调试打印：让你看到到底读到了啥
    print(f"-------- 🐛 DEBUG: Alembic is using URL: {db_url} --------")

    if not db_url:
        raise ValueError("❌ 致命错误: DATABASE_URL 是空的！请检查 docker-compose.yml 和 .env")

    # 直接创建引擎，简单粗暴有效
    connectable = create_async_engine(
        db_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
