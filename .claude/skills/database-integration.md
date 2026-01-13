---
description: Database integration with SQLAlchemy async, SQLite for development, PostgreSQL for production, migrations with Alembic
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Database Integration Expert Skill

You are an expert in database integration using SQLAlchemy async ORM with SQLite for development and PostgreSQL for production environments.

### Database Strategy Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                    Environment Strategy                      │
├─────────────────────────────────────────────────────────────┤
│  Development  │  SQLite (aiosqlite)    │  Fast, no setup    │
│  Testing      │  SQLite in-memory      │  Isolated tests    │
│  Production   │  PostgreSQL (asyncpg)  │  Scalable, robust  │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```text
app/
├── db/
│   ├── __init__.py
│   ├── base.py          # Base model class
│   ├── session.py       # Database session management
│   └── migrations/      # Alembic migrations
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
├── models/
│   ├── __init__.py
│   └── *.py             # SQLAlchemy models
└── config.py            # Database configuration
```

### Configuration Setup

```python
from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: str = "development"

    # SQLite settings (development)
    SQLITE_DATABASE: str = "app.db"

    # PostgreSQL settings (production)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "app"

    # Connection pool settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Generate database URL based on environment."""
        if self.ENVIRONMENT == "production":
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return f"sqlite+aiosqlite:///./{self.SQLITE_DATABASE}"

    @computed_field
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Sync URL for Alembic migrations."""
        if self.ENVIRONMENT == "production":
            return (
                f"postgresql://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return f"sqlite:///./{self.SQLITE_DATABASE}"


settings = DatabaseSettings()
```

### Base Model Definition

```python
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

### SQLAlchemy Models

```python
from sqlalchemy import (
    String, Integer, Boolean, Text, ForeignKey,
    UniqueConstraint, Index, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum

from app.db.base import Base, TimestampMixin, SoftDeleteMixin


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    # Columns
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus),
        default=UserStatus.ACTIVE,
        nullable=False,
    )

    # Relationships
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    profile: Mapped["UserProfile"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Table arguments
    __table_args__ = (
        Index("ix_users_email_status", "email", "status"),
    )


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
    )
    bio: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    location: Mapped[str | None] = mapped_column(String(100))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="profile")


class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(250), unique=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    author: Mapped["User"] = relationship(back_populates="posts")
    tags: Mapped[list["Tag"]] = relationship(
        secondary="post_tags",
        back_populates="posts",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_posts_author_published", "author_id", "is_published"),
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    posts: Mapped[list["Post"]] = relationship(
        secondary="post_tags",
        back_populates="tags",
    )


# Association table for many-to-many
from sqlalchemy import Table, Column

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
```

### Async Database Session

```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool, NullPool

from app.config import settings
from app.db.base import Base


def create_engine() -> AsyncEngine:
    """Create async database engine based on environment."""
    connect_args = {}
    poolclass = None

    if "sqlite" in settings.DATABASE_URL:
        # SQLite specific settings
        connect_args = {"check_same_thread": False}
        poolclass = StaticPool
    else:
        # PostgreSQL specific settings
        poolclass = NullPool if settings.ENVIRONMENT == "testing" else None

    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.ENVIRONMENT == "development",
        pool_pre_ping=True,
        pool_size=settings.DB_POOL_SIZE if "postgresql" in settings.DATABASE_URL else 0,
        max_overflow=settings.DB_MAX_OVERFLOW if "postgresql" in settings.DATABASE_URL else 0,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        connect_args=connect_args,
        poolclass=poolclass,
    )


engine = create_engine()

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
```

### Application Lifespan

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.session import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(lifespan=lifespan)
```

### Alembic Setup

```bash
# Install alembic
pip install alembic

# Initialize alembic
alembic init app/db/migrations
```

**alembic.ini** (key settings):
```ini
[alembic]
script_location = app/db/migrations
prepend_sys_path = .
sqlalchemy.url = driver://user:pass@localhost/dbname
```

**app/db/migrations/env.py**:
```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.config import settings
from app.db.base import Base
from app.models import *  # Import all models

config = context.config
config.set_main_option("sqlalchemy.url", settings.SYNC_DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
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


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Migration Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Add users table"

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history

# Generate SQL without executing
alembic upgrade head --sql
```

### PostgreSQL-Specific Features

```python
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import (
    ARRAY, JSONB, UUID, INET, CIDR,
    TSVECTOR, insert as pg_insert
)
from sqlalchemy.orm import Mapped, mapped_column
import uuid


class AdvancedPost(Base):
    __tablename__ = "advanced_posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(50)), default=[])
    metadata: Mapped[dict] = mapped_column(JSONB, default={})
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR)


# Full-text search query
async def search_posts(db: AsyncSession, query: str):
    result = await db.execute(
        select(AdvancedPost)
        .where(AdvancedPost.search_vector.match(query))
        .order_by(text("ts_rank(search_vector, plainto_tsquery(:q)) DESC"))
        .params(q=query)
    )
    return result.scalars().all()


# Upsert (INSERT ... ON CONFLICT)
async def upsert_user(db: AsyncSession, user_data: dict):
    stmt = pg_insert(User).values(**user_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["email"],
        set_={
            "username": stmt.excluded.username,
            "updated_at": func.now(),
        },
    )
    await db.execute(stmt)
    await db.commit()
```

### SQLite-Specific Considerations

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine


# Enable foreign keys for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# SQLite doesn't support ARRAY - use JSON instead
class SQLiteCompatibleModel(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Use JSON for array-like data in SQLite
    tags: Mapped[list[str]] = mapped_column(JSON, default=[])
```

### Database Testing Setup

```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest_asyncio.fixture
async def test_db():
    """Create in-memory SQLite database for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield async_session

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_db):
    """Get a database session for tests."""
    async with test_db() as session:
        yield session


class TestUserRepository:
    async def test_create_user(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        user = await repo.create(UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123",
        ))
        assert user.id is not None
        assert user.email == "test@example.com"
```

### Connection Pool Monitoring

```python
from sqlalchemy import event
from sqlalchemy.pool import Pool
import logging

logger = logging.getLogger(__name__)


@event.listens_for(Pool, "checkout")
def on_checkout(dbapi_conn, connection_rec, connection_proxy):
    logger.debug("Connection checked out from pool")


@event.listens_for(Pool, "checkin")
def on_checkin(dbapi_conn, connection_rec):
    logger.debug("Connection returned to pool")


@event.listens_for(Pool, "connect")
def on_connect(dbapi_conn, connection_rec):
    logger.info("New database connection created")


@event.listens_for(Pool, "invalidate")
def on_invalidate(dbapi_conn, connection_rec, exception):
    logger.warning(f"Connection invalidated: {exception}")
```

### Environment File Template

```env
# .env.example

# Environment
ENVIRONMENT=development  # development | testing | production

# SQLite (development)
SQLITE_DATABASE=app.db

# PostgreSQL (production)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=myapp

# Connection Pool
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
```

### Database Integration Checklist

- [ ] Configure environment-based database URLs
- [ ] Use async SQLAlchemy with aiosqlite/asyncpg
- [ ] Define Base model with common mixins (timestamps, soft delete)
- [ ] Set up proper relationships with cascade options
- [ ] Create indexes for frequently queried columns
- [ ] Initialize Alembic for migrations
- [ ] Enable foreign keys for SQLite
- [ ] Configure connection pooling for PostgreSQL
- [ ] Set up test database with in-memory SQLite
- [ ] Implement proper session management with try/commit/rollback

---

When integrating databases, use SQLite for development speed and PostgreSQL for production reliability. Always use async patterns and proper migration management.
