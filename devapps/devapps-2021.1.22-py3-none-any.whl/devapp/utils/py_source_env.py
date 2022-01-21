"""
Dependency free sourcer of shell style environ files into a
python process
"""


import json
import os
import subprocess as sp
import sys
from fnmatch import fnmatch
from os.path import exists

env = os.environ


def die(msg, **kw):
    print(msg, str(kw))
    sys.exit(1)


def source(*f, set_sys_path_from_py_path=None, ign_missing=False, insert_env_vars=()):
    """ sourcing shell config file
    we source all in one process, in order to allow referencing of vars within

    Referenced environ vars from outside are not resolved, unless state by insert_env_vars!
    """
    pyth = sys.executable

    F = []
    for i in list(f):
        if not exists(i):
            if not ign_missing:
                die('does not exist', fn=i)
        else:
            F.append(i)
    if not F:
        return {}
    # . is compatible with sh, source not
    src = '. ' + ' && . '.join(F)
    for i in insert_env_vars:
        if not '*' in i:
            src = ('export %s="%s" && ' % (i, env.get(i, ''))) + src
        else:
            ae = [k for k in env if fnmatch(k, i)]
            for j in ae:
                src = ('export %s="%s" && ' % (j, env.get(j, ''))) + src

    dump = '"%s" -Ssc "import os, json;' % pyth
    dump += 'print(json.dumps(dict(os.environ)))"'
    # -i: Starts with empty environ -> no refs work in our sourced file:
    cmd = ['env', '-i', '/bin/bash', '-c', 'set -a && %s && %s' % (src, dump)]
    out, err = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE).communicate()
    if err or not out:
        die('Error sourcing', f=f, err=err)
    res = json.loads(out)
    for k in 'SHLVL', '_', 'PWD':
        res.pop(k, 0)
    res = dict([(str(k), str(v)) for k, v in list(res.items())])
    if set_sys_path_from_py_path:
        pp = res.get('PYTHONPATH', '').split(':')
        for p in pp:
            sys.path.insert(0, p)
    return res
