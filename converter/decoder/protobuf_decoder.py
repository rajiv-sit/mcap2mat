"""
Protobuf decoder using a loaded descriptor registry.
"""

from __future__ import annotations

from typing import Any, Optional

from google.protobuf.json_format import MessageToDict

from converter.decoder.registry import ProtoRegistry


def decode(payload: bytes, registry: ProtoRegistry, type_name: Optional[str]) -> Any:
    """
    Decode Protobuf payload to a Python dict using the provided registry.
    If the type is unknown or decoding fails, raise an exception for the caller to handle.
    """
    if not registry or not type_name:
        raise ValueError("Protobuf registry or type name missing")
    msg = registry.decode_to_message(type_name, payload)
    return MessageToDict(msg, preserving_proto_field_name=True)
