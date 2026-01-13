"""Todo entity dataclass for Phase I Todo CLI Application."""

from dataclasses import dataclass


@dataclass
class Todo:
    """
    Represents a single todo item.

    Attributes:
        id: Unique identifier (auto-generated, positive integer)
        title: Todo title (required, non-empty string)
        description: Optional description (defaults to empty string)
        completed: Completion status (defaults to False)
    """
    id: int
    title: str
    description: str = ""
    completed: bool = False
