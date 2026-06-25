"""Agent domain events."""

from __future__ import annotations

from dataclasses import dataclass

from agent_runtime.domain.events.base import DomainEvent
from agent_runtime.domain.value_objects.ids import AgentId


@dataclass(frozen=True, slots=True, kw_only=True)
class AgentRenamed(DomainEvent):
    """Emitted when an agent's name is changed.

    Attributes:
        agent_id: The ID of the agent that was renamed.
        old_name: The previous name of the agent.
        new_name: The new name of the agent.
    """

    agent_id: AgentId
    old_name: str
    new_name: str


__all__ = ["AgentRenamed"]
