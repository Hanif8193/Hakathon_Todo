"""Database configuration and session management for Todo application.

This module provides async database engine, session management, and initialization
functions for SQLModel with PostgreSQL (Neon) backend.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please set it in .env file (copy from .env.example)"
    )

# Create async engine for PostgreSQL with asyncpg driver
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (set to False in production)
    future=True,
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """Dependency function to get database session.

    Yields an async session that automatically commits on success
    or rolls back on error.

    Usage:
        @app.get("/items")
        async def read_items(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session_maker() as session:
        yield session


async def init_db():
    """Initialize database schema by creating all tables.

    This function creates all SQLModel tables if they don't exist.
    Run this once during application startup or via CLI command.

    Usage:
        # In main.py startup event
        await init_db()

        # Or via CLI
        python -c "import asyncio; from backend.database import init_db; asyncio.run(init_db())"
    """
    async with engine.begin() as conn:
        # Import models to ensure they're registered with SQLModel
        from backend.models import User, Task

        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
        print(">>> Database tables created successfully")
