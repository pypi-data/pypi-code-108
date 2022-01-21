#!/usr/bin/env python
"""
Tool to quickly build and app with plugins.

Usage: See lc.py

"""
import os
import sys
from fnmatch import fnmatch
from importlib import import_module

from devapp.tools import dir_of


def get_docstr(app=None):
    if not app:
        app = sys.argv[0]

    D = '''
Usage: %(app)s ACTION [--flag[=value] ...]

Available Plugins:
<PLUGINS>

Help:
    %(app)s <action> <-h|--helpfull> [match]

Note:
    - Action shortcuts understood, e.g. action "foo_bar_baz" = fbb
    - Plugins are taken on first found basis
    - Flags also have shortcut versions (e.g. -hf for --helpfull)

Example:
    %(app)s %(exmpl)s -hf log # all flags about logging
    '''
    D = D % {'app': os.path.basename(app), 'exmpl': example[0]}
    return D


class Plugins:
    pass


plugins = lambda: [p for p in dir(Plugins) if not p.startswith('_')]
_short = lambda p: ''.join([k[0] for k in p.split('_') if k])
shorts = lambda: {_short(k): k for k in plugins()}

example = ['']


def usage(e=0, app=None):
    ps = plugins()
    a = '\n'.join(['    - \x1b[1;32m%s\x1b[0m' % a for a in ps])
    if ps:
        example[0] = ps[0]
    print(get_docstr(app).replace('<PLUGINS>', a).replace(os.environ['HOME'], '~'))
    sys.exit(e)


helpflags = set(['-h', '--help', '--helpfull'])


def main(argv=None):
    """allows to pass argv[1:] (for testing)"""
    # if argv is not None:
    #     while len(sys.argv) > 1:
    #         sys.argv.pop()
    #     sys.argv.extend(argv)

    argv = sys.argv
    n_app = argv[0].rsplit('/', 1)[-1]  # e.g. app or ops
    find_plugins(n_app)
    if not plugins():
        msg = (
            'No plugins found. Create plugins/%s_<namespace>/ folder(s), '
            'containing importable python modules.'
        )
        print(msg % n_app)
        sys.exit(1)
    plugin = sys.argv[1] if len(sys.argv) > 1 else 'x'
    plugin = shorts().get(plugin, plugin)
    if not plugin in plugins():
        ec = 0 if any([a for a in sys.argv if a in helpflags]) else 1
        usage(ec)

    plug = plugname = getattr(Plugins, plugin)
    if isinstance(plug, str):
        plug = import_module(plug)

    sys_argv_rm_minus_h_for_hf(argv, plug, plugname)

    plug.main()


def sys_argv_rm_minus_h_for_hf(argv, plug, plugname):
    h, hf = False, False
    r = []
    for a in argv:
        if a in ('-h', '--help'):
            h = True
            continue
        if a in ('-hf', '--helpfull'):
            hf = True
        r.append(a)
    sys.argv.clear()
    sys.argv.extend(r)
    if h and not hf:
        sys.argv.append('-hf')
        sys.argv.append(plugname)
    if h or hf:
        # at -h, print out the module doc already here, since -h won't:
        # edit - no it actually does (doc pp -h)
        print()
        # print(plug.__doc__.strip())
        # print()


def all_plugin_dirs(name):
    """On name collisions we take first one found in sys.path
    => $PYTHONPATH overrules site-packages
    """
    all = {}

    def scan_sys_pth(d, all=all, exists=os.path.exists, name=name):
        for l in os.listdir(d):
            n = '%s/%s/plugins/%s_%s' % (d, l, name, l)
            if exists(n):
                name = os.path.basename(n)
                if not name in all:
                    all[name] = n

    [scan_sys_pth(d) for d in sys.path if os.path.isdir(d)]
    return all.values()


def find_plugins(n_app, pth='./plugins', match='*'):
    # ../devapp/bin/app.py' -> app:
    ds = all_plugin_dirs(n_app)
    [add_plugins(d, match) for d in ds]
    return main


def add_plugins(dp, match, _have=[]):
    dplugs = os.path.abspath(dp)
    d = os.path.dirname(dplugs)
    if not d in sys.path:
        sys.path.insert(0, dir_of(dplugs))
    dpre = dplugs.rsplit('/', 1)[-1]

    def c(fn, match=match):
        f = fn.split('.py')
        if len(f) == 2 and not fn.startswith('_'):
            if fnmatch(f[0], match):
                return f

    plugs = [fn for fn in os.listdir(dplugs) if c(fn)]
    for p in plugs:
        n = p.rsplit('.py')[0]
        # plug = import_module('%s.%s' % (dpre, n))
        plug = '%s.%s' % (dpre, n)
        setattr(Plugins, n, plug)


if __name__ == '__main__':
    main()
