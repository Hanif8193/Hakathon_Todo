---
description: Authentication and authorization with JWT, OAuth2, password hashing, and role-based access control
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Authentication & Authorization Expert Skill

You are an expert in implementing secure authentication and authorization systems using JWT, OAuth2, and role-based access control (RBAC) in FastAPI.

### Security Overview

```text
┌──────────────────────────────────────────────────────────────┐
│                    Authentication Flow                       │
│                                                              │
│  Client ──► Login ──► Verify Credentials ──► Issue JWT       │
│                                                              │
│  Client ──► Request + JWT ──► Validate Token ──► Authorize   │
└──────────────────────────────────────────────────────────────┘
```

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Cost factor for bcrypt
)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

### JWT Token Management

```python
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError
from pydantic import BaseModel

from app.config import settings


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: str  # Subject (user ID)
    exp: datetime  # Expiration time
    iat: datetime  # Issued at
    type: str  # Token type: "access" or "refresh"
    scopes: list[str] = []  # Permission scopes


class TokenPair(BaseModel):
    """Access and refresh token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


def create_access_token(
    subject: str | int,
    scopes: list[str] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a new access token."""
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    ))

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "access",
        "scopes": scopes or [],
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_refresh_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a new refresh token."""
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    ))

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "refresh",
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_token(token: str) -> TokenPayload | None:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return TokenPayload(**payload)
    except JWTError:
        return None


def create_token_pair(
    user_id: int,
    scopes: list[str] | None = None,
) -> TokenPair:
    """Create both access and refresh tokens."""
    access_token = create_access_token(user_id, scopes)
    refresh_token = create_refresh_token(user_id)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
```

### OAuth2 Password Flow

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated

from app.models.user import User
from app.repositories.user import UserRepository
from app.core.security import verify_password, decode_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scopes={
        "users:read": "Read user information",
        "users:write": "Create and update users",
        "admin": "Full administrative access",
    },
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if not payload or payload.type != "access":
        raise credentials_exception

    user = await user_repo.get_by_id(int(payload.sub))
    if not user:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


# Type aliases for cleaner code
CurrentUser = Annotated[User, Depends(get_current_user)]
ActiveUser = Annotated[User, Depends(get_current_active_user)]
```

### Role-Based Access Control (RBAC)

```python
from enum import Enum
from functools import wraps
from fastapi import Depends, HTTPException, status
from typing import Annotated


class Role(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class Permission(str, Enum):
    # User permissions
    READ_USERS = "users:read"
    WRITE_USERS = "users:write"
    DELETE_USERS = "users:delete"

    # Post permissions
    READ_POSTS = "posts:read"
    WRITE_POSTS = "posts:write"
    DELETE_POSTS = "posts:delete"

    # Admin permissions
    MANAGE_ROLES = "roles:manage"
    VIEW_ANALYTICS = "analytics:view"


# Role-permission mapping
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.USER: {
        Permission.READ_USERS,
        Permission.READ_POSTS,
        Permission.WRITE_POSTS,
    },
    Role.MODERATOR: {
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.READ_POSTS,
        Permission.WRITE_POSTS,
        Permission.DELETE_POSTS,
    },
    Role.ADMIN: set(Permission),  # All permissions
}


def get_user_permissions(user: User) -> set[Permission]:
    """Get all permissions for a user based on their role."""
    return ROLE_PERMISSIONS.get(Role(user.role), set())


