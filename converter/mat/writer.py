"""
MAT writer built on scipy.io.savemat.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Mapping, MutableMapping

import numpy as np
from scipy.io import savemat


def to_mat_arrays(topic_data: Mapping[str, Dict[str, List]]) -> Dict[str, object]:
    """
    Convert internal topic data into savemat-compatible structures.
    Each topic becomes a dict of numpy arrays or object arrays.
    """
    mat_ready: Dict[str, object] = {}
    for topic, data in topic_data.items():
        topic_struct: MutableMapping[str, object] = {}
        topic_struct["timestamps"] = np.array(data.get("timestamps", []), dtype=np.int64)
        topic_struct["encoding"] = np.array(data.get("encoding", []), dtype=object)
        topic_struct["schema"] = np.array(data.get("schema", []), dtype=object)
        topic_struct["data"] = np.array(data.get("data", []), dtype=object)
        if "raw" in data:
            topic_struct["raw"] = np.array(data.get("raw", []), dtype=object)
        mat_ready[topic] = topic_struct
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
