"""Business logic layer for Todo CLI Application.

This module provides high-level operations with validation and error handling.
All operations return structured dictionaries with success status and messages.
"""

try:
    from . import storage
    from .todo import Todo
except ImportError:
    import storage
    from todo import Todo


def add_new_todo(title: str, description: str = "") -> dict:
    """
    Add a new todo with validation.

    Args:
        title: Todo title (must be non-empty after stripping whitespace)
        description: Optional description

    Returns:
        Dictionary with:
            - success (bool): True if todo was added, False otherwise
            - message (str): Success or error message
            - data (Todo | None): The created todo, or None on failure
    """
    # Validate title
    title_stripped = title.strip()
    if not title_stripped:
        return {
            "success": False,
            "message": "Title cannot be empty",
            "data": None
        }

    # Create todo
    todo = storage.add_todo(title_stripped, description)

    return {
        "success": True,
        "message": f"Todo added successfully! (ID: {todo.id})",
        "data": todo
    }


def view_all_todos() -> dict:
    """
    Retrieve all todos.

    Returns:
        Dictionary with:
            - success (bool): Always True
            - data (list[Todo]): List of all todos (empty if none exist)
    """
    todos = storage.get_all_todos()

    return {
        "success": True,
        "data": todos
    }


def update_todo_details(todo_id: int, title: str | None, description: str | None) -> dict:
    """
    Update todo title and/or description.

    Args:
        todo_id: ID of todo to update
        title: New title (None to keep current), must be non-empty if provided
        description: New description (None to keep current)

    Returns:
        Dictionary with:
            - success (bool): True if updated, False otherwise
            - message (str): Success or error message
    """
    # Check if todo exists
    todo = storage.get_todo(todo_id)
    if todo is None:
        return {
            "success": False,
            "message": "Todo ID not found"
        }

    # Validate new title if provided
    if title is not None:
        title_stripped = title.strip()
        if not title_stripped:
            return {
                "success": False,
                "message": "Title cannot be empty"
            }
        # Update with stripped title
        storage.update_todo(todo_id, title=title_stripped)

    # Update description if provided
    if description is not None:
        storage.update_todo(todo_id, description=description)

    return {
        "success": True,
        "message": f"Todo {todo_id} updated successfully!"
    }


def toggle_todo_status(todo_id: int, complete: bool) -> dict:
    """
    Mark todo as complete or incomplete.

    Args:
        todo_id: ID of todo to update
        complete: True to mark complete, False to mark incomplete

    Returns:
        Dictionary with:
            - success (bool): True if updated, False otherwise
            - message (str): Success or error message
    """
    # Check if todo exists
    todo = storage.get_todo(todo_id)
    if todo is None:
        return {
            "success": False,
            "message": "Todo ID not found"
        }

    # Update status
    storage.mark_complete(todo_id, complete)

    status_text = "complete" if complete else "incomplete"
    return {
        "success": True,
        "message": f"Todo {todo_id} marked as {status_text}!"
    }


def remove_todo(todo_id: int) -> dict:
    """
    Delete a todo by ID.

    Args:
        todo_id: ID of todo to delete

    Returns:
        Dictionary with:
            - success (bool): True if deleted, False otherwise
            - message (str): Success or error message
    """
    # Attempt to delete
    success = storage.delete_todo(todo_id)

    if not success:
        return {
            "success": False,
            "message": "Todo ID not found"
        }

    return {
        "success": True,
        "message": f"Todo {todo_id} deleted successfully!"
    }
