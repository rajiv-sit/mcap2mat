"""
Console entrypoint wiring config parsing to the conversion pipeline.
"""

from __future__ import annotations

import sys

from converter import config
from converter.pipeline.converter import run_conversion


def main(argv: list[str] | None = None) -> int:
    args = config.parse_args(argv)
    result = run_conversion(args)
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
