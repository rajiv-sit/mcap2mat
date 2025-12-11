"""
MAT writer built on scipy.io.savemat.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Mapping, MutableMapping

import numpy as np
from scipy.io import savemat


def _normalize_value(value: object) -> object:
    """
    Ensure savemat-friendly values (convert bytes-like to uint8 arrays).
    """
    if isinstance(value, (bytes, bytearray, memoryview)):
        return np.frombuffer(bytes(value), dtype=np.uint8)
    return value


def _to_object_array(seq: List[object]) -> np.ndarray:
    """Convert a Python list into an object array with normalized entries."""
    return np.array([_normalize_value(v) for v in seq], dtype=object)


def _matlab_safe_name(name: str, used: set[str]) -> str:
    """
    Produce a MATLAB-safe variable name and ensure uniqueness.
    """
    cleaned = re.sub(r"[^0-9a-zA-Z_]", "_", name)
    if not cleaned or not cleaned[0].isalpha():
        cleaned = f"v_{cleaned}"
    cleaned = cleaned[:63]  # MATLAB variable name limit
    candidate = cleaned
    suffix = 1
    while candidate in used:
        candidate = f"{cleaned}_{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate


def to_mat_arrays(topic_data: Mapping[str, Dict[str, List]]) -> Dict[str, object]:
    """
    Convert internal topic data into savemat-compatible structures.
    Each topic becomes a dict of numpy arrays or object arrays.
    """
    mat_ready: Dict[str, object] = {}
    used_names: set[str] = set()
    name_map: Dict[str, str] = {}

    for topic, data in topic_data.items():
        safe_name = _matlab_safe_name(topic, used_names)
        name_map[topic] = safe_name

        topic_struct: MutableMapping[str, object] = {}
        topic_struct["timestamps"] = np.array(data.get("timestamps", []), dtype=np.int64)
        topic_struct["encoding"] = _to_object_array(data.get("encoding", []))
        topic_struct["schema"] = _to_object_array(data.get("schema", []))
        topic_struct["data"] = _to_object_array(data.get("data", []))
        if "raw" in data:
            topic_struct["raw"] = _to_object_array(data.get("raw", []))
        mat_ready[safe_name] = topic_struct

    # Preserve mapping back to original topic names so MATLAB users can look them up.
    mat_ready["topic_name_map"] = {
        "original": np.array(list(name_map.keys()), dtype=object),
        "matlab": np.array(list(name_map.values()), dtype=object),
    }
    return mat_ready


def write_mat(
    path: Path,
    topic_data: Mapping[str, Dict[str, List]],
    compress: bool = False,
) -> None:
    """
    Persist the converted data into a MATLAB .mat file.
    """
    prepared = to_mat_arrays(topic_data)
    savemat(path.as_posix(), prepared, do_compression=compress)
