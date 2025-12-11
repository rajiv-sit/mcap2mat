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
