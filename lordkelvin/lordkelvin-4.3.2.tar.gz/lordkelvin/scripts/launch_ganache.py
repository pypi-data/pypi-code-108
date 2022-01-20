#!/usr/bin/env -S python3 -u
import os, sys, re, subprocess as subp, time
from collections import OrderedDict as odict

PID_FNAME = '/tmp/ganache.pid'
    
PORT = sys.argv[1]

try:
    os.kill(int(open(PID_FNAME).read()), 9)
    print('>> old process killed')
    try:
        os.system('rm -fr ganache.pid')
    except:
        pass
    pass
except:
    print('>> no old process')
    pass

if PORT == '.':
    PORT = os.getenv('PORT')
elif PORT == '-k':
    raise exit(0)

prv, pub = odict(), odict()

cmd = f"ganache-cli -h 0 -p {PORT}"

print(">> Launching " + cmd)

p = subp.Popen(cmd.split(), stdout=subp.PIPE)

with open(PID_FNAME, 'w') as f:
    print(p.pid, file=f)
    pass

for line in p.stdout:
    line = line.decode()
    print(f'  | {line}', end='')
    if line.startswith('Listening on'):
        break
    arr = line.strip().split()
    if arr:
        m = re.match(r'\((\d)\)', arr[0])
        if m:
            n = m.group(1)
            if n in pub:
                prv[n] = arr[1][3:]
            else:
                pub[n] = arr[1]
                pass
            pass
        pass
    pass

for k in pub:
    with open(f'/tmp/{k}.pub', 'w') as f:
        print(pub[k], file=f)
        pass
    with open(f'/tmp/{k}.prv', 'w') as f:
        print(prv[k], file=f)
        pass
    pass

cmd = sys.argv[2:]

if cmd:
    print(">>", repr(cmd))
    raise os.execlp(cmd[0], *cmd)

print(">> no cmd")
