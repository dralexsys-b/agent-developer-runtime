"""Aggregate root base class for domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field

from agent_runtime.domain.events import DomainEvent


@dataclass(kw_only=True)
class AggregateRoot:
    """Base class for aggregate roots that emit domain events."""

    _events: list[DomainEvent] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    def _record_event(self, event: DomainEvent) -> None:
        """Record a domain event for later retrieval."""
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        """Extract and return all pending domain events."""
        events = self._events.copy()
        self._events.clear()
        return events
