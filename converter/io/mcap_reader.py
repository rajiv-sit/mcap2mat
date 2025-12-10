"""
MCAP reader helpers for streaming iteration without loading whole files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Generator, Iterable, Optional, Tuple

from mcap.reader import make_reader
from mcap.records import Channel, Message, Schema


def iter_messages(
    path: Path, topics: Optional[Iterable[str]] = None
) -> Generator[Tuple[Optional[Schema], Channel, Message], None, None]:
    """
    Yield (schema, channel, message) tuples from an MCAP file, streaming.
    """
    topic_set = set(topics) if topics else None
    with path.open("rb") as fh:
        reader = make_reader(fh)
        for schema, channel, message in reader.iter_messages():
            if topic_set and channel.topic not in topic_set:
                continue
            yield schema, channel, message
