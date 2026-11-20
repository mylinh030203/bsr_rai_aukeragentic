import os
import hashlib

p = 'docs/design/prototype/assets/data.js'
data = open(p, 'rb').read()
print(len(data), hashlib.sha256(data).hexdigest()[:12], data.count(b'\r\n'))
print(os.access(p, os.R_OK), os.access(p, os.W_OK))
