"""
Configuration parsing for the MCAP→MAT converter.
"""

from __future__ import annotations

import argparse
import dataclasses
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


@dataclasses.dataclass
class Config:
    """Resolved configuration options for a conversion run."""

    input_path: Path
    output_path: Path
    topics: Optional[List[str]]
    time_range: Optional[Tuple[Optional[float], Optional[float]]]
    proto_set: Optional[Path]
    proto_search_paths: List[Path]
    keep_raw: bool
    compress_mat: bool
    dry_run: bool


def _parse_time_range(value: str) -> Tuple[Optional[float], Optional[float]]:
    """Parse a start,end time range expressed in seconds."""
    parts = value.split(",")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("time-range must be start,end")
    start = float(parts[0]) if parts[0] else None
    end = float(parts[1]) if parts[1] else None
    if start is not None and end is not None and end < start:
        raise argparse.ArgumentTypeError("end must be >= start")
    return start, end


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert MCAP files to MATLAB .mat files (pure Python, cross-platform)."
    )
    parser.add_argument("--in", dest="input_path", required=True, help="Path to input .mcap")
    parser.add_argument("--out", dest="output_path", required=True, help="Path to output .mat")
    parser.add_argument(
        "--topics",
        dest="topics",
        help="Comma-separated topic filter; omit for all topics.",
    )
    parser.add_argument(
        "--time-range",
        dest="time_range",
        type=_parse_time_range,
        help="Start,end seconds filter; empty value for open bound (e.g., '1.0,' or ',5.0').",
    )
    parser.add_argument(
        "--proto-set",
        dest="proto_set",
        help="Optional Protobuf FileDescriptorSet file for decoding.",
    )
    parser.add_argument(
        "--proto-path",
        dest="proto_search_paths",
        action="append",
        default=[],
        help="Optional directory containing .proto files (can be repeated).",
    )
    parser.add_argument(
        "--keep-raw",
        dest="keep_raw",
        action="store_true",
        help="Include undecoded raw bytes in output.",
    )
    parser.add_argument(
        "--compress",
        dest="compress_mat",
        action="store_true",
        help="Enable savemat compression (off by default for widest MATLAB compatibility).",
    )
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Inspect MCAP structure without writing a MAT file.",
    )
    return parser


def parse_args(args: Optional[Iterable[str]] = None) -> Config:
    parser = build_arg_parser()
    ns = parser.parse_args(args=args)
    topics = ns.topics.split(",") if ns.topics else None
    proto_paths = [Path(p) for p in ns.proto_search_paths]
    return Config(
        input_path=Path(ns.input_path),
        output_path=Path(ns.output_path),
        topics=topics,
        time_range=ns.time_range,
        proto_set=Path(ns.proto_set) if ns.proto_set else None,
        proto_search_paths=proto_paths,
        keep_raw=bool(ns.keep_raw),
        compress_mat=bool(ns.compress_mat),
        dry_run=bool(ns.dry_run),
    )
