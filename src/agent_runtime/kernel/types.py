"""Basic type wrappers for Kernel layer.

Provides type-safe wrappers around primitive types to add semantics
and prevent mixing incompatible values.

All timestamp operations use timezone-aware (UTC) datetime objects.
"""

from datetime import UTC, datetime


class Timestamp:
    """Wrapper around datetime to provide type safety.

    Use this instead of raw datetime objects to make it clear
    when a value represents a timestamp in the system.
    All timestamps are timezone-aware (UTC).
    """

    def __init__(self, value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp requires a timezone-aware datetime")
        self._value = value.astimezone(UTC)

    @classmethod
    def now(cls) -> "Timestamp":
        """Create a Timestamp representing the current moment (UTC)."""
        return cls(datetime.now(UTC))

    @classmethod
    def from_datetime(cls, dt: datetime) -> "Timestamp":
        """Create a Timestamp from an existing datetime object.

        Args:
            dt: A timezone-aware datetime object.

        Returns:
            Timestamp normalized to UTC.

        Raises:
            ValueError: If dt is naive (no timezone info).
        """
        return cls(dt)

    def to_datetime(self) -> datetime:
        """Extract the underlying datetime object (UTC)."""
        return self._value

    def __repr__(self) -> str:
        return f"Timestamp({self._value.isoformat()})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Timestamp):
            return False
        return self._value == other._value

    def __lt__(self, other: "Timestamp") -> bool:
        return self._value < other._value

    def __le__(self, other: "Timestamp") -> bool:
        return self._value <= other._value


__all__ = ["Timestamp"]
