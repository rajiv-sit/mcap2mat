# MCAP to MAT Converter

Pure-Python, cross-platform MCAP→MAT converter. No native extensions, runs anywhere Python 3.8+ works (Windows, Linux, macOS, QNX).

## Quickstart
- Create env: `python -m venv .venv`
- Activate  
  - Windows: `.venv\Scripts\activate`  
  - POSIX/QNX/macOS: `source .venv/bin/activate`
- Install deps: `pip install -r requirements.txt` (or `pip install -e .` for editable)

## Usage
```
mcap2mat --in input.mcap --out output.mat \
  --topics cam,lidar \
  --time-range 0,10 \
  --proto-set descriptors.pb \
  --keep-raw
```

Notes
- Paths can be relative or absolute. In PowerShell keep the command on one line or use backticks for line breaks.
- Topic names are sanitized to MATLAB-safe variable names. The MAT includes `topic_name_map` that maps sanitized names back to original MCAP topics.
- Binary payloads are stored as `uint8`; JSON/Protobuf are decoded when possible (pass `--proto-set`/`--proto-path` if you want Proto decoding).

MATLAB example
```matlab
m = load('C:/path/to/output.mat');
map = m.topic_name_map;
% map.original{i} -> map.matlab{i}
data = m.v__radar_fl;        % example sanitized name
data.timestamps(1:5)         % inspect timestamps
first_payload = data.data{1}; % uint8 for binary topics
```

## Layout
- `converter/` core package
- `converter/io/` MCAP reader
- `converter/decoder/` JSON/Protobuf/binary handlers
- `converter/mat/` MATLAB writer
- `converter/pipeline/` orchestrator
- `tests/` pipeline tests

## Tests
- Install test deps (pytest is part of the editable install via requirements): `pip install -r requirements.txt`
- Run all tests: `python -m pytest`
- Quick sample conversion test (requires `data/data1.mcap`): `python -m pytest tests/test_data1_conversion.py`

MATLAB compatibility via `scipy.io.savemat`; default uncompressed for widest MATLAB version support.
