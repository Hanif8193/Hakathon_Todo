"""In-memory storage layer for Todo CLI Application.

This module provides CRUD operations for todos using an in-memory dictionary.
All data is lost when the application exits (Phase I design requirement).
"""

from typing import Optional
try:
    from .todo import Todo
except ImportError:
    from todo import Todo


# Global storage: dictionary mapping todo IDs to Todo objects
todos: dict[int, Todo] = {}

# Global ID counter: auto-increments for each new todo
next_id: int = 1


def add_todo(title: str, description: str = "") -> Todo:
    """
    Create and store a new todo with auto-generated ID.

    Args:
        title: Todo title (required, should be non-empty)
        description: Optional description (defaults to empty string)

    Returns:
        The created Todo object with assigned ID
    """
    global next_id

    todo = Todo(
        id=next_id,
        title=title,
        description=description,
        completed=False
    )

    todos[next_id] = todo
    next_id += 1

    return todo


def get_todo(todo_id: int) -> Optional[Todo]:
    """
    Retrieve a todo by ID.

    Args:
        todo_id: The unique identifier of the todo

    Returns:
        The Todo object if found, None otherwise
    """
    return todos.get(todo_id)


def get_all_todos() -> list[Todo]:
    """
    Retrieve all todos.

    Returns:
        List of all Todo objects (empty list if no todos exist)
    """
    return list(todos.values())


def update_todo(todo_id: int, **kwargs) -> bool:
    """
    Update fields of an existing todo.

    Args:
        todo_id: The unique identifier of the todo to update
        **kwargs: Fields to update (title, description, completed)

    Returns:
        True if todo was found and updated, False otherwise
    """
    todo = todos.get(todo_id)

    if todo is None:
        return False

    # Update only provided fields
    if 'title' in kwargs:
        todo.title = kwargs['title']
    if 'description' in kwargs:
        todo.description = kwargs['description']
    if 'completed' in kwargs:
        todo.completed = kwargs['completed']

    return True


def delete_todo(todo_id: int) -> bool:
    """
    Delete a todo by ID.

    Args:
        todo_id: The unique identifier of the todo to delete

    Returns:
        True if todo was found and deleted, False otherwise
    """
    if todo_id in todos:
        del todos[todo_id]
        return True
    return False


def mark_complete(todo_id: int, completed: bool) -> bool:
    """
    Mark a todo as complete or incomplete.

    Args:
        todo_id: The unique identifier of the todo
        completed: True to mark complete, False to mark incomplete

    Returns:
        True if todo was found and status updated, False otherwise
    """
    todo = todos.get(todo_id)

    if todo is None:
        return False

    todo.completed = completed
    return True
