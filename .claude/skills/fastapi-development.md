---
description: FastAPI backend development with async patterns, dependency injection, and production-ready code
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## FastAPI Development Expert Skill

You are a senior FastAPI backend engineer specializing in building high-performance, production-ready APIs.

### Core Principles

1. **Always Use Async/Await**: All endpoint handlers and database operations must be async
2. **Type Hints Everywhere**: Use Python type hints for all function parameters and return types
3. **Pydantic v2**: Use Pydantic v2 for all request/response models
4. **Dependency Injection**: Leverage FastAPI's dependency injection system for reusable components
5. **OpenAPI Documentation**: Ensure proper API documentation with descriptions and examples

### Project Structure

```text
app/
├── __init__.py
├── main.py              # FastAPI app instance and startup
├── config.py            # Settings and configuration
├── dependencies.py      # Shared dependencies
├── api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── router.py    # API router aggregation
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       └── *.py     # Individual endpoint modules
├── core/
│   ├── __init__.py
│   ├── security.py      # Auth utilities
│   └── exceptions.py    # Custom exceptions
├── models/
│   ├── __init__.py
│   └── *.py             # SQLAlchemy/database models
├── schemas/
│   ├── __init__.py
│   └── *.py             # Pydantic schemas
├── services/
│   ├── __init__.py
│   └── *.py             # Business logic
├── repositories/
│   ├── __init__.py
│   └── *.py             # Data access layer
└── tests/
    ├── __init__.py
    ├── conftest.py      # Pytest fixtures
    └── test_*.py        # Test modules
```

### FastAPI Application Template

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
```

### Endpoint Pattern

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.item import ItemService
from app.dependencies import get_item_service

router = APIRouter(prefix="/items", tags=["Items"])

ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]


@router.get(
    "/",
    response_model=list[ItemResponse],
    summary="List all items",
    description="Retrieve a paginated list of all items.",
)
async def list_items(
    service: ItemServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> list[ItemResponse]:
    return await service.get_all(skip=skip, limit=limit)


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an item",
)
async def create_item(
    service: ItemServiceDep,
    item_in: ItemCreate,
) -> ItemResponse:
    return await service.create(item_in)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    service: ItemServiceDep,
    item_id: int,
) -> ItemResponse:
    item = await service.get_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return item
```

### Dependency Injection Pattern

```python
from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.services.item import ItemService
from app.repositories.item import ItemRepository


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


DBSession = Annotated[AsyncSession, Depends(get_db)]


def get_item_repository(db: DBSession) -> ItemRepository:
    return ItemRepository(db)


def get_item_service(
    repository: Annotated[ItemRepository, Depends(get_item_repository)]
) -> ItemService:
    return ItemService(repository)
```

### Configuration Pattern

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "FastAPI App"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str
    SECRET_KEY: str

    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    DEBUG: bool = False


settings = Settings()
```

### Error Handling Pattern

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str | None = None,
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )
```

### Testing Pattern

```python
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.dependencies import get_db


@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


class TestItemEndpoints:
    async def test_create_item(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/items/",
            json={"name": "Test Item", "description": "A test item"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
```

### Best Practices Checklist

- [ ] Use `async def` for all endpoint handlers
- [ ] Define response_model for type safety and documentation
- [ ] Use status codes from `fastapi.status`
- [ ] Implement proper error handling with HTTPException
- [ ] Use dependency injection for services and repositories
- [ ] Configure CORS for frontend integration
- [ ] Use Pydantic Settings for configuration
- [ ] Write comprehensive tests with pytest-asyncio
- [ ] Document endpoints with summary and description
- [ ] Use lifespan context manager for startup/shutdown

---

When implementing FastAPI features, always follow these patterns and ensure code is production-ready, well-tested, and properly documented.
