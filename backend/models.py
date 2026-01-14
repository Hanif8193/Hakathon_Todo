"""SQLModel database models for Todo application.

This module defines the User and Task entities with their relationships,
constraints, and database schema per data-model.md specification.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List


class User(SQLModel, table=True):
    """User account with authentication credentials.

    Represents an authenticated user with email-based login.
    Password is stored as bcrypt hash, never plaintext.
    """

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing primary key"
    )

    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User email address (unique identifier for login)"
    )

    password_hash: str = Field(
        max_length=255,
        description="Bcrypt hashed password (never store plaintext)"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp (UTC)"
    )

    # Relationships
    tasks: List["Task"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Task(SQLModel, table=True):
    """Todo task owned by a user.

    Represents a task item with title, optional description, and completion status.
    Each task belongs to exactly one user (enforced by foreign key).
    """

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing primary key"
    )

    title: str = Field(
        max_length=200,
        description="Task title (required, max 200 chars)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Task description (optional, max 2000 chars)"
    )

    completed: bool = Field(
        default=False,
        description="Task completion status (default: incomplete)"
    )

    user_id: int = Field(
        foreign_key="user.id",
        index=True,
        description="Owner user ID (foreign key to user.id)"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task last modification timestamp (UTC)"
    )

    # Relationships
    owner: User = Relationship(back_populates="tasks")
