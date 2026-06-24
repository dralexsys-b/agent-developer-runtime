"""Typed identifiers for domain entities."""

from __future__ import annotations

from dataclasses import dataclass

from agent_runtime.kernel import generate_id, validate_id


@dataclass(frozen=True, slots=True, kw_only=True)
class AgentId:
    """Typed identifier for Agent entities."""

    value: str

    def __post_init__(self) -> None:
        """Validate and normalize the UUID string."""
        object.__setattr__(self, "value", validate_id(self.value))

    def __str__(self) -> str:
        """Return canonical value for logging, serialization, CLI."""
        return self.value

    @classmethod
    def new(cls) -> AgentId:
        """Create a new AgentId with a generated UUID."""
        return cls(value=generate_id())


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskId:
    """Typed identifier for Task entities."""

    value: str

    def __post_init__(self) -> None:
        """Validate and normalize the UUID string."""
        object.__setattr__(self, "value", validate_id(self.value))

    def __str__(self) -> str:
        """Return canonical value for logging, serialization, CLI."""
        return self.value

    @classmethod
    def new(cls) -> TaskId:
        """Create a new TaskId with a generated UUID."""
        return cls(value=generate_id())
