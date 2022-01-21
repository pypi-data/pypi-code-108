# TODO DEPRECATED - move to archive
"""
CLI Wrapper.
- Maps CLI to Class Trees (namespaces) with functions

- Is able to pull out the devapp switches before digging into the tree

"""

import sys
from functools import partial
from inspect import signature

import mdvl
from devapp.app import app, run_app


def auto_type(v):
    for k, b in ('true', True), ('false', False):
        if str(v).lower() == k:
            return b
    for t in float, int:
        try:
            return typ(v)
        except:
            pass
    if not t:
        return ''
    return str(v)


def not_found(*a, **kw):
    app.die('Not supported')


def find_in_cls(cls, p):
    v = getattr(cls, p, None)
    if v is not None:
        return v
    p = p.lower()
    for k in dir(cls):
        if k.lower().startswith(p):
            vv = getattr(cls, k)
            if callable(vv):
                return vv


def sh_help(cls, cli, out=None, hir=0):
    hir += 1
    out = [] if out is None else out
    out.append('%s %s' % ('#' * hir, cls.__name__))
    d = getattr(cls, '__doc__')
    if d and '-hh' in cli:
        out.append(d)
    dflt_meth = getattr(cls, 'default', None)
    clss = []
    for k in dir(cls):
        if k.startswith('_') or k == 'default':
            continue
        c = getattr(cls, k)

        if isinstance(c, type):
            clss.append(c)

        elif callable(c):
            if c == dflt_meth:
                k += '[default]'
            out.append(
                '- **%s**(%s  '
                % (k, str(signature(c)).split('(', 1)[1].replace('**', '..'))
            )
            d = getattr(c, '__doc__')
            if d and '-hh' in cli:
                out.append(d)
    for c in clss:
        sh_help(c, cli, out, hir)
    if hir == 1:
        mdvl.render('\n'.join(out))
        return 0


def run_cls_tree(cls_tree):
    """sys.argv = [app, devappflags.., cls, subcls..., func, funcargs...]"""
    # get the devapp run flags into sys.argv (unit first non minus arg):
    for i in range(1, len(sys.argv)):
        if not sys.argv[i].startswith('-'):
            break
    sys.argv, meth_args = sys.argv[:i], sys.argv[i:]

    # get command func:
    cmd = cls_tree
    while meth_args:
        # get the command function from the nested class tree:
        p = meth_args.pop(0)
        ncmd = find_in_cls(cmd, p)
        if ncmd == None:
            meth_args.insert(0, p)
            break
        cmd = ncmd

    # we do our own help system, this is not about flags:
    b = [*sys.argv, *meth_args]
    if '-h' in b or '--help' in b or '-hh' in b:
        sys.exit(sh_help(cmd, cli=b))

    if isinstance(cmd, type):
        cmd = getattr(cmd, 'default', not_found)

    # get command args:
    a, kw = (), {}
    for p in meth_args:
        if '=' in p:
            k, v = p.split('=', 1)
            kw[k] = auto_type(v)
        else:
            a += (p,)
    # wrap command function with args:
    cmd = partial(cmd, *a, **kw)
    # kw_log = dict(
    #    log_dev_fmt_coljson=['res'],
    #    censor=(['res', 'token'], ['res', 'access_token']),
    # )
    return run_app(cmd)  # , kw_log=kw_log)
