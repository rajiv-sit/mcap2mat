# MCAP to MAT Converter

Pure-Python, cross-platform MCAP→MAT converter. No native extensions, runs anywhere Python 3.8+ works (Windows, Linux, macOS, QNX).

## Quickstart
- Create venv: `python -m venv .venv`
- Activate: Windows `.venv\Scripts\activate`, POSIX/QNX/macOS `source .venv/bin/activate`
- Install: `pip install -e .`

## Usage
```
mcap2mat --in input.mcap --out output.mat \
  --topics cam,lidar \
  --time-range 0,10 \
  --proto-set descriptors.pb \
  --keep-raw
```

## Layout
- `converter/` core package
- `converter/io/` MCAP reader
- `converter/decoder/` JSON/Protobuf/binary handlers
- `converter/mat/` MATLAB writer
- `converter/pipeline/` orchestrator
- `tests/` pipeline tests

MATLAB compatibility via `scipy.io.savemat`; default uncompressed for widest MATLAB version support.
