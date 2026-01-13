---
description: CRUD operations with repository pattern, SQLAlchemy async, and service layer architecture
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## CRUD Operations Expert Skill

You are an expert in implementing CRUD (Create, Read, Update, Delete) operations using clean architecture patterns with SQLAlchemy and FastAPI.

### Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                            │
│  (Endpoints receive requests, return responses)             │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     Service Layer                           │
│  (Business logic, validation, orchestration)                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Repository Layer                          │
│  (Data access, database operations)                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     Database Layer                          │
│  (SQLAlchemy models, database connection)                   │
└─────────────────────────────────────────────────────────────┘
```

### Database Model (SQLAlchemy)

```python
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

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


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(String(10000))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationships
    author: Mapped["User"] = relationship(back_populates="posts")
```

### Database Session Setup

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from app.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Pydantic Schemas

```python
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# Base schemas
class UserBase(BaseModel):
    email: str = Field(max_length=255)
    username: str = Field(min_length=3, max_length=50)


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=10000)


# Create schemas
class UserCreate(UserBase):
    password: str = Field(min_length=8)


class PostCreate(PostBase):
    pass


# Update schemas (all fields optional)
class UserUpdate(BaseModel):
    email: str | None = Field(None, max_length=255)
    username: str | None = Field(None, min_length=3, max_length=50)
    password: str | None = Field(None, min_length=8)
    is_active: bool | None = None


class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1, max_length=10000)
    is_published: bool | None = None


# Response schemas
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_published: bool
    author_id: int
    created_at: datetime
    updated_at: datetime


# List response with pagination
class PaginatedUsers(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    limit: int
    pages: int
```

### Generic Base Repository

```python
from typing import Generic, TypeVar, Type, Sequence
from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic base repository with CRUD operations."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> ModelType | None:
        """Get a single record by ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:
        """Get all records with pagination."""
        result = await self.db.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.id)
        )
        return result.scalars().all()

    async def count(self) -> int:
        """Count total records."""
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        id: int,
        obj_in: UpdateSchemaType,
    ) -> ModelType | None:
        """Update an existing record."""
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0

    async def exists(self, id: int) -> bool:
        """Check if a record exists."""
        result = await self.db.execute(
            select(func.count())
            .select_from(self.model)
            .where(self.model.id == id)
        )
        return result.scalar_one() > 0
```

### Specific Repository Implementation

```python
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User-specific repository with additional methods."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[User]:
        """Get all active users."""
        result = await self.db.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def deactivate(self, id: int) -> User | None:
        """Deactivate a user."""
        user = await self.get_by_id(id)
        if user:
            user.is_active = False
            await self.db.flush()
            await self.db.refresh(user)
        return user
```

### Service Layer

```python
from typing import Sequence
from fastapi import HTTPException, status
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse, PaginatedUsers
from app.core.security import hash_password


class UserService:
    """User business logic layer."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_user(self, user_id: int) -> UserResponse:
        """Get user by ID or raise 404."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        return UserResponse.model_validate(user)

    async def get_users(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> PaginatedUsers:
        """Get paginated list of users."""
        skip = (page - 1) * limit
        users = await self.repository.get_all(skip=skip, limit=limit)
        total = await self.repository.count()
        pages = (total + limit - 1) // limit

        return PaginatedUsers(
            items=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )

    async def create_user(self, user_in: UserCreate) -> UserResponse:
        """Create new user with validation."""
        # Check email uniqueness
        if await self.repository.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # Check username uniqueness
        if await self.repository.get_by_username(user_in.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        # Hash password before storage
        user_data = user_in.model_dump()
        user_data["hashed_password"] = hash_password(user_data.pop("password"))

        user = await self.repository.create(
            UserCreate.model_validate(user_data)
        )
        return UserResponse.model_validate(user)

    async def update_user(
        self,
        user_id: int,
        user_in: UserUpdate,
    ) -> UserResponse:
        """Update existing user."""
        # Check existence
        existing = await self.repository.get_by_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )

        # Check email uniqueness if updating email
        if user_in.email and user_in.email != existing.email:
            if await self.repository.get_by_email(user_in.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use",
                )

        # Hash password if provided
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(
                update_data.pop("password")
            )

        user = await self.repository.update(
            user_id,
            UserUpdate.model_validate(update_data),
        )
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int) -> None:
        """Delete user by ID."""
        if not await self.repository.exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        await self.repository.delete(user_id)
```

### API Endpoints

```python
from fastapi import APIRouter, Depends, status
from typing import Annotated

from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, PaginatedUsers
)
from app.services.user import UserService
from app.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["Users"])

UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.get(
    "/",
    response_model=PaginatedUsers,
    summary="List users",
    description="Get a paginated list of all users.",
)
async def list_users(
    service: UserServiceDep,
    page: int = 1,
    limit: int = 20,
) -> PaginatedUsers:
    return await service.get_users(page=page, limit=limit)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new user account.",
)
async def create_user(
    service: UserServiceDep,
    user_in: UserCreate,
) -> UserResponse:
    return await service.create_user(user_in)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user",
    description="Get a specific user by ID.",
)
async def get_user(
    service: UserServiceDep,
    user_id: int,
) -> UserResponse:
    return await service.get_user(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update an existing user.",
)
async def update_user(
    service: UserServiceDep,
    user_id: int,
    user_in: UserUpdate,
) -> UserResponse:
    return await service.update_user(user_id, user_in)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user by ID.",
)
async def delete_user(
    service: UserServiceDep,
    user_id: int,
) -> None:
    await service.delete_user(user_id)
```

### Dependency Injection Setup

```python
from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.repositories.user import UserRepository
from app.services.user import UserService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


DBSession = Annotated[AsyncSession, Depends(get_db)]


def get_user_repository(db: DBSession) -> UserRepository:
    return UserRepository(db)


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    return UserService(repository)
```

### CRUD Operations Checklist

- [ ] Database models with proper relationships and indexes
- [ ] Pydantic schemas for Create, Update, and Response
- [ ] Generic base repository with common operations
- [ ] Specific repositories for custom queries
- [ ] Service layer for business logic and validation
- [ ] API endpoints with proper HTTP methods and status codes
- [ ] Dependency injection for loose coupling
- [ ] Pagination support for list endpoints
- [ ] Proper error handling (404, 409, 422)
- [ ] Transaction management in database sessions

---

When implementing CRUD operations, always follow the repository-service-endpoint pattern for clean separation of concerns.
