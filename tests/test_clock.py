"""Unit tests for Clock abstraction."""

from datetime import UTC, datetime, timedelta, timezone, tzinfo

import pytest

from agent_runtime.kernel.clock import Clock, FixedClock, SystemClock


class _BrokenTZInfo(tzinfo):
    """Custom tzinfo where utcoffset() returns None.

    This simulates a broken tzinfo implementation that has tzinfo set
    but cannot provide a valid UTC offset. Inherits from tzinfo (not timezone)
    because datetime.timezone is not an acceptable base type in CPython.
    """

    def utcoffset(self, dt: datetime | None) -> timedelta | None:
        """Return None to simulate broken tzinfo."""
        return None

    def dst(self, dt: datetime | None) -> timedelta | None:
        """Return None for DST offset."""
        return None

    def tzname(self, dt: datetime | None) -> str | None:
        """Return timezone name."""
        return "Broken"


class TestSystemClock:
    """Tests for SystemClock implementation."""

    def test_system_clock_returns_utc_aware_datetime(self) -> None:
        """SystemClock.now() should return a timezone-aware UTC datetime."""
        clock = SystemClock()
        result = clock.now()

        assert result.tzinfo is not None
        assert result.utcoffset() is not None
        assert result.tzinfo == UTC

    def test_system_clock_returns_current_time(self) -> None:
        """SystemClock.now() should return approximately current time."""
        clock = SystemClock()
        before = datetime.now(UTC)
        result = clock.now()
        after = datetime.now(UTC)

        assert before <= result <= after

    def test_system_clock_implements_clock_protocol(self) -> None:
        """SystemClock should implement Clock protocol."""
        clock: Clock = SystemClock()
        assert hasattr(clock, "now")
        assert callable(clock.now)


class TestFixedClock:
    """Tests for FixedClock implementation."""

    def test_fixed_clock_returns_same_time(self) -> None:
        """FixedClock should always return the same timestamp."""
        fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        clock = FixedClock(fixed_time)

        result1 = clock.now()
        result2 = clock.now()

        assert result1 == result2
        assert result1 == fixed_time

    def test_fixed_clock_normalizes_to_utc(self) -> None:
        """FixedClock should normalize input time to UTC."""
        # Create a time in UTC+3 timezone
        plus3 = timezone(timedelta(hours=3))
        local_time = datetime(2024, 1, 1, 15, 0, 0, tzinfo=plus3)  # 15:00 UTC+3

        clock = FixedClock(local_time)
        result = clock.now()

        # Result should be normalized to UTC (15:00 UTC+3 == 12:00 UTC)
        assert result.tzinfo == UTC
        assert result == datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

    def test_fixed_clock_rejects_naive_datetime(self) -> None:
        """FixedClock should reject naive (timezone-unaware) datetime."""
        naive_time = datetime(2024, 1, 1, 12, 0, 0)

        with pytest.raises(ValueError, match="timezone-aware"):
            FixedClock(naive_time)

    def test_fixed_clock_rejects_datetime_with_none_utcoffset(self) -> None:
        """FixedClock should reject datetime where utcoffset() returns None."""
        # Create a datetime with broken tzinfo (tzinfo is set but utcoffset() is None)
        broken_tz = _BrokenTZInfo()
        broken_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=broken_tz)

        with pytest.raises(ValueError, match="timezone-aware"):
            FixedClock(broken_time)

    def test_fixed_clock_implements_clock_protocol(self) -> None:
        """FixedClock should implement Clock protocol."""
        fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        clock: Clock = FixedClock(fixed_time)

        assert hasattr(clock, "now")
        assert callable(clock.now)


class TestClockProtocol:
    """Tests for Clock protocol contract."""

    def test_both_implementations_have_same_interface(self) -> None:
        """SystemClock and FixedClock should have the same interface."""
        system_clock = SystemClock()
        fixed_clock = FixedClock(datetime.now(UTC))

        # Both should have now() method
        assert hasattr(system_clock, "now")
        assert hasattr(fixed_clock, "now")

        # Both should return datetime
        assert isinstance(system_clock.now(), datetime)
        assert isinstance(fixed_clock.now(), datetime)

        # Both should return timezone-aware datetime
        assert system_clock.now().tzinfo is not None
        assert fixed_clock.now().tzinfo is not None
