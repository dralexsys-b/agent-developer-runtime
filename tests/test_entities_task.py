"""Contract tests for Task entity."""

import pytest

from agent_runtime.domain.entities import Task
from agent_runtime.domain.value_objects.ids import TaskId
from agent_runtime.kernel import Timestamp

VALID_UUID = "550e8400-e29b-41d4-a716-446655440000"


def test_task_creation_with_valid_fields() -> None:
    """Task can be created with valid id, title, and created_at."""
    task_id = TaskId(value=VALID_UUID)
    created_at = Timestamp.now()

    task = Task(
        id=task_id,
        title="Implement feature",
        created_at=created_at,
    )

    assert task.id == task_id
    assert task.title == "Implement feature"
    assert task.created_at == created_at


def test_task_rejects_empty_title() -> None:
    """Task title cannot be empty."""
    with pytest.raises(ValueError):
        Task(
            id=TaskId(value=VALID_UUID),
            title="",
            created_at=Timestamp.now(),
        )


def test_task_has_empty_event_queue_initially() -> None:
    """New task has an empty event queue."""
    task = Task(
        id=TaskId(value=VALID_UUID),
        title="Implement feature",
        created_at=Timestamp.now(),
    )

    assert task.pull_events() == []
