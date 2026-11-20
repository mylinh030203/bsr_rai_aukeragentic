p = 'docs/design/prototype/assets/app.js'
d = open(p, 'rb').read()
start = d.find(b'const markers = eventsInRange.map')
end = d.find(b'</svg>`;', start)
print('start', start, 'end', end)
print(d[start:end].decode('utf-8'))
