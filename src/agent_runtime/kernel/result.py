"""Result type for explicit error handling.

Implements the Result[T, E] pattern to avoid exceptions in business logic.
Use this when you want to handle errors explicitly rather than using try/except.

Example:
    def divide(a: int, b: int) -> Result[int, str]:
        if b == 0:
            return Result.error("Division by zero")
        return Result.ok(a // b)

    result = divide(10, 2)
    if result.is_ok():
        print(result.unwrap())  # 5
"""

from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


class Result(Generic[T, E]):
    """Container for either a success value or an error value."""

    def __init__(self, value: T | None, error: E | None) -> None:
        self._value = value
        self._error = error

    @classmethod
    def ok(cls, value: T) -> "Result[T, E]":
        """Create a successful Result."""
        return cls(value=value, error=None)

    @classmethod
    def error(cls, error: E) -> "Result[T, E]":
        """Create a failed Result."""
        return cls(value=None, error=error)

    def is_ok(self) -> bool:
        """Check if this Result contains a success value."""
        return self._error is None

    def is_error(self) -> bool:
        """Check if this Result contains an error value."""
        return self._error is not None

    def unwrap(self) -> T:
        """Get the success value, or raise if this is an error Result.

        Raises:
            ValueError: If this Result contains an error.
        """
        if self._error is not None:
            raise ValueError(f"Called unwrap on error Result: {self._error}")
        if self._value is None:
            raise ValueError("Result contains neither value nor error")
        return self._value

    def unwrap_error(self) -> E:
        """Get the error value, or raise if this is a success Result.

        Raises:
            ValueError: If this Result contains a success value.
        """
        if self._value is not None:
            raise ValueError(f"Called unwrap_error on success Result: {self._value}")
        if self._error is None:
            raise ValueError("Result contains neither value nor error")
        return self._error


__all__ = ["Result"]
