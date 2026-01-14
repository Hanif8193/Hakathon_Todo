"""Authentication utilities for JWT token generation and password hashing.

This module provides JWT token creation/validation and bcrypt password hashing
functions for secure user authentication.
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# Get secret from environment variable (REQUIRED)
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")

if not SECRET_KEY:
    raise ValueError(
        "BETTER_AUTH_SECRET environment variable is not set. "
        "Please set it in .env file (minimum 32 characters)"
    )

if len(SECRET_KEY) < 32:
    raise ValueError(
        "BETTER_AUTH_SECRET must be at least 32 characters long. "
        f"Current length: {len(SECRET_KEY)}"
    )

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Password hashing configuration (bcrypt with work factor 12)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hashed password string (format: $2b$12$...)

    Example:
        >>> hashed = hash_password("SecurePass123")
        >>> print(hashed)
        $2b$12$...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password from database

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("SecurePass123")
        >>> verify_password("SecurePass123", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.

    Args:
        data: Dictionary of claims to encode in token (e.g., {"sub": "user_id", "email": "user@example.com"})
        expires_delta: Optional custom expiration time (defaults to 24 hours)

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token({"sub": "1", "email": "user@example.com"})
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    to_encode = data.copy()

    # Set expiration time (default 24 hours)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    # Encode JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token.

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary of token claims if valid, None if invalid/expired

    Example:
        >>> token = create_access_token({"sub": "1", "email": "user@example.com"})
        >>> payload = decode_access_token(token)
        >>> print(payload)
        {'sub': '1', 'email': 'user@example.com', 'exp': ..., 'iat': ...}
        >>> decode_access_token("invalid_token")
        None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def extract_user_id_from_token(token: str) -> Optional[int]:
    """Extract user_id from JWT token.

    Args:
        token: JWT token string

    Returns:
        User ID as integer if token is valid, None otherwise

    Example:
        >>> token = create_access_token({"sub": "123", "email": "user@example.com"})
        >>> extract_user_id_from_token(token)
        123
        >>> extract_user_id_from_token("invalid_token")
        None
    """
    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None

    try:
        return int(user_id_str)
    except (ValueError, TypeError):
        return None
