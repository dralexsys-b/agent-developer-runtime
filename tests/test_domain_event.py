"""Contract tests for DomainEvent base class."""

from dataclasses import FrozenInstanceError, dataclass
from datetime import UTC, datetime
from typing import Any, cast, final

import pytest

from agent_runtime.domain.events import DomainEvent
from agent_runtime.kernel import Timestamp, validate_id


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class SampleEvent(DomainEvent):
    """Concrete test event for testing DomainEvent contract."""
    pass


class TestEventCreation:
    """DomainEvent must auto-generate event_id and occurred_at."""

    def test_auto_generates_non_empty_valid_uuid(self) -> None:
        """event_id is a non-empty valid UUID when not provided."""
        event = SampleEvent()
        assert event.event_id
        assert validate_id(event.event_id) == event.event_id

    def test_accepts_explicit_occurred_at(self) -> None:
        """Can provide explicit occurred_at timestamp."""
        fixed_dt = datetime(2026, 6, 23, 10, 0, 0, tzinfo=UTC)
        explicit_time = Timestamp.from_datetime(fixed_dt)
        event = SampleEvent(occurred_at=explicit_time)
        assert event.occurred_at == explicit_time


class TestEventType:
    """event_type must be a computed property returning the class name."""

    def test_returns_concrete_class_name(self) -> None:
        """event_type returns the concrete subclass name."""
        event = SampleEvent()
        assert event.event_type == "SampleEvent"


class TestEventImmutability:
    """DomainEvent must be immutable (frozen=True)."""

    def test_cannot_modify_fields(self) -> None:
        """Attempting to modify fields raises FrozenInstanceError."""
        event = SampleEvent()
        with pytest.raises(FrozenInstanceError):
            event.event_id = "another"  # type: ignore[misc]


class TestEventKeywordOnly:
    """DomainEvent must enforce keyword-only arguments."""

    def test_rejects_positional_arguments(self) -> None:
        """Positional arguments raise TypeError."""
        ctor = cast(Any, SampleEvent)
        with pytest.raises(TypeError):
            ctor(Timestamp.now())
