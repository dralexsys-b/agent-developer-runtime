"""Domain events - facts about things that happened in the domain."""

from .agent import AgentRenamed
from .base import DomainEvent

__all__ = [
    "AgentRenamed",
    "DomainEvent",
]
