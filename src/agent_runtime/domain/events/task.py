"""Task domain events."""

from __future__ import annotations

from dataclasses import dataclass

from agent_runtime.domain.events.base import DomainEvent
from agent_runtime.domain.value_objects.ids import TaskId


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskTitleChanged(DomainEvent):
    """Emitted when a task's title is changed.

    Attributes:
        task_id: The ID of the task whose title was changed.
        old_title: The previous title of the task.
        new_title: The new title of the task.
    """

    task_id: TaskId
    old_title: str
    new_title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskStarted(DomainEvent):
    """Emitted when a task transitions to IN_PROGRESS status.

    Attributes:
        task_id: The ID of the task that was started.
    """

    task_id: TaskId


__all__ = [
    "TaskStarted",
    "TaskTitleChanged",
]
