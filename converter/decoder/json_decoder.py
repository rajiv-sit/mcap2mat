"""
JSON decoder using orjson when available, falling back to stdlib json.
"""

from __future__ import annotations

import json
from typing import Any

try:
    import orjson  # type: ignore
except Exception:  # pragma: no cover - optional dep
    orjson = None


def decode(payload: bytes) -> Any:
    """Decode bytes to Python data via JSON."""
    if orjson:
        return orjson.loads(payload)
    return json.loads(payload.decode("utf-8"))
