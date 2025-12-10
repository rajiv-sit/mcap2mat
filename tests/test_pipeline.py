"""
Lightweight sanity tests for configuration and module wiring.
"""

from converter import config


def test_parse_args_minimal():
    args = config.parse_args(
        ["--in", "input.mcap", "--out", "output.mat"]
    )
    assert args.input_path.name == "input.mcap"
    assert args.output_path.name == "output.mat"
    assert args.topics is None
    assert args.time_range is None
