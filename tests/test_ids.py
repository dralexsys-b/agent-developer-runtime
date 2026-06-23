"""Unit tests for ID generation and validation."""

import uuid

import pytest

from agent_runtime.kernel.errors import InvalidIDError, KernelError
from agent_runtime.kernel.ids import generate_id, validate_id


class TestGenerateId:
    """Tests for generate_id() function."""

    def test_generate_id_returns_string(self) -> None:
        """generate_id() should return a string."""
        result = generate_id()
        assert isinstance(result, str)

    def test_generate_id_returns_valid_uuid_v4(self) -> None:
        """generate_id() should return a valid UUID v4 string."""
        result = generate_id()
        # Should not raise
        parsed = uuid.UUID(result)
        assert parsed.version == 4

    def test_generate_id_returns_lowercase(self) -> None:
        """generate_id() should return lowercase UUID string."""
        result = generate_id()
        assert result == result.lower()


class TestValidateId:
    """Tests for validate_id() function."""

    def test_validate_id_accepts_valid_uuid(self) -> None:
        """validate_id() should accept a valid UUID string."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        result = validate_id(valid_uuid)
        assert result == valid_uuid

    def test_validate_id_normalizes_to_lowercase(self) -> None:
        """validate_id() should normalize UUID to lowercase."""
        uppercase_uuid = "550E8400-E29B-41D4-A716-446655440000"
        result = validate_id(uppercase_uuid)
        assert result == "550e8400-e29b-41d4-a716-446655440000"

    def test_validate_id_accepts_uuid_without_hyphens(self) -> None:
        """validate_id() should accept UUID without hyphens and normalize."""
        no_hyphens = "550e8400e29b41d4a716446655440000"
        result = validate_id(no_hyphens)
        # Should add hyphens in standard format
        assert result == "550e8400-e29b-41d4-a716-446655440000"

    def test_validate_id_rejects_empty_string(self) -> None:
        """validate_id() should reject empty string."""
        with pytest.raises(InvalidIDError, match=r"Invalid UUID format"):
            validate_id("")

    def test_validate_id_rejects_non_uuid_string(self) -> None:
        """validate_id() should reject non-UUID strings."""
        with pytest.raises(InvalidIDError, match=r"Invalid UUID format"):
            validate_id("not-a-uuid")

    def test_validate_id_rejects_partial_uuid(self) -> None:
        """validate_id() should reject partial UUID strings."""
        with pytest.raises(InvalidIDError, match=r"Invalid UUID format"):
            validate_id("550e8400-e29b-41d4")


class TestInvalidIDError:
    """Tests for InvalidIDError exception."""

    def test_invalid_id_error_is_kernel_error(self) -> None:
        """InvalidIDError should inherit from KernelError."""
        assert issubclass(InvalidIDError, KernelError)

    def test_invalid_id_error_is_exception(self) -> None:
        """InvalidIDError should inherit from Exception."""
        assert issubclass(InvalidIDError, Exception)

    def test_invalid_id_error_can_be_raised(self) -> None:
        """InvalidIDError should be raisable."""
        with pytest.raises(InvalidIDError):
            raise InvalidIDError("test error")

    def test_invalid_id_error_message(self) -> None:
        """InvalidIDError should preserve error message with input."""
        with pytest.raises(InvalidIDError, match=r"Invalid UUID format"):
            validate_id("invalid")
