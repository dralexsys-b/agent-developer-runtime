"""ID generation and validation utilities.

Provides functions to generate unique identifiers for domain entities.
Uses UUID v4 for random IDs.
"""

import uuid

from agent_runtime.kernel.errors import InvalidIDError


def generate_id() -> str:
    """Generate a new random UUID v4 as string.

    Returns:
        UUID v4 string in lowercase.
    """
    return str(uuid.uuid4())


def validate_id(id_str: str) -> str:
    """Validate and normalize a UUID string.

    Args:
        id_str: String to validate.

    Returns:
        Normalized UUID string (lowercase).

    Raises:
        InvalidIDError: If the string is not a valid UUID.
    """
    try:
        return str(uuid.UUID(id_str))
    except (ValueError, AttributeError) as e:
        raise InvalidIDError(f"Invalid UUID format: {id_str}") from e


__all__ = ["generate_id", "validate_id"]