class PermissionChecker:
    """Dependency for checking user permissions."""

    def __init__(self, required_permissions: list[Permission]):
        self.required_permissions = set(required_permissions)

    async def __call__(
        self,
        current_user: ActiveUser,
    ) -> User:
        user_permissions = get_user_permissions(current_user)

        if not self.required_permissions.issubset(user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user


# Usage as dependency
def require_permissions(*permissions: Permission):
    """Create a permission checker dependency."""
    return Depends(PermissionChecker(list(permissions)))


# Example usage in endpoints
@router.delete(
    "/users/{user_id}",
    dependencies=[require_permissions(Permission.DELETE_USERS)],
)
async def delete_user(user_id: int, current_user: ActiveUser):
    pass
```

### Authentication Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.core.security import (
    verify_password,
    create_token_pair,
    decode_token,
    hash_password,
)
from app.repositories.user import UserRepository
from app.schemas.auth import TokenPair

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post(
    "/login",
    response_model=TokenPair,
    summary="User login",
    description="Authenticate user and return JWT tokens.",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> TokenPair:
    # Find user by email (username field in OAuth2 form)
    user = await user_repo.get_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Create token pair with user's scopes
    scopes = [p.value for p in get_user_permissions(user)]
    return create_token_pair(user.id, scopes)


@router.post(
    "/register",
    response_model=TokenPair,
    status_code=status.HTTP_201_CREATED,
    summary="User registration",
)
async def register(
    request: RegisterRequest,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> TokenPair:
    # Check if email exists
    if await user_repo.get_by_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Check if username exists
    if await user_repo.get_by_username(request.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    # Create user
    user = await user_repo.create({
        "email": request.email,
        "username": request.username,
        "hashed_password": hash_password(request.password),
        "role": Role.USER.value,
    })

    return create_token_pair(user.id)


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Refresh access token",
)
async def refresh_token(
    request: RefreshRequest,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> TokenPair:
    payload = decode_token(request.refresh_token)

    if not payload or payload.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = await user_repo.get_by_id(int(payload.sub))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    scopes = [p.value for p in get_user_permissions(user)]
    return create_token_pair(user.id, scopes)


@router.post("/logout", summary="User logout")
async def logout(current_user: ActiveUser):
    """
    Logout endpoint - client should discard tokens.
    For server-side token invalidation, implement token blacklisting.
    """
    return {"message": "Successfully logged out"}


@router.get("/me", summary="Get current user")
async def get_me(current_user: ActiveUser):
    return current_user
```

### API Key Authentication

```python
from fastapi import Security
from fastapi.security import APIKeyHeader, APIKeyQuery

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def get_api_key(
    api_key_header: str | None = Security(api_key_header),
    api_key_query: str | None = Security(api_key_query),
) -> str:
    """Extract API key from header or query parameter."""
    api_key = api_key_header or api_key_query

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )

    # Validate API key (check database, cache, etc.)
    if not await validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return api_key


# Usage
@router.get("/external-data")
async def get_external_data(
    api_key: Annotated[str, Depends(get_api_key)],
):
    pass
```

### OAuth2 External Providers

```python
from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from fastapi.responses import RedirectResponse

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/oauth/google")
async def google_login(request: Request):
    """Redirect to Google OAuth."""
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/oauth/google/callback")
async def google_callback(
    request: Request,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
):
    """Handle Google OAuth callback."""
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    # Find or create user
    user = await user_repo.get_by_email(user_info["email"])
    if not user:
        user = await user_repo.create({
            "email": user_info["email"],
            "username": user_info.get("name", user_info["email"].split("@")[0]),
            "hashed_password": "",  # OAuth users don't have passwords
            "oauth_provider": "google",
            "oauth_id": user_info["sub"],
        })

    tokens = create_token_pair(user.id)
    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/auth/callback?token={tokens.access_token}"
    )
```

### Security Configuration

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class SecuritySettings(BaseSettings):
    # JWT settings
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Password settings
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # OAuth settings
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: SecretStr | None = None

    # Rate limiting
    LOGIN_RATE_LIMIT: str = "5/minute"
    REGISTER_RATE_LIMIT: str = "3/minute"


settings = SecuritySettings()
```

### Security Middleware

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response


# Add to app
app.add_middleware(SecurityHeadersMiddleware)
```

### Auth Checklist

- [ ] Use bcrypt for password hashing (cost factor >= 12)
- [ ] Implement JWT with short-lived access tokens
- [ ] Use refresh tokens for session extension
- [ ] Store secrets in environment variables
- [ ] Implement rate limiting on auth endpoints
- [ ] Add security headers middleware
- [ ] Validate token type (access vs refresh)
- [ ] Implement role-based access control
- [ ] Log authentication events
- [ ] Handle token revocation/blacklisting

---

When implementing authentication, always follow security best practices and never store sensitive data in plain text.
