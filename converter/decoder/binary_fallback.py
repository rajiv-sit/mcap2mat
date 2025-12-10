"""
Binary fallback when decoding is unavailable.
"""

from __future__ import annotations

from typing import Any


def preserve(payload: bytes) -> Any:
    """
    Return raw bytes as-is. Kept as a function for symmetry with other decoders.
    """
    return payload
