"""
Schema/descriptor registry for Protobuf decoding.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from google.protobuf import descriptor_pb2, descriptor_pool, message_factory


class ProtoRegistry:
    """
    Minimal registry that can decode messages using a FileDescriptorSet.
    """

    def __init__(self, descriptor_set_path: Optional[Path] = None) -> None:
        self._pool = descriptor_pool.DescriptorPool()
        self._factory = message_factory.MessageFactory(self._pool)
        if descriptor_set_path:
            self._load_descriptor_set(descriptor_set_path)

    def _load_descriptor_set(self, path: Path) -> None:
        data = path.read_bytes()
        fds = descriptor_pb2.FileDescriptorSet()
        fds.ParseFromString(data)
        for fd_proto in fds.file:
            self._pool.Add(fd_proto)

    def has_type(self, full_name: str) -> bool:
        try:
            self._pool.FindMessageTypeByName(full_name)
            return True
        except Exception:
            return False

    def decode_to_message(self, full_name: str, payload: bytes):
        descriptor = self._pool.FindMessageTypeByName(full_name)
        message_cls = self._factory.GetPrototype(descriptor)
        msg = message_cls()
        msg.ParseFromString(payload)
        return msg
