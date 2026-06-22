"""Base exception classes for Kernel layer.

These exceptions are used by Kernel and may be inherited by
Domain layer exceptions. They represent infrastructure-level
errors that can occur anywhere in the system.
"""


class KernelError(Exception):
    """Base exception for all Kernel errors."""


class InvalidIDError(KernelError):
    """Raised when an identifier is invalid."""


class TimestampError(KernelError):
    """Raised when timestamp validation fails."""


__all__ = ["KernelError", "InvalidIDError", "TimestampError"]
