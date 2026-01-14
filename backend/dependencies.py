"""Dependency injection functions for FastAPI.

This module provides reusable dependency functions for database sessions
and user authentication across all API endpoints.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.database import async_session_maker
from backend.auth import extract_user_id_from_token
from backend.models import User

# HTTP Bearer token security scheme for Swagger UI
security = HTTPBearer()


async def get_session() -> AsyncSession:
    """Dependency function to get database session.

    Yields an async session that automatically commits on success
    or rolls back on error. Use this in route handlers for database access.

    Usage:
        @app.get("/items")
        async def read_items(session: AsyncSession = Depends(get_session)):
            statement = select(Item)
            results = await session.exec(statement)
            return results.all()
    """
    async with async_session_maker() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> User:
    """Dependency function to get authenticated user from JWT token.

    Extracts JWT token from Authorization header, validates it, extracts user_id,
    and retrieves user from database. Returns 401 Unauthorized if token is invalid
    or user doesn't exist.

    Usage:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id, "email": current_user.email}

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        session: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException: 401 Unauthorized if token is invalid or user not found
    """
    token = credentials.credentials

    # Extract user_id from JWT token
    user_id = extract_user_id_from_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Retrieve user from database
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    session: AsyncSession = Depends(get_session)
) -> Optional[User]:
    """Optional authentication dependency (doesn't fail if no token provided).

    Useful for endpoints that behave differently for authenticated vs anonymous users.

    Usage:
        @app.get("/content")
        async def get_content(user: Optional[User] = Depends(get_optional_current_user)):
            if user:
                return {"message": f"Welcome back, {user.email}"}
            else:
                return {"message": "Welcome, guest"}

    Args:
        credentials: Optional HTTP Bearer credentials
        session: Database session

    Returns:
        User object if authenticated, None if no token provided or invalid
    """
    if credentials is None:
        return None

    token = credentials.credentials
    user_id = extract_user_id_from_token(token)

    if user_id is None:
        return None

    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    return user
