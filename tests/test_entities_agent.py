"""Contract tests for Agent entity."""

import pytest

from agent_runtime.domain.entities import Agent
from agent_runtime.domain.value_objects.ids import AgentId
from agent_runtime.kernel import Timestamp

VALID_UUID = "550e8400-e29b-41d4-a716-446655440000"


def test_agent_creation_with_valid_fields() -> None:
    """Agent can be created with valid id, name, and created_at."""
    agent_id = AgentId(value=VALID_UUID)
    created_at = Timestamp.now()

    agent = Agent(
        id=agent_id,
        name="Atlas",
        created_at=created_at,
    )

    assert agent.id == agent_id
    assert agent.name == "Atlas"
    assert agent.created_at == created_at


def test_agent_rejects_empty_name() -> None:
    """Agent name cannot be empty."""
    with pytest.raises(ValueError):
        Agent(
            id=AgentId(value=VALID_UUID),
            name="",
            created_at=Timestamp.now(),
        )


def test_agent_can_be_renamed() -> None:
    """Agent can change its name."""
    agent = Agent(
        id=AgentId(value=VALID_UUID),
        name="Atlas",
        created_at=Timestamp.now(),
    )

    agent.rename("Nova")

    assert agent.name == "Nova"


def test_agent_rejects_empty_name_on_rename() -> None:
    """Agent rename rejects empty name."""
    agent = Agent(
        id=AgentId(value=VALID_UUID),
        name="Atlas",
        created_at=Timestamp.now(),
    )

    with pytest.raises(ValueError):
        agent.rename("")


def test_agent_has_empty_event_queue_initially() -> None:
    """New agent has an empty event queue."""
    agent = Agent(
        id=AgentId(value=VALID_UUID),
        name="Atlas",
        created_at=Timestamp.now(),
    )

    assert agent.pull_events() == []


def test_agent_rename_emits_agent_renamed_event() -> None:
    """Agent.rename() emits AgentRenamed event with old and new names."""
    from agent_runtime.domain.events import AgentRenamed

    agent = Agent(
        id=AgentId(value=VALID_UUID),
        name="Atlas",
        created_at=Timestamp.now(),
    )

    agent.rename("Nova")

    events = agent.pull_events()

    assert len(events) == 1
    event = events[0]
    assert isinstance(event, AgentRenamed)
    assert event.agent_id == agent.id
    assert event.old_name == "Atlas"
    assert event.new_name == "Nova"
    assert event.event_type == "AgentRenamed"


def test_pull_events_clears_event_queue() -> None:
    """pull_events() returns events once and clears the queue."""
    agent = Agent(
        id=AgentId(value=VALID_UUID),
        name="Atlas",
        created_at=Timestamp.now(),
    )

    agent.rename("Nova")

    first = agent.pull_events()
    second = agent.pull_events()

    assert len(first) == 1
    assert second == []
