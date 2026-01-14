"""Authentication router for user signup and login endpoints.

This module provides POST /api/auth/signup and POST /api/auth/login
endpoints for user registration and authentication with JWT tokens.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from backend.database import get_session
from backend.models import User
from backend.schemas import (
    SignupRequest,
    LoginRequest,
    AuthResponse,
    UserProfile,
    ErrorResponse
)
from backend.auth import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "Email already registered"}
    }
)
async def signup(
    request: SignupRequest,
    session: AsyncSession = Depends(get_session)
):
    """Create new user account.

    Registers a new user with email and password. Returns JWT token upon success.

    **Business Rules**:
    - Email must be unique (no duplicate accounts)
    - Password must be at least 8 characters
    - Password is hashed with bcrypt before storage (never stored in plaintext)

    **FR-001**: System MUST provide user registration with email and password
    **FR-007**: System MUST hash and salt passwords before storing
    """
    # Check if email already exists
    statement = select(User).where(User.email == request.email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash password with bcrypt
    password_hash = hash_password(request.password)

    # Create new user
    user = User(
        email=request.email,
        password_hash=password_hash
    )

    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Generate JWT token with user_id claim
    token_data = {
        "sub": str(user.id),
        "email": user.email
    }
    token = create_access_token(token_data)

    # Return auth response
    return AuthResponse(
        user=UserProfile(
            id=user.id,
            email=user.email,
            created_at=user.created_at
        ),
        token=token,
        message="Account created successfully"
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"}
    }
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    """Authenticate user and issue JWT token.

    Validates user credentials and returns JWT token for authenticated requests.

    **Business Rules**:
    - Email must match an existing account
    - Password must match the hashed password in database
    - JWT token expires after 24 hours (configurable)
    - Token includes user_id claim for user-scoped queries

    **FR-002**: System MUST provide user login with email and password authentication
    **FR-003**: System MUST issue JWT tokens upon successful authentication
    """
    # Find user by email
    statement = select(User).where(User.email == request.email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token with user_id claim
    token_data = {
        "sub": str(user.id),
        "email": user.email
    }
    token = create_access_token(token_data)

    # Return auth response
    return AuthResponse(
        user=UserProfile(
            id=user.id,
            email=user.email,
            created_at=user.created_at
        ),
        token=token,
        message="Login successful"
    )
