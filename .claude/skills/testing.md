---
description: Testing with pytest, async testing, fixtures, mocking, coverage, and test-driven development patterns
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Testing Expert Skill

You are an expert in testing Python applications using pytest, with specialization in async testing, FastAPI integration testing, and test-driven development.

### Testing Strategy Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                     Testing Pyramid                         │
├─────────────────────────────────────────────────────────────┤
│                      E2E Tests                              │
│                    (Few, Slow)                              │
│                   ┌──────────┐                              │
│                  /            \                             │
│        Integration Tests                                    │
│           (Some, Medium)                                    │
│         ┌──────────────────┐                                │
│        /                    \                               │
│              Unit Tests                                     │
│            (Many, Fast)                                     │
│    ┌────────────────────────────┐                           │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```text
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── pytest.ini               # Pytest configuration
├── unit/
│   ├── __init__.py
│   ├── test_services.py
│   ├── test_utils.py
│   └── test_models.py
├── integration/
│   ├── __init__.py
│   ├── test_repositories.py
│   └── test_database.py
├── api/
│   ├── __init__.py
│   ├── test_endpoints.py
│   └── test_auth.py
└── e2e/
    ├── __init__.py
    └── test_workflows.py
```

### Pytest Configuration

**pyproject.toml**:
```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "-ra",
    "--strict-markers",
    "--tb=short",
    "-x",  # Stop on first failure
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["app"]
branch = true
omit = [
    "*/tests/*",
    "*/__init__.py",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
fail_under = 80
show_missing = true
```

### Shared Fixtures (conftest.py)

```python
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import create_access_token


# Database fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


# Factory fixtures
@pytest.fixture
def user_factory(db_session: AsyncSession):
    """Factory for creating test users."""
    from app.models.user import User
    from app.core.security import hash_password

    async def create_user(
        email: str = "test@example.com",
        username: str = "testuser",
        password: str = "password123",
        is_active: bool = True,
    ) -> User:
        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            is_active=is_active,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return create_user


@pytest_asyncio.fixture
async def test_user(user_factory):
    """Create a default test user."""
    return await user_factory()


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user."""
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def authenticated_client(
    client: AsyncClient,
    auth_headers: dict,
) -> AsyncClient:
    """Client with authentication headers."""
    client.headers.update(auth_headers)
    return client
```

### Unit Testing

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.user import UserService
from app.schemas.user import UserCreate


