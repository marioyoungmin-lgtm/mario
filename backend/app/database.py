"""Async database setup for LifeOS 0-21.

This module centralizes PostgreSQL connectivity using SQLAlchemy's async engine
and exposes a dependency helper (`get_db`) for FastAPI routes.
"""

from collections.abc import AsyncGenerator
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# PostgreSQL DSN for asyncpg driver.
# Override with env var in each environment.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/lifeos",
)

# Async engine is the core DB interface in SQLAlchemy 2.0 async mode.
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Session factory to create per-request AsyncSession instances.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Declarative base inherited by all ORM models.
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a managed async DB session."""
    async with AsyncSessionLocal() as session:
        yield session
