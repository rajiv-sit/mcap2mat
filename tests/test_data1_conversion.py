from pathlib import Path

from converter import config
from converter.pipeline.converter import run_conversion


def test_convert_data1_mcap_to_mat(tmp_path):
    data_dir = Path(__file__).resolve().parent.parent / "data"
    input_path = data_dir / "data1.mcap"
    assert input_path.exists(), "Expected data1.mcap in data/ directory"

    output_path = tmp_path / "data1.mat"
    cfg = config.Config(
        input_path=input_path,
        output_path=output_path,
        topics=None,
        time_range=None,
        proto_set=None,
        proto_search_paths=[],
        keep_raw=False,
        compress_mat=False,
        dry_run=False,
    )

    assert run_conversion(cfg) is True
    assert output_path.exists(), "MAT file was not created"
    assert output_path.stat().st_size > 0
