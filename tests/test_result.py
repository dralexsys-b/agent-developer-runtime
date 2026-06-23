"""Unit tests for Result type (monadic error handling)."""

from typing import Never

import pytest

from agent_runtime.kernel.result import Result


class CustomError(Exception):
    """Test-only error type for Result tests."""


class TestResultOk:
    """Tests for Result.ok() factory method."""

    def test_unwrap_returns_success_value(self) -> None:
        """unwrap() on ok Result should return the value."""
        result: Result[str, Never] = Result.ok("success")

        assert result.unwrap() == "success"

    def test_ok_unwrap_error_raises(self) -> None:
        """unwrap_error() on ok Result should raise ValueError."""
        result: Result[int, Never] = Result.ok(42)

        with pytest.raises(ValueError, match=r"Called unwrap_error on success Result: 42"):
            result.unwrap_error()


class TestResultError:
    """Tests for Result.error() factory method."""

    def test_unwrap_error_returns_error_value(self) -> None:
        """unwrap_error() on error Result should return the error."""
        result: Result[Never, str] = Result.error("failure")

        assert result.unwrap_error() == "failure"

    def test_error_unwrap_raises(self) -> None:
        """unwrap() on error Result should raise ValueError."""
        result: Result[Never, str] = Result.error("error message")

        with pytest.raises(ValueError, match=r"Called unwrap on error Result: error message"):
            result.unwrap()


class TestResultState:
    """Tests for is_ok() and is_error() methods."""

    def test_ok_state(self) -> None:
        """Ok Result should be ok and not error."""
        result: Result[int, str] = Result.ok(42)

        assert result.is_ok() is True
        assert result.is_error() is False

    def test_error_state(self) -> None:
        """Error Result should be error and not ok."""
        result: Result[int, str] = Result.error("err")

        assert result.is_ok() is False
        assert result.is_error() is True


class TestResultGeneric:
    """Tests for Result with different types."""

    def test_result_with_int_value(self) -> None:
        """Result should work with int values."""
        result: Result[int, str] = Result.ok(42)
        assert result.unwrap() == 42

    def test_result_with_str_error(self) -> None:
        """Result should work with str errors."""
        result: Result[int, str] = Result.error("error")
        assert result.unwrap_error() == "error"

    def test_result_with_dict_value(self) -> None:
        """Result should work with dict values."""
        data: dict[str, str] = {"key": "value"}
        result: Result[dict[str, str], str] = Result.ok(data)
        assert result.unwrap() == data

    def test_result_with_custom_error_type(self) -> None:
        """Result should work with custom error types."""
        err = CustomError("custom")
        result: Result[int, CustomError] = Result.error(err)
        assert result.unwrap_error() is err
