function out = mcap2mat(mcapPath, varargin)
%MCAP2MAT Convert MCAP file to MAT; returns struct, table, and writes .mat if outPath given.

p = inputParser;
addRequired(p, 'mcapPath', @(s) ischar(s) || isstring(s));
addParameter(p, 'out', '', @(s) ischar(s) || isstring(s));
parse(p, mcapPath, varargin{:});
mcapPath = char(p.Results.mcapPath);
outPath  = char(p.Results.out);

if isempty(pyenv().Version)
    error('Configure Python: pyenv("Version","/path/to/python")');
end

pyLines = [
    "import sys, json, scipy.io as sio; from mcap.reader import make_reader; import numpy as np;"
    "mcap_file = sys.argv[1]; out_path = sys.argv[2] if len(sys.argv) > 2 else '';"
    "code = '''with open(mcap_file, 'rb') as f:\n"
    "    r = make_reader(f)\n"
    "    records = []\n"
    "    for schema, channel, message in r.iter_messages():\n"
    "        records.append({\n"
    "            'channel': channel.topic,\n"
    "            'log_time': int(message.log_time),\n"
    "            'publish_time': int(message.publish_time),\n"
    "            'data': bytes(message.data).hex()\n"
    "        })\n"
    "    data = {'records': records}\n"
    "    if out_path: sio.savemat(out_path, data)\n"
    "    print(json.dumps(data))''' ; exec(code)"
];
pycode = strjoin(pyLines, " ");

cmd = sprintf('python -c "%s" "%s" "%s" 2>&1', pycode, mcapPath, outPath);
[status, cmdout] = system(cmd);
if status ~= 0
    error('Python failed (status %d): %s', status, cmdout);
end
if isempty(strtrim(cmdout))
    error('Python produced no output. Cmd was: %s', cmd);
end

out = jsondecode(cmdout);

% Convenience: table view and decoded byte payloads
if isfield(out, 'records') && ~isempty(out.records)
    out.table = struct2table(out.records);
    dataHex = out.table.data;
    out.data_bytes = cellfun(@(h) uint8(sscanf(h, '%2x')).', dataHex, 'UniformOutput', false);
else
    out.table = table;
    out.data_bytes = {};
end

if ~isempty(outPath)
    fprintf('Saved MAT to %s\n', outPath);
end
end
