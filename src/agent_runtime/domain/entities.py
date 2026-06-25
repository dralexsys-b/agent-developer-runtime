"""Domain entities."""

from __future__ import annotations

from dataclasses import dataclass

from agent_runtime.domain.value_objects.ids import AgentId
from agent_runtime.kernel import Timestamp


@dataclass(kw_only=True)
class Agent:
    """Domain entity representing an autonomous agent."""

    id: AgentId
    name: str
    created_at: Timestamp

    def __post_init__(self) -> None:
        """Validate entity fields."""
        if self.name == "":
            raise ValueError("Agent name cannot be empty")

    def rename(self, new_name: str) -> None:
        """Rename the agent.

        Args:
            new_name: New name for the agent.

        Raises:
            ValueError: If new_name is empty.
        """
        if new_name == "":
            raise ValueError("Agent name cannot be empty")
        self.name = new_name
