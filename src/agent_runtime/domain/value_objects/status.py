"""Task status value object."""

from enum import StrEnum, auto


class TaskStatus(StrEnum):
    """Status of a task in its lifecycle."""

    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
