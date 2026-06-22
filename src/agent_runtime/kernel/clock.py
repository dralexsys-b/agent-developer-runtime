"""Clock abstraction for time operations.

Provides a pluggable clock interface to avoid direct dependency on
system time in business logic. This enables deterministic testing
and time manipulation.

All timestamps are timezone-aware (UTC).
"""

from datetime import UTC, datetime
from typing import Protocol


class Clock(Protocol):
    """Protocol for clock implementations."""

    def now(self) -> datetime:
        """Return current timestamp."""
        ...


class SystemClock:
    """Default clock implementation using system time."""

    def now(self) -> datetime:
        """Return current UTC timestamp from system clock."""
        return datetime.now(UTC)


class FixedClock:
    """Clock that always returns the same timestamp. Useful for testing."""

    def __init__(self, fixed_time: datetime) -> None:
        if fixed_time.tzinfo is None or fixed_time.utcoffset() is None:
            raise ValueError("FixedClock requires a timezone-aware datetime")
        self._fixed_time = fixed_time.astimezone(UTC)

    def now(self) -> datetime:
        """Return the fixed timestamp."""
        return self._fixed_time


__all__ = ["Clock", "SystemClock", "FixedClock"]
