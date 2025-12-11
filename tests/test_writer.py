from converter.mat.writer import to_mat_arrays


def test_matlab_safe_topic_names_and_mapping():
    topic_data = {
        "/radar/fl": {
            "timestamps": [1],
            "encoding": ["binary"],
            "schema": [""],
            "data": [b"x"],
        },
        "radar_fl": {"timestamps": [2], "encoding": ["binary"], "schema": [""], "data": [b"y"]},
        "123topic": {"timestamps": [3], "encoding": ["json"], "schema": [""], "data": ["z"]},
    }

    prepared = to_mat_arrays(topic_data)
    assert "topic_name_map" in prepared

    mapping = prepared["topic_name_map"]
    originals = list(mapping["original"])
    matlab_names = list(mapping["matlab"])

    assert set(originals) == set(topic_data.keys())
    assert len(matlab_names) == len(originals)
    assert len(set(matlab_names)) == len(matlab_names)

    sanitized_keys = {k for k in prepared.keys() if k != "topic_name_map"}
    assert all("/" not in key for key in sanitized_keys)

    pairs = dict(zip(originals, matlab_names))
    for orig, safe in pairs.items():
        assert safe in prepared, f"Sanitized name missing for {orig}"


def test_bytes_normalized_to_uint8_arrays():
    topic_data = {
        "topic": {
            "timestamps": [1, 2],
            "encoding": ["binary", "binary"],
            "schema": ["", ""],
            "data": [b"\x00\x01", bytearray(b"\x02\x03")],
            "raw": [memoryview(b"\x04\x05")],
        }
    }

    prepared = to_mat_arrays(topic_data)
    topic_struct = prepared["topic"]

    data_field = topic_struct["data"]
    raw_field = topic_struct["raw"]

    assert all(hasattr(entry, "dtype") and entry.dtype == "uint8" for entry in data_field)
    assert all(hasattr(entry, "dtype") and entry.dtype == "uint8" for entry in raw_field)


def test_records_struct_flattened_with_raw():
    topic_data = {
        "topic": {
            "timestamps": [1],
            "encoding": ["binary"],
            "schema": [""],
            "data": [b"\x00\x01"],
            "raw": [b"\x00\x01"],
        }
    }
    records = [
        {
            "channel": "topic",
            "log_time": 123,
            "publish_time": 456,
            "encoding": "binary",
            "schema": "",
            "data": b"\x00\x01",
            "raw": b"\x00\x01",
        }
    ]

    prepared = to_mat_arrays(topic_data, records=records)
    assert "records" in prepared

    rec_struct = prepared["records"]
    assert set(rec_struct.keys()) == {
        "channel",
        "log_time",
        "publish_time",
        "encoding",
        "schema",
        "data",
        "raw",
    }

    assert rec_struct["channel"][0] == "topic"
    assert rec_struct["log_time"][0] == 123
    assert rec_struct["publish_time"][0] == 456
    assert rec_struct["encoding"][0] == "binary"
    assert rec_struct["schema"][0] == ""
    assert hasattr(rec_struct["data"][0], "dtype") and rec_struct["data"][0].dtype == "uint8"
    assert hasattr(rec_struct["raw"][0], "dtype") and rec_struct["raw"][0].dtype == "uint8"
