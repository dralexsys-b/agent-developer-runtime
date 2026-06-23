"""Unit tests for Timestamp wrapper."""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from agent_runtime.kernel.types import Timestamp


class TestTimestampConstructor:
    """Tests for Timestamp constructor."""

    def test_constructor_accepts_utc_aware_datetime(self) -> None:
        """Timestamp should accept timezone-aware UTC datetime."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        ts = Timestamp(dt)
        assert ts.to_datetime() == dt

    def test_constructor_normalizes_to_utc(self) -> None:
        """Timestamp should normalize input datetime to UTC."""
        plus3 = timezone(timedelta(hours=3))
        local_dt = datetime(2024, 1, 1, 15, 0, 0, tzinfo=plus3)

        ts = Timestamp(local_dt)
        result = ts.to_datetime()

        assert result.tzinfo == UTC
        assert result == datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

    def test_constructor_rejects_naive_datetime(self) -> None:
        """Timestamp should reject naive (timezone-unaware) datetime."""
        naive_dt = datetime(2024, 1, 1, 12, 0, 0)

        with pytest.raises(ValueError, match="timezone-aware"):
            Timestamp(naive_dt)


class TestTimestampNow:
    """Tests for Timestamp.now() factory method."""

    def test_now_returns_timestamp(self) -> None:
        """Timestamp.now() should return a Timestamp instance."""
        ts = Timestamp.now()
        assert isinstance(ts, Timestamp)

    def test_now_returns_utc_aware_datetime(self) -> None:
        """Timestamp.now() should return UTC-aware datetime."""
        ts = Timestamp.now()
        dt = ts.to_datetime()

        assert dt.tzinfo is not None
        assert dt.tzinfo == UTC

    def test_now_returns_current_time(self) -> None:
        """Timestamp.now() should return approximately current time."""
        before = datetime.now(UTC)
        ts = Timestamp.now()
        after = datetime.now(UTC)

        result = ts.to_datetime()
        assert before <= result <= after


class TestTimestampFromDatetime:
    """Tests for Timestamp.from_datetime() factory method."""

    def test_from_datetime_accepts_utc_aware(self) -> None:
        """from_datetime() should accept timezone-aware datetime."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        ts = Timestamp.from_datetime(dt)

        assert ts.to_datetime() == dt

    def test_from_datetime_normalizes_to_utc(self) -> None:
        """from_datetime() should normalize to UTC."""
        plus3 = timezone(timedelta(hours=3))
        local_dt = datetime(2024, 1, 1, 15, 0, 0, tzinfo=plus3)

        ts = Timestamp.from_datetime(local_dt)
        result = ts.to_datetime()

        assert result.tzinfo == UTC
        assert result == datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

    def test_from_datetime_rejects_naive(self) -> None:
        """from_datetime() should reject naive datetime."""
        naive_dt = datetime(2024, 1, 1, 12, 0, 0)

        with pytest.raises(ValueError, match="timezone-aware"):
            Timestamp.from_datetime(naive_dt)


class TestTimestampToDatetime:
    """Tests for Timestamp.to_datetime() method."""

    def test_to_datetime_returns_datetime(self) -> None:
        """to_datetime() should return a datetime instance."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        ts = Timestamp(dt)

        result = ts.to_datetime()

        assert isinstance(result, datetime)

    def test_to_datetime_returns_utc_datetime(self) -> None:
        """to_datetime() should return UTC-aware datetime."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        ts = Timestamp(dt)

        result = ts.to_datetime()

        assert result.tzinfo == UTC
        assert result == dt


class TestTimestampComparisons:
    """Tests for Timestamp comparison operators."""

    def test_equality_same_value(self) -> None:
        """Two Timestamps with same value should be equal."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        ts1 = Timestamp(dt)
        ts2 = Timestamp(dt)

        assert ts1 == ts2

    def test_equality_different_timezone_same_instant(self) -> None:
        """Two Timestamps representing same instant should be equal."""
        utc_dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        plus3 = timezone(timedelta(hours=3))
        local_dt = datetime(2024, 1, 1, 15, 0, 0, tzinfo=plus3)

        ts1 = Timestamp(utc_dt)
        ts2 = Timestamp(local_dt)

        assert ts1 == ts2

    def test_inequality_different_value(self) -> None:
        """Two Timestamps with different values should not be equal."""
        dt1 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        dt2 = datetime(2024, 1, 1, 13, 0, 0, tzinfo=UTC)

        ts1 = Timestamp(dt1)
        ts2 = Timestamp(dt2)

        assert ts1 != ts2

    def test_equality_with_non_timestamp(self) -> None:
        """Timestamp should not be equal to non-Timestamp objects."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        ts = Timestamp(dt)

        assert ts != dt
        assert ts != "2024-01-01T12:00:00"
        assert ts != 42

    def test_less_than(self) -> None:
        """Earlier timestamp should be less than later timestamp."""
        dt1 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        dt2 = datetime(2024, 1, 1, 13, 0, 0, tzinfo=UTC)

        ts1 = Timestamp(dt1)
        ts2 = Timestamp(dt2)

        assert ts1 < ts2
        assert not ts2 < ts1

    def test_less_than_or_equal(self) -> None:
        """Less than or equal should work correctly."""
        dt1 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        dt2 = datetime(2024, 1, 1, 13, 0, 0, tzinfo=UTC)

        ts1 = Timestamp(dt1)
        ts2 = Timestamp(dt2)
        ts3 = Timestamp(dt1)

        assert ts1 <= ts2
        assert ts1 <= ts3
        assert not ts2 <= ts1


class TestTimestampRepr:
    """Tests for Timestamp string representation."""

    def test_repr_exact_format(self) -> None:
        """__repr__ should return exact format with ISO datetime."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        ts = Timestamp(dt)

        assert repr(ts) == "Timestamp(2024-01-01T12:00:00+00:00)"