class TestUserService:
    """Unit tests for UserService."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        repo = Mock()
        repo.get_by_id = AsyncMock(return_value=None)
        repo.get_by_email = AsyncMock(return_value=None)
        repo.create = AsyncMock()
        repo.update = AsyncMock()
        repo.delete = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_repository):
        """Create service with mock repository."""
        return UserService(mock_repository)

    async def test_create_user_success(self, service, mock_repository):
        """Test successful user creation."""
        # Arrange
        user_data = UserCreate(
            email="new@example.com",
            username="newuser",
            password="password123",
        )
        mock_repository.create.return_value = Mock(
            id=1,
            email="new@example.com",
            username="newuser",
        )

        # Act
        result = await service.create_user(user_data)

        # Assert
        mock_repository.create.assert_called_once()
        assert result.email == "new@example.com"

    async def test_create_user_duplicate_email(self, service, mock_repository):
        """Test user creation with duplicate email."""
        # Arrange
        user_data = UserCreate(
            email="existing@example.com",
            username="newuser",
            password="password123",
        )
        mock_repository.get_by_email.return_value = Mock(id=1)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.create_user(user_data)

        assert exc_info.value.status_code == 409
        assert "already registered" in str(exc_info.value.detail)

    async def test_get_user_not_found(self, service, mock_repository):
        """Test getting non-existent user."""
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.get_user(999)

        assert exc_info.value.status_code == 404


class TestPasswordUtils:
    """Unit tests for password utilities."""

    def test_hash_password(self):
        """Test password hashing."""
        from app.core.security import hash_password, verify_password

        password = "mysecretpassword"
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_hash_uniqueness(self):
        """Test that same password produces different hashes."""
        from app.core.security import hash_password

        password = "samepassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Salted hashes should differ
```

### Integration Testing

```python
import pytest
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class TestUserRepository:
    """Integration tests for UserRepository."""

    async def test_create_and_get_user(self, db_session):
        """Test creating and retrieving a user."""
        repo = UserRepository(db_session)

        # Create user
        user = await repo.create(UserCreate(
            email="test@example.com",
            username="testuser",
            password="hashedpassword",
        ))

        assert user.id is not None
        assert user.email == "test@example.com"

        # Retrieve user
        retrieved = await repo.get_by_id(user.id)
        assert retrieved is not None
        assert retrieved.email == user.email

    async def test_get_by_email(self, db_session, user_factory):
        """Test finding user by email."""
        repo = UserRepository(db_session)
        user = await user_factory(email="find@example.com")

        found = await repo.get_by_email("find@example.com")
        assert found is not None
        assert found.id == user.id

        not_found = await repo.get_by_email("nonexistent@example.com")
        assert not_found is None

    async def test_update_user(self, db_session, user_factory):
        """Test updating a user."""
        repo = UserRepository(db_session)
        user = await user_factory()

        updated = await repo.update(user.id, UserUpdate(
            username="updated_username"
        ))

        assert updated.username == "updated_username"
        assert updated.email == user.email  # Unchanged

    async def test_delete_user(self, db_session, user_factory):
        """Test deleting a user."""
        repo = UserRepository(db_session)
        user = await user_factory()

        result = await repo.delete(user.id)
        assert result is True

        deleted = await repo.get_by_id(user.id)
        assert deleted is None
```

### API Testing

```python
import pytest
from fastapi import status


class TestUserEndpoints:
    """API tests for user endpoints."""

    async def test_create_user(self, client):
        """Test POST /api/v1/users/"""
        response = await client.post(
            "/api/v1/users/",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "password123",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "new@example.com"
        assert "password" not in data
        assert "id" in data

    async def test_create_user_invalid_email(self, client):
        """Test POST /api/v1/users/ with invalid email."""
        response = await client.post(
            "/api/v1/users/",
            json={
                "email": "invalid-email",
                "username": "newuser",
                "password": "password123",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_users_unauthorized(self, client):
        """Test GET /api/v1/users/ without auth."""
        response = await client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_users_authorized(self, authenticated_client, test_user):
        """Test GET /api/v1/users/ with auth."""
        response = await authenticated_client.get("/api/v1/users/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1

    async def test_get_user_by_id(self, authenticated_client, test_user):
        """Test GET /api/v1/users/{id}"""
        response = await authenticated_client.get(
            f"/api/v1/users/{test_user.id}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    async def test_get_user_not_found(self, authenticated_client):
        """Test GET /api/v1/users/{id} with invalid ID."""
        response = await authenticated_client.get("/api/v1/users/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_user(self, authenticated_client, test_user):
        """Test PATCH /api/v1/users/{id}"""
        response = await authenticated_client.patch(
            f"/api/v1/users/{test_user.id}",
            json={"username": "updated_name"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "updated_name"

    async def test_delete_user(self, authenticated_client, user_factory):
        """Test DELETE /api/v1/users/{id}"""
        user = await user_factory(email="delete@example.com")

        response = await authenticated_client.delete(
            f"/api/v1/users/{user.id}"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestAuthEndpoints:
    """API tests for authentication endpoints."""

    async def test_login_success(self, client, test_user):
        """Test POST /api/v1/auth/login"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "password123",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client, test_user):
        """Test POST /api/v1/auth/login with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_user(self, authenticated_client, test_user):
        """Test GET /api/v1/auth/me"""
        response = await authenticated_client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
```

### Mocking External Services

```python
import pytest
from unittest.mock import AsyncMock, patch


class TestExternalServiceIntegration:
    """Tests with mocked external services."""

    async def test_send_email_on_registration(self, client):
        """Test email is sent when user registers."""
        with patch("app.services.email.send_welcome_email") as mock_send:
            mock_send.return_value = AsyncMock()

            response = await client.post(
                "/api/v1/users/",
                json={
                    "email": "new@example.com",
                    "username": "newuser",
                    "password": "password123",
                },
            )

            assert response.status_code == 201
            mock_send.assert_called_once_with("new@example.com")

    async def test_external_api_failure(self, client):
        """Test handling of external API failure."""
        with patch("app.services.external.fetch_data") as mock_fetch:
            mock_fetch.side_effect = Exception("API unavailable")

            response = await client.get("/api/v1/external-data/")

            assert response.status_code == 503

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        with patch("app.core.cache.redis_client") as mock:
            mock.get = AsyncMock(return_value=None)
            mock.set = AsyncMock(return_value=True)
            mock.delete = AsyncMock(return_value=True)
            yield mock

    async def test_cache_miss(self, client, mock_redis):
        """Test behavior on cache miss."""
        mock_redis.get.return_value = None

        response = await client.get("/api/v1/cached-data/123")

        assert response.status_code == 200
        mock_redis.set.assert_called_once()
```

### Parametrized Tests

```python
import pytest


class TestValidation:
    """Parametrized validation tests."""

    @pytest.mark.parametrize("email,expected_valid", [
        ("valid@example.com", True),
        ("user.name@domain.org", True),
        ("invalid-email", False),
        ("@nodomain.com", False),
        ("no@tld", False),
        ("", False),
    ])
    async def test_email_validation(self, client, email, expected_valid):
        """Test email validation with various inputs."""
        response = await client.post(
            "/api/v1/users/",
            json={
                "email": email,
                "username": "testuser",
                "password": "password123",
            },
        )

        if expected_valid:
            assert response.status_code in [201, 409]  # Created or conflict
        else:
            assert response.status_code == 422

    @pytest.mark.parametrize("password,expected_valid", [
        ("short", False),           # Too short
        ("password123", True),      # Valid
        ("12345678", True),         # Numbers only (if allowed)
        ("a" * 100, True),          # Long password
    ])
    async def test_password_validation(self, client, password, expected_valid):
        """Test password validation with various inputs."""
        response = await client.post(
            "/api/v1/users/",
            json={
                "email": f"test{len(password)}@example.com",
                "username": f"user{len(password)}",
                "password": password,
            },
        )

        if expected_valid:
            assert response.status_code == 201
        else:
            assert response.status_code == 422
```

### Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/api/test_endpoints.py

# Run specific test class
pytest tests/api/test_endpoints.py::TestUserEndpoints

# Run specific test
pytest tests/api/test_endpoints.py::TestUserEndpoints::test_create_user

# Run tests matching pattern
pytest -k "test_create"

# Run only unit tests (by marker)
pytest -m "not integration and not e2e"

# Run with verbose output
pytest -v --tb=long

# Run parallel tests
pytest -n auto  # requires pytest-xdist

# Generate JUnit XML report
pytest --junitxml=report.xml
```

### Testing Checklist

- [ ] Configure pytest with appropriate settings
- [ ] Create shared fixtures in conftest.py
- [ ] Write unit tests with mocked dependencies
- [ ] Write integration tests with real database
- [ ] Write API tests for all endpoints
- [ ] Use parametrized tests for validation
- [ ] Mock external services appropriately
- [ ] Set up test coverage reporting
- [ ] Configure CI to run tests automatically
- [ ] Maintain coverage above threshold (80%+)

---

When testing, follow the testing pyramid: many unit tests, some integration tests, few E2E tests. Always test both happy paths and error cases.
