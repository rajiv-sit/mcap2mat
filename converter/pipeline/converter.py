"""
End-to-end MCAP→MAT conversion pipeline.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from converter import config
from converter.decoder import binary_fallback, json_decoder, protobuf_decoder
from converter.decoder.registry import ProtoRegistry
from converter.io.mcap_reader import iter_messages
from converter.mat.writer import write_mat


LOG = logging.getLogger(__name__)


def _within_time_range(
    log_time_ns: int, time_range: Optional[tuple[Optional[float], Optional[float]]]
) -> bool:
    if not time_range:
        return True
    start, end = time_range
    t_sec = log_time_ns / 1e9
    if start is not None and t_sec < start:
        return False
    if end is not None and t_sec > end:
        return False
    return True


def _select_decoder(message_encoding: Optional[str]) -> str:
    enc = (message_encoding or "").lower()
    if "json" in enc:
        return "json"
    if "protobuf" in enc or "proto" in enc:
        return "protobuf"
    return "binary"


def run_conversion(cfg: config.Config) -> bool:
    """
    Execute the conversion. Returns True on success, False otherwise.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    registry = ProtoRegistry(cfg.proto_set) if cfg.proto_set else None
    topic_data: Dict[str, Dict[str, List]] = {}
    seen_topics = set()

    for schema, channel, message in iter_messages(cfg.input_path, cfg.topics):
        if not _within_time_range(message.log_time, cfg.time_range):
            continue

        topic = channel.topic
        seen_topics.add(topic)
        bucket = topic_data.setdefault(
            topic, {"timestamps": [], "encoding": [], "schema": [], "data": []}
        )
        decoder_kind = _select_decoder(channel.message_encoding)
        decoded = None
        raw_payload = message.data
        schema_name = schema.name if schema else None

        try:
            if decoder_kind == "json":
                decoded = json_decoder.decode(raw_payload)
            elif decoder_kind == "protobuf" and registry and schema_name and registry.has_type(schema_name):
                decoded = protobuf_decoder.decode(raw_payload, registry, schema_name)
            else:
                decoded = binary_fallback.preserve(raw_payload)
                decoder_kind = "binary"
        except Exception as exc:  # pragma: no cover - passthrough logging
            LOG.warning("Decode failed for topic %s: %s", topic, exc)
            decoded = binary_fallback.preserve(raw_payload)
            decoder_kind = "binary"

        bucket["timestamps"].append(message.log_time)
        bucket["encoding"].append(decoder_kind)
        bucket["schema"].append(schema_name or "")
        bucket["data"].append(decoded)
        if cfg.keep_raw:
            bucket.setdefault("raw", []).append(raw_payload)

    if cfg.dry_run:
        LOG.info("Dry run complete. Topics seen: %s", sorted(seen_topics))
        return True

    write_mat(cfg.output_path, topic_data, compress=cfg.compress_mat)
    LOG.info("Wrote MAT file to %s", cfg.output_path)
    return True
