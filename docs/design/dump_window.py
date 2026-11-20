"""Dump a character window by line/column so long template lines can be read
without a broad dump (the previous full-file dump overflowed tool output).
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = 'docs/design/prototype/assets/app.js'
lines = open(path, encoding='utf-8').read().split('\n')

start = int(sys.argv[1]) - 1
end = int(sys.argv[2])
width = int(sys.argv[3]) if len(sys.argv) > 3 else 1200

for k in range(start, min(end, len(lines))):
    text = lines[k]
    print(f'--- {k + 1} (len {len(text)}) ---')
    print(text[:width])
    if len(text) > width:
        print(f'... [truncated {len(text) - width} chars] ...')
