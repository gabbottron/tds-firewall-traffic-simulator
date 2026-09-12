"""FSTO/1 teaching contract implementation."""

from .generator import (
    generate_canonical,
    get_canonical_hex,
    get_canonical_digest,
    CANONICAL_FIELDS,
    FIELD_ORDER,
)

__all__ = [
    "generate_canonical",
    "get_canonical_hex",
    "get_canonical_digest",
    "CANONICAL_FIELDS",
    "FIELD_ORDER",
]
