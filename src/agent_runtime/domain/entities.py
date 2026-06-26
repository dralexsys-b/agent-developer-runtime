"""Domain entities."""

from __future__ import annotations

from dataclasses import dataclass

from agent_runtime.domain.aggregate_root import AggregateRoot
from agent_runtime.domain.events import AgentRenamed, TaskStarted, TaskTitleChanged
from agent_runtime.domain.value_objects.ids import AgentId, TaskId
from agent_runtime.domain.value_objects.status import TaskStatus
from agent_runtime.kernel import Timestamp


@dataclass(kw_only=True)
class Agent(AggregateRoot):
    """Domain entity representing an autonomous agent."""

    id: AgentId
    name: str
    created_at: Timestamp

    def __post_init__(self) -> None:
        """Validate entity fields."""
        if self.name == "":
            raise ValueError("Agent name cannot be empty")

    def rename(self, new_name: str) -> None:
        """Rename the agent.

        Args:
            new_name: New name for the agent.

        Raises:
            ValueError: If new_name is empty.
        """
        if new_name == "":
            raise ValueError("Agent name cannot be empty")

        old_name = self.name
        self.name = new_name

        self._record_event(
            AgentRenamed(
                agent_id=self.id,
                old_name=old_name,
                new_name=new_name,
            )
        )

@dataclass(kw_only=True)
class Task(AggregateRoot):
    """Domain entity representing a task."""

    id: TaskId
    title: str
    created_at: Timestamp
    status: TaskStatus = TaskStatus.PENDING

    def __post_init__(self) -> None:
        """Validate entity fields."""
        if self.title == "":
            raise ValueError("Task title cannot be empty")


    def change_title(self, title: str) -> None:
        """Change the task title.

        Args:
            title: New title for the task.

        Raises:
            ValueError: If title is empty.
        """
        if title == "":
            raise ValueError("Task title cannot be empty")

        old_title = self.title
        self.title = title

        self._record_event(
            TaskTitleChanged(
                task_id=self.id,
                old_title=old_title,
                new_title=title,
            )
        )

    def start(self) -> None:
        """Start the task."""
        self.status = TaskStatus.IN_PROGRESS

        self._record_event(
            TaskStarted(
                task_id=self.id,
            )
        )
