"""Domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field

from agent_runtime.domain.events import AgentRenamed, DomainEvent
from agent_runtime.domain.value_objects.ids import AgentId, TaskId
from agent_runtime.kernel import Timestamp


@dataclass(kw_only=True)
class Agent:
    """Domain entity representing an autonomous agent."""

    id: AgentId
    name: str
    created_at: Timestamp

    _events: list[DomainEvent] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

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

    def _record_event(self, event: DomainEvent) -> None:
        """Record a domain event for later retrieval."""
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        """Extract and return all pending domain events."""
        events = self._events.copy()
        self._events.clear()
        return events


@dataclass(kw_only=True)
class Task:
    """Domain entity representing a task."""

    id: TaskId
    title: str
    created_at: Timestamp

    _events: list[DomainEvent] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        """Validate entity fields."""
        if self.title == "":
            raise ValueError("Task title cannot be empty")

    def _record_event(self, event: DomainEvent) -> None:
        """Record a domain event for later retrieval."""
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        """Extract and return all pending domain events."""
        events = self._events.copy()
        self._events.clear()
        return events
