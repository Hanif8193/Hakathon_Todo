"""Pydantic request/response schemas for Todo application API.

This module defines validation schemas for API endpoints, separate from
database models to allow for different validation rules and response shapes.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# ============================================
# Authentication Schemas
# ============================================

class SignupRequest(BaseModel):
    """Request schema for user signup (POST /api/auth/signup)."""

    email: EmailStr = Field(
        ...,
        description="User email address (must be valid email format)"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (min 8 characters, will be hashed)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }


class LoginRequest(BaseModel):
    """Request schema for user login (POST /api/auth/login)."""

    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }


class UserProfile(BaseModel):
    """Response schema for user profile information."""

    id: int = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "created_at": "2026-01-14T10:30:00Z"
            }
        }


class AuthResponse(BaseModel):
    """Response schema for authentication endpoints (signup/login)."""

    user: UserProfile = Field(..., description="User profile information")
    token: str = Field(..., description="JWT token for authenticated requests")
    message: str = Field(..., description="Success message")

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "created_at": "2026-01-14T10:30:00Z"
                },
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "message": "Login successful"
            }
        }


# ============================================
# Task Schemas
# ============================================

class TaskBase(BaseModel):
    """Base schema for task with common fields."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (required, 1-200 chars)"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Task description (optional, max 2000 chars)"
    )


class CreateTaskRequest(TaskBase):
    """Request schema for creating a task (POST /api/tasks)."""

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for Phase II"
            }
        }


class UpdateTaskRequest(TaskBase):
    """Request schema for updating a task (PUT /api/tasks/{id})."""

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation (updated)",
                "description": "Write comprehensive docs for Phase II with examples"
            }
        }


class TaskResponse(BaseModel):
    """Response schema for task data."""

    id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(..., description="Task completion status")
    user_id: int = Field(..., description="Task owner user ID")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last modification timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for Phase II",
                "completed": False,
                "user_id": 1,
                "created_at": "2026-01-14T10:30:00Z",
                "updated_at": "2026-01-14T10:30:00Z"
            }
        }


class TaskListResponse(BaseModel):
    """Response schema for task list (GET /api/tasks)."""

    tasks: list[TaskResponse] = Field(..., description="List of user's tasks")
    count: int = Field(..., description="Total number of tasks")

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "title": "Complete project documentation",
                        "description": "Write comprehensive docs for Phase II",
                        "completed": False,
                        "user_id": 1,
                        "created_at": "2026-01-14T10:30:00Z",
                        "updated_at": "2026-01-14T10:30:00Z"
                    }
                ],
                "count": 1
            }
        }


# ============================================
# Error Schemas
# ============================================

class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(..., description="User-friendly error message")
    status: int = Field(..., description="HTTP status code")
    details: Optional[dict] = Field(None, description="Additional error context")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid email format",
                "status": 400,
                "details": {
                    "field": "email",
                    "issue": "Email must be a valid email address"
                }
            }
        }
