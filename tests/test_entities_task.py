"""Contract tests for Task entity."""

import pytest

from agent_runtime.domain.entities import Task
from agent_runtime.domain.events import TaskStarted, TaskTitleChanged
from agent_runtime.domain.value_objects.ids import TaskId
from agent_runtime.domain.value_objects.status import TaskStatus
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


def test_task_can_change_title() -> None:
    """Task can change its title."""
    task = Task(
        id=TaskId(value=VALID_UUID),
        title="Old Title",
        created_at=Timestamp.now(),
    )

    task.change_title("New Title")

    assert task.title == "New Title"


def test_task_rejects_empty_title_on_change() -> None:
    """Task rejects empty title on change."""
    task = Task(
        id=TaskId(value=VALID_UUID),
        title="Old Title",
        created_at=Timestamp.now(),
    )

    with pytest.raises(ValueError):
        task.change_title("")


def test_task_change_title_emits_task_title_changed_event() -> None:
    """Task.change_title() emits TaskTitleChanged event with old and new titles."""
    task = Task(
        id=TaskId(value=VALID_UUID),
        title="Old Title",
        created_at=Timestamp.now(),
    )

    task.change_title("New Title")

    events = task.pull_events()

    assert len(events) == 1

    event = events[0]

    assert isinstance(event, TaskTitleChanged)
    assert event.task_id == task.id
    assert event.old_title == "Old Title"
    assert event.new_title == "New Title"
    assert event.event_type == "TaskTitleChanged"


def test_task_can_start() -> None:
    """Task can be started."""
    task = Task(
        id=TaskId(value=VALID_UUID),
        title="Implement feature",
        created_at=Timestamp.now(),
    )

    task.start()


def test_task_start_changes_status() -> None:
    """Starting a task moves it to IN_PROGRESS."""

    task = Task(
        id=TaskId(value=VALID_UUID),
        title="Implement feature",
        created_at=Timestamp.now(),
    )

    task.start()

    assert task.status == TaskStatus.IN_PROGRESS


def test_task_is_pending_after_creation() -> None:
    """Newly created task has PENDING status."""
    task = Task(
        id=TaskId(value=VALID_UUID),
        title="Implement feature",
        created_at=Timestamp.now(),
    )

    assert task.status == TaskStatus.PENDING


def test_task_start_emits_task_started_event() -> None:
    """Starting a task publishes TaskStarted event."""
    task = Task(
        id=TaskId(value=VALID_UUID),
        title="Implement feature",
        created_at=Timestamp.now(),
    )

    task.start()

    events = task.pull_events()

    assert len(events) == 1

    event = events[0]

    assert isinstance(event, TaskStarted)
    assert event.task_id == task.id
    assert event.event_type == "TaskStarted"
