"""Base domain event class.

This module provides the foundational DomainEvent class that serves as
the base for all domain events in the system.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agent_runtime.kernel import Timestamp, generate_id


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent:
    """Base class for all domain events.

    Domain events represent facts about things that happened in the domain.
    They are immutable value objects that capture information about past occurrences.

    Concrete domain events inherit from this class.

    Attributes:
        occurred_at: When the event occurred in the domain.
        event_id: Technical identifier for this event instance (UUID).

    Note:
        The event_type property automatically returns the concrete class name,
        enabling polymorphic event handling without manual type specification.
    """

    occurred_at: Timestamp = field(default_factory=Timestamp.now)
    event_id: str = field(default_factory=generate_id)

    @property
    def event_type(self) -> str:
        """Returns the concrete event class name.

        This property enables automatic event type detection without
        requiring manual specification in subclasses.
        """
        return self.__class__.__name__


__all__ = ["DomainEvent"]
