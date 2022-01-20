#!/usr/bin/env python3
"""
$@

Usage:
  $@ [-q|-v] [-H HOST] [-p PORT] [ARGS...]
  $@ (-k | -h | -V)

Options:
  -q --quiet      quiet mode
  -v --verbose    verbose mode
  -k --kill       kill ganache process
  -h --help       show this screen.
  -V --version    show version.
  -H --host HOST  listening port [default: localhost]
  -p --port PORT  listening port [default: .]
  ARGS...         command to run [default: ./activate $SHELL]
"""
import os, sys, re, subprocess as subp, docopt
from collections import OrderedDict as odict
version = '1.1.1'
def eprint(*a,**kw):
    return print(*a, **kw, file=sys.stderr)
def writef(path, data, mode = 0o666):
    fd = os.open(path, os.O_CREAT|os.O_WRONLY, mode)
    with os.fdopen(fd, 'w') as f: f.write(data)
    return data
def main():
    name = 'ganache.pid'
    path = '/tmp/' + name
    try:
        os.kill(int(open(path).read()), 9)
        eprint('>> old process killed')
    except:
        eprint('>> no old process')
        pass
    try: os.unlink(path)
    except: pass
    doc = __doc__.replace('$@', sys.argv[0])
    A = docopt.docopt(doc, version=version)
    eprint(A)
    if A['--kill']: exit()
    quiet   = A['--quiet']
    verbose = A['--verbose']
    host = A['--host']
    port = A['--port']
    if port ==  '.': port = os.getenv('PORT', 9999)
    cmd = f"ganache-cli -h 0 -p {port}"
    activate = 'activate.sh'
    tmpl = '''\
#!/bin/bash
export PORT={port}
export PUBLIC={pub}
export PRIVATE={prv}
export WEB3_PROVIDER_URI={uri}
"$@"
'''    
    eprint(">> Launching " + cmd)
    p = subp.Popen(cmd, stdout=subp.PIPE, shell=True)
    writef(path, f'{p.pid}')
    prv, pub = odict(), odict()
    for line in p.stdout:
        line = line.decode().rstrip()
        if not quiet: print(f'  | {line}')
        if line.startswith('Listening on'):
            quiet = not verbose
            for k in pub:
                writef(f'/tmp/{k}.pub', pub[k])
                writef(f'/tmp/{k}.prv', prv[k])
                pass
            writef(activate, tmpl.format(
                port = port,
                pub = pub['0'],
                prv = prv['0'],
                uri = f'http://{host}:{port}',
            ), 0o700)
            arr = A['ARGS'] or [os.getenv('SHELL','/bin/sh')]
            arr = [f'./{activate}'] + arr
            eprint(">>", repr(arr))
            if os.fork(): os.execvp(arr[0], arr)
        elif arr := line.strip().split():
            if m := re.match(r'\((\d)\)', arr[0]):
                n, s = m.group(1), arr[1]
                if n in pub: prv[n] = s[3:]
                else:        pub[n] = s
                pass
            pass
        pass
    pass
if __name__=='__main__': main()
