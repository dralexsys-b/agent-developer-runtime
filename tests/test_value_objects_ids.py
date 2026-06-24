"""Contract tests for Identity Types (AgentId, TaskId)."""

from dataclasses import FrozenInstanceError
from typing import Any, cast

import pytest

from agent_runtime.domain.value_objects.ids import AgentId, TaskId
from agent_runtime.kernel import InvalidIDError, validate_id

VALID_UUID = "550e8400-e29b-41d4-a716-446655440000"
INVALID_UUID = "not-a-valid-uuid"
VALID_UUID_UPPER = VALID_UUID.upper()


class TestIdentityCreation:
    """Tests for creating new identity objects."""

    def test_constructor_with_valid_string_creates_object(self) -> None:
        """Constructor with valid UUID string creates an identity object."""
        agent_id = AgentId(value=VALID_UUID)
        assert agent_id.value == VALID_UUID

    def test_new_returns_agent_id(self) -> None:
        """AgentId.new() returns an AgentId instance."""
        agent_id = AgentId.new()
        assert isinstance(agent_id, AgentId)

    def test_new_returns_valid_identity_object(self) -> None:
        """AgentId.new() returns a valid identity that can be used."""
        agent_id = AgentId.new()
        assert validate_id(agent_id.value) == agent_id.value
        assert str(agent_id) == agent_id.value

    def test_new_returns_distinct_values(self) -> None:
        """Two independently created AgentId instances should normally be distinct."""
        first = AgentId.new()
        second = AgentId.new()
        assert first != second


class TestIdentityValidation:
    """Tests for validation behavior during construction."""

    def test_constructor_with_invalid_string_raises_invalid_id_error(self) -> None:
        """Constructor with invalid string raises InvalidIDError."""
        with pytest.raises(InvalidIDError):
            AgentId(value=INVALID_UUID)


class TestIdentityCanonicalization:
    """Tests for UUID canonicalization behavior."""

    def test_canonicalization_uppercase_to_lowercase(self) -> None:
        """Uppercase UUID is normalized to lowercase in .value."""
        agent_id = AgentId(value=VALID_UUID_UPPER)
        assert agent_id.value == VALID_UUID

    def test_empty_string_raises_invalid_id_error(self) -> None:
        """Constructor with empty string raises InvalidIDError."""
        with pytest.raises(InvalidIDError):
            AgentId(value="")

    def test_canonicalized_values_are_equal(self) -> None:
        """Objects created from uppercase and lowercase UUID are equal."""
        agent1 = AgentId(value=VALID_UUID_UPPER)
        agent2 = AgentId(value=VALID_UUID)
        assert agent1 == agent2


class TestIdentityImmutability:
    """Tests for immutability guarantees."""

    def test_immutability_cannot_modify_value(self) -> None:
        """Attempting to modify .value raises FrozenInstanceError."""
        agent_id = AgentId(value=VALID_UUID)
        obj = cast(Any, agent_id)
        with pytest.raises(FrozenInstanceError):
            obj.value = "another"


class TestIdentityEquality:
    """Tests for equality semantics."""

    def test_equality_same_type_same_value(self) -> None:
        """Two AgentIds with same value are equal."""
        agent1 = AgentId(value=VALID_UUID)
        agent2 = AgentId(value=VALID_UUID)
        assert agent1 == agent2

    def test_inequality_different_types_same_value(self) -> None:
        """AgentId and TaskId with same UUID are NOT equal."""
        agent_id = AgentId(value=VALID_UUID)
        task_id = TaskId(value=VALID_UUID)
        assert agent_id != task_id
        assert not (agent_id == task_id)


class TestIdentityPublicAPI:
    """Tests for public API surface."""

    def test_str_returns_value(self) -> None:
        """str(agent_id) returns the canonical .value."""
        agent_id = AgentId(value=VALID_UUID)
        assert str(agent_id) == agent_id.value

    def test_kw_only_rejects_positional_arguments(self) -> None:
        """Positional arguments are rejected due to kw_only=True."""
        ctor = cast(Any, AgentId)
        with pytest.raises(TypeError):
            ctor(VALID_UUID)
