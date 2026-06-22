"""Kernel layer — foundational primitives for all layers.

Kernel provides types and utilities used by Domain, Application,
Runtime, and Contracts layers. Kernel never imports from any
other layer.
"""

from agent_runtime.kernel.clock import Clock, FixedClock, SystemClock
from agent_runtime.kernel.errors import InvalidIDError, KernelError, TimestampError
from agent_runtime.kernel.ids import generate_id, validate_id
from agent_runtime.kernel.result import Result
from agent_runtime.kernel.types import Timestamp

__all__ = [
    "Clock",
    "FixedClock",
    "InvalidIDError",
    "KernelError",
    "Result",
    "SystemClock",
    "Timestamp",
    "TimestampError",
    "generate_id",
    "validate_id",
]
