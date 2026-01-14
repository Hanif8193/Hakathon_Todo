"""Tasks router for task CRUD endpoints.

This module provides task management endpoints for authenticated users.
All endpoints require JWT authentication and enforce user data isolation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime

from backend.dependencies import get_session, get_current_user
from backend.models import User, Task
from backend.schemas import (
    TaskListResponse,
    TaskResponse,
    CreateTaskRequest,
    UpdateTaskRequest,
    ErrorResponse
)

router = APIRouter()


@router.get(
    "",
    response_model=TaskListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def list_tasks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get all tasks for authenticated user.

    Returns tasks ordered by creation date (newest first).
    Only returns tasks owned by the authenticated user (user data isolation).

    **FR-012**: System MUST allow authenticated users to view all their tasks (user-scoped)
    **FR-016**: System MUST prevent users from accessing or modifying other users' tasks
    """
    # Query tasks filtered by authenticated user_id
    statement = select(Task).where(
        Task.user_id == current_user.id
    ).order_by(
        Task.created_at.desc()
    )

    result = await session.execute(statement)
    tasks = result.scalars().all()

    # Convert to response schema
    task_responses = [
        TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in tasks
    ]

    return TaskListResponse(
        tasks=task_responses,
        count=len(task_responses)
    )


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def create_task(
    task_data: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Create a new task for authenticated user.

    Title is required (1-200 characters), description is optional (max 2000 characters).
    New tasks default to completed=False.

    **FR-013**: System MUST allow authenticated users to create new tasks
    **FR-010**: System MUST validate title is required and under 200 characters
    """
    # Validate title is not empty after stripping whitespace
    if not task_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    # Create new task with authenticated user_id
    new_task = Task(
        title=task_data.title.strip(),
        description=task_data.description.strip() if task_data.description else None,
        user_id=current_user.id,
        completed=False  # Default to incomplete
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return TaskResponse(
        id=new_task.id,
        title=new_task.title,
        description=new_task.description,
        completed=new_task.completed,
        user_id=new_task.user_id,
        created_at=new_task.created_at,
        updated_at=new_task.updated_at
    )


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Task not found"}
    }
)
async def update_task(
    task_id: int,
    task_data: UpdateTaskRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Update task details (title, description, or completion status).

    Only the task owner can update their tasks.
    Updates the updated_at timestamp automatically.

    **FR-014**: System MUST allow authenticated users to edit their tasks
    **FR-016**: System MUST prevent users from accessing or modifying other users' tasks
    """
    # Get task and verify ownership
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Validate title if provided
    if task_data.title is not None:
        trimmed_title = task_data.title.strip()
        if not trimmed_title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty"
            )
        task.title = trimmed_title

    # Update description if provided
    if task_data.description is not None:
        task.description = task_data.description.strip() if task_data.description else None

    # Update completion status if provided
    if task_data.completed is not None:
        task.completed = task_data.completed

    # Refresh updated_at timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Task not found"}
    }
)
async def toggle_task_completion(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Toggle task completion status (completed true <-> false).

    Only the task owner can toggle their tasks.
    Updates the updated_at timestamp automatically.

    **FR-015**: System MUST allow authenticated users to mark tasks as complete/incomplete
    **FR-016**: System MUST prevent users from accessing or modifying other users' tasks
    """
    # Get task and verify ownership
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle completion status
    task.completed = not task.completed

    # Refresh updated_at timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Task not found"}
    }
)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Delete a task permanently.

    Only the task owner can delete their tasks.

    **FR-016**: System MUST prevent users from accessing or modifying other users' tasks
    **US6**: User Story 6 - Delete Tasks
    """
    # Get task and verify ownership
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id
    )
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Delete the task
    await session.delete(task)
    await session.commit()

    # Return 204 No Content (no response body)
    return None
