from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import declarative_base

from app import config

# Create the async engine
async_engine: AsyncEngine = create_async_engine(
    config.get_postgres_dsn("asyncpg"),
    echo=True,
    pool_size=config.DATABASE_ASYNC_POOL_SIZE,
    max_overflow=0,
    pool_recycle=config.DATABASE_POOL_RECYCLE_SECONDS,
)

# Create the async session maker
AsyncSessionMaker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession,
)

# Create a declarative base
Base = declarative_base()


# Async generator to get the async session
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionMaker() as db:
        yield db


async def create_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
