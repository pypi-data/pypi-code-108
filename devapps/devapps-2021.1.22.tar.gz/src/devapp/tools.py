"""
Taken from axc2 pretty much as is
"""
import collections
import json

import toml

# colors from the os theme for python:
import os
import re
import shutil
import string
import subprocess
import sys
import time
import types
from copy import deepcopy
from fnmatch import fnmatch

# from jsondiff import diff as js_diff # TODO
from functools import partial
from pprint import pformat
from threading import current_thread
from absl import flags
from theming.formatting.markdown import indent, deindent  # noqa

reverse_dict = lambda m: {v: k for k, v in m.items()}


def parse_kw_str(kws, header_kws=None, try_json=True):
    """for kw via cli"""
    header_kws = {} if header_kws is None else header_kws
    if try_json:
        if kws and kws[0] in ('{', '['):
            try:
                return json.loads(kws)
            except:
                pass
    if ', ' in kws:
        raise Exception('No comma allowed')
    kw = {}
    parts = kws.split()
    kw.update(
        {
            p[0]: cast(p[1])
            for p in [(k if '=' in k else k + '=true').split('=') for k in parts]
        }
    )
    kw = {k: header_kws.get(v, v) for k, v in kw.items()}
    return kw


def local_ips(c=[0]):
    i = c[0]
    if i:
        return i
    ips = subprocess.check_output(['hostname', '-I'])
    c[0] = ips.decode('utf-8').strip().split()
    return c[0]


def hostname(c=[0]):
    i = c[0]
    if i:
        return i
    c[0] = socket.gethostname()
    return c[0]


def gitcmd(dir, cmd='git rev-parse --verify HEAD'):
    cmds = [cmd, 'git config --get remote.origin.url']
    t = 'cd "%s" && %s'
    while len(dir) > 2:
        dir = dirname(dir)
        if exists(dir + '/.git/objects'):
            res = [os.popen(t % (dir, cmd)).read().strip() for cmd in cmds]
            return (
                dict(dir=dir, name=os.path.basename(dir), cmd=res[0], url=res[1])
                if res[0]
                else None
            )


def flatten(d, sep='_'):
    import collections

    obj = collections.OrderedDict()

    def recurse(t, parent_key=''):

        if isinstance(t, list):
            for i in range(len(t)):
                recurse(t[i], parent_key + sep + str(i) if parent_key else str(i))
        elif isinstance(t, dict):
            for k, v in t.items():
                recurse(v, parent_key + sep + k if parent_key else k)
        else:
            obj[parent_key] = t

    recurse(d)

    return obj


def cast(v):
    if v and v[0] in ('{', '['):
        return json.loads(v)
    try:
        return int(v)
    except:
        try:
            return float(v)
        except:
            return {'true': True, 'false': False}.get(v, v)


# --------------------------------------------------------------------------------- tty
have_tty = lambda: sys.stdin.isatty() and sys.stdout.isatty()

try:
    # Setting the default for the cli - flag, i.e. this rules w/o the flag:
    term_fixed_width_env = int(os.environ.get('term_width'))
except:
    term_fixed_width_env = 0
try:
    # Setting the default for the cli - flag, i.e. this rules w/o the flag:
    term_fixed_height_env = int(os.environ.get('term_height'))
except:
    term_fixed_height_env = 0


def walk_dir(directory, crit=None):
    crit = (lambda *a: True) if crit is None else crit
    files = []
    j = os.path.join
    for (dirpath, dirnames, filenames) in os.walk(directory):
        files += [j(dirpath, file) for file in filenames if crit(dirpath, file)]
    return files


from contextlib import contextmanager


class Pytest:
    """Helpers specifically for pytest"""

    this_test = lambda: os.environ['PYTEST_CURRENT_TEST']
    cur_flags = {}
    had_flags = {}

    @contextmanager
    def set_flags(**testflags):
        """intended to be run *after* Pytest.init"""
        Pytest.cur_flags.update(testflags)
        f = testflags.items()
        [into(Pytest.had_flags, k, getattr(flags.FLAGS, k)) for k in testflags]
        [setattr(flags.FLAGS, k, v) for k, v in f]
        yield StopIteration
        [setattr(flags.FLAGS, k, v) for k, v in Pytest.had_flags.items()]
        Pytest.cur_flags.clear()
        Pytest.had_flags.clear()

    def parse_test_infos(into=None):
        m = {} if into is None else into
        t = Pytest.this_test()
        f = t.split('::')
        m['class'] = f[1]
        m['test'] = f[-1].split('(')[0].strip()  # testname
        m['file'] = _ = f[0]
        m['fn_mod'] = _ = _.rsplit('/', 1)[-1].rsplit('.py', 1)[0]
        mod = sys.modules[_]
        m['path'] = mod.__file__
        return m

    this_test_func_name = lambda: Pytest.parse_test_infos()['test']

    def set_sys_argv(done=[0]):
        """
        remove any pytest cli args, like -xs, sind that would break FLGs:

        coverage:pytest.py, else pytest. and yes, its shit.
        TODO: create a conf + fixture, avoiding this:
        """
        is_pytest_run = 'pytest' in sys.argv[0].rsplit('/', 1)[-1]

        if done[0] or not is_pytest_run:
            return
        done[0] = True

        while len(sys.argv) > 1:
            sys.argv.pop()

        # strangly we lack our export env, e.g. port-offset in pytest runs since 2020/12
        # happens only if we start via make test, not when started from poetry shell.
        # not sure of a bug of us or a feature of pytest

        # Actual workaround, but deemed anyway better,is to read the flags from here:
        f = '%s/config/pytest.flags' % project.root()
        if os.path.exists(f):
            sys.argv.append('--flagfile=%s' % f)
        # 'environ_flags': True,
        # 'port_offset': os.environ.get('port_offset', 0),
        # 'make_autodocs': os.environ.get('make_autodocs', False),
        # 'log_level': 10,
        # 'log_time_fmt': 'dt',
        # 'log_add_thread_name': True,
        # 'log_dev_fmt_coljson': 'pipes,cfg,payload',
        # 'plot_depth': 3,
        # 'plot_id_short_chars': 8,
        # }

        dflts = {}
        if sys.stdout.isatty():
            dflts['plot_before_build'] = True

        for k, v in dflts.items():
            v = envget(k, v)
            print('pytest EnvFlag: %s = %s' % (k, v))
            if v:
                env[k] = str(v)

    def init():
        Pytest.set_sys_argv()
        FLG(sys.argv)  # parsing the flags


import fcntl, termios, struct


def terminal_size():
    # try piped left and/or right, if both piped then return 80,25:
    # since we want to print we try first stdout:
    for fd in 1, 0:
        try:
            h, w, hp, wp = struct.unpack(
                'HHHH',
                fcntl.ioctl(fd, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)),
            )
            return (w or 80), h  # go really sure its no 0
        except:
            pass
    return 80, 25


def termwidth():
    return termsize()[0]


def termsize():
    try:
        w, h = FLG.term_fixed_width, FLG.term_fixed_height
    except:
        # not yet parsed?
        w, h = 0, 0
    if w and h:
        return w, h
    return terminal_size()


# -------------------------------------------------------------------------- data utils
def to_list(o):
    o = [] if o is None else o
    t = type(o)
    return o if t == list else list(o) if t == tuple else [o]


def matched(d, match, prefix=()):
    """Returns parts of data where keys match match string - mainly for debugging (P)"""
    if isinstance(d, (tuple, list)):
        v = [matched(l, match) for l in d]
        if not any([k for k in v if k is not None]):
            return None
        # remove structs wich don't match but leave data:
        r, rd = [], []
        for o in v:
            if isinstance(o, (dict, list, tuple)):
                rd.append(o)
            r.append(o)
        return rd  # best
    if not isinstance(d, dict):
        return
    match = '*%s*' % match
    r = {}
    for k, v in d.items():
        k = str(k)
        np = prefix + (k,)
        if fnmatch(k, match):
            r['.'.join(np)] = v
        vv = matched(v, match, prefix=np)
        if vv:
            if isinstance(v, dict):
                if vv:
                    r.update(vv)
            elif isinstance(v, (tuple, list)):
                r['.'.join(np)] = vv

    return r


def headerize(dicts_list, mark=None):
    '''mark e.g. "dicts"'''
    l = dicts_list
    if not isinstance(l, list) or not l or not isinstance(l[0], dict):
        return l

    r = [list(l[0].keys())]
    r.extend([[m.get(h) for h in r[0]] for m in l])
    if mark:
        r = {mark: r}
    return r


def recurse_data(data, key_callbacks):
    if isinstance(data, dict):
        for k, v in data.items():
            cb = key_callbacks.get(k)
            if cb:
                data[k] = v = cb(v)
            if isinstance(v, (list, dict, tuple)):
                data[k] = v = recurse_data(v, key_callbacks)
    elif isinstance(data, list):
        data = [recurse_data(d, key_callbacks) for d in data]
    elif isinstance(data, tuple):
        data = tuple([recurse_data(d, key_callbacks) for d in data])
    return data


termcols = shutil.get_terminal_size((80, 20)).columns


def P(data, depth=None, match=None, headered=None, out=True, **kw):
    """
    Pretty Printer for large Dicts. In globals(). For debugging.
    P(data, 0, 'wifi') -> deep subtree match

    P(data, depth=2, match=None, [headered|h]='all')

    headered='all' -> all values for key 'all', if a list of dicts, will be printed as lists with headers
    h='all': alias for headered


    kw: pformat kws: indent=1, width=80, depth=None, stream=None, *, compact=False, sort_dicts=True
    """
    # P(data, 'match') also:
    kw['width'] = kw.get('width') or termcols
    headered = kw.pop('h', headered)
    if headered:
        data = deepcopy(data)
        kw['compact'] = kw.get('compact', True)

    if isinstance(depth, str):
        match = depth
        depth = None
    depth = depth or None  # 0 is None
    if match:
        data = matched(data, match)
    h = to_list(headered)
    if h:
        h = {k: partial(headerize, mark='@DL') for k in h}
        data = recurse_data(data, h)
    p = pformat(data, depth=depth, **kw)
    if out:
        print(p)
    else:
        return p


class DictTree(dict):
    __is_tree__ = True

    @property
    def __class__(self):
        # isinstance is dict:
        return dict

    def __getattr__(self, name):
        v = self[name]
        if isinstance(v, dict):
            return v if hasattr(v, '__is_tree__') else DictTree(v)
        return v


class DictTreeMatched(dict):
    __is_tree__ = True

    @property
    def __class__(self):
        # isinstance is dict:
        return dict

    def __getattr__(self, name, nil=b'\x04'):
        v = self.get(name, nil)
        if v == nil:
            for k in self.keys():
                if k.startswith(name):
                    return getattr(self, k)
            self[name]

        if isinstance(v, dict):
            return v if hasattr(v, '__is_tree__') else DictTreeMatched(v)
        return v


# debugging tool: P('data', 1) in pdb sessions
if isinstance(__builtins__, dict):
    __builtins__['P'] = P
    __builtins__['DT'] = DictTree
    __builtins__['T'] = DictTreeMatched
else:
    __builtins__.P = P
    __builtins__.DT = DictTree
    __builtins__.T = DictTreeMatched


def get_deep(key, data, sep='.', create=False, dflt=None):
    """
    Client can, via the dflt. decide how to handle problems, like collisions with values
    """
    # key maybe already path tuple - or string with sep as seperator:
    if not key:
        return data
    d = data
    parts = key.split(sep) if isinstance(key, str) else list(key)
    while parts:
        part = parts.pop(0)
        try:
            data = data[part]
        except TypeError as ex:
            # a list was in the original data:
            try:
                data = data[int(part)]
            except:
                # this happens when we are already at a value, like an int
                # client wants to go deeper, not possible, but we can't delete the int
                # -> leave the client to decide:
                if dflt is None:
                    raise KeyError(key)
                return dflt
        except KeyError as ex:
            if not create:
                if dflt is None:
                    raise
                return dflt
            data = data.setdefault(part, {})

    return data


def deep_update(orig_dict, new_dict, maptyp=collections.abc.Mapping):
    for key, val in new_dict.items():
        if isinstance(val, maptyp):
            tmp = deep_update(orig_dict.get(key, {}), val)
            orig_dict[key] = tmp
        elif isinstance(val, list):
            orig_dict[key] = orig_dict.get(key, []) + val
        else:
            orig_dict[key] = new_dict[key]
    return orig_dict


def in_gevent():
    try:
        import gevent

        return gevent.sleep == time.sleep
    except:
        return False


has_tty = lambda: sys.stdin.isatty() and sys.stdout.isatty()


def confirm(msg):
    if not has_tty():
        raise Exception('Require confirmation for: %s' % msg)
    print(msg)
    r = input('Confirmed [y|N]? ')
    if r.lower() != 'y':
        from devapp.app import app

        app.die('Unconfirmed')


now = lambda: int(time.time() * 1000)
is_ = isinstance


def jdiff(d1, d2):
    try:
        # Got exception when we have L(list) in test_share.py
        return jsondiff(d1, d2, marshal=True)
    except Exception as ex:
        # TODO: convert tuples recursively into strings
        try:
            d1 = json.loads(json.dumps(d1, default=str))
            d2 = json.loads(json.dumps(d2, default=str))
            return jsondiff(d1, d2, marshal=True)
        except Exception as ex:
            return {'err': 'cannot diff', 'exc': str(ex)}


def dict_merge(source, destination):
    """dest wins"""

    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            dict_merge(value, node)
        else:
            destination[key] = value

    return destination


tn = lambda: current_thread().name
pass_ = lambda *a, **kw: None
exists = os.path.exists
dirname = os.path.dirname
abspath = os.path.abspath
env = os.environ
envget = os.environ.get
# kw: rscs may later provide e.g. their name, allowing port offset specific for them:
def offset_port(port, **kw):
    return int(port) + FLG.port_offset


import socket


def wait_for_port(port, host='127.0.0.1', timeout=5.0, log_err=True):
    """Wait until a port starts accepting TCP connections.
    Raises:
        TimeoutError: The port isn't accepting connection after time specified in `timeout`.
    """
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError as ex:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                if not log_err:
                    return
                try:
                    from devapp.app import app

                    return app.error('Timeout', host=host, port=port, timeout=timeout)
                except:
                    print('timeout awaiting port %s' % port)


def repl_dollar_var_with_env_val(
    s, die_on_fail=True, ask_on_fail=False, get_vals=False
):
    """
    s = foo_$bar.or${baz}  - the first form searched until first non Letter char
    Will be replaced by value of environ for $bar and $baz
    """
    if not '$' in s:
        if not get_vals:
            return s
        return s, {}

    tty, vals = have_tty(), {}

    def go(s, ask_on_fail, tty=tty, vals=vals):
        s += ' '
        missing, have, Letters, nil = {}, [], string.ascii_letters + '_', '\x1b'
        parts = s.split('$')
        n = parts[0]
        for p in parts[1:]:
            if not p:
                raise
            if p[0] == '{':
                if not '}' in p:
                    raise
                have.append(p.split('}', 1)[0][1:])
            else:
                S = ''
                for c in p:
                    S += c
                    if not c in Letters:
                        break
                have.append(S[:-1])
                s = s.replace('$%s' % S, '${%s}%s' % (have[-1], c))
        for k in have:
            app = import_app()
            if not k in env and ask_on_fail and tty:
                app.warn('Missing value in environ', required=k, within=s)
                v = input('Enter value for "$%s": ' % k)
            else:
                v = env[k]
            s = s.replace('${%s}' % k, v)
            vals[k] = v
        return s[:-1]

    r = s
    try:
        r = go(s, ask_on_fail)
        if '$' in r:
            raise
    except Exception as ex:
        if die_on_fail or ask_on_fail:
            app = import_app()
            app.die('Not defined in environ', var=s)
    if get_vals:
        return r, vals
    return r


def import_app():
    from devapp.app import app

    return app


# here = dir_of(__file__)
def dir_of(fn, up=0):
    d = abspath(dirname(fn))
    return dir_of(d, up - 1) if up else d


def to_url(shorthand):
    s = shorthand
    if not s.startswith('http'):
        s = 'http://' + s
    schema, rest = s.split('://', 1)
    if not '/' in rest:
        rest = rest + '/'
    hp, path = rest.split('/', 1)
    if hp.startswith(':'):
        hp = '127.0.0.1' + hp
    elif hp.isdigit():
        hp = '127.0.0.1:%s' % hp
    hp = hp.replace('*', '0.0.0.0')
    return schema + '://' + hp + '/' + path


def host_port(shorthand):
    u = to_url(shorthand).split('//', 1)[1]
    h, p = u.split(':')
    return h, int(p.split('/', 1)[0])


def write_config_cls_key(k, v):
    fn = env['DA_DIR'] + '/config.cls'
    s = read_file(fn).splitlines()
    s = [l for l in s if not l.startswith('%s=' % k)]
    s.append('%s="%s"' % (k, v))
    s.sort()
    write_file(fn, '\n'.join(s) + '\n')


archives = {'.tar.gz': 'tar xfvz "%(frm)s"', '.tar': 'tar xfv "%(frm)s"'}


def download_file(url, local_filename, auto_extract=True):
    """auto extract works for exe types like hugo.tar.gz -> contains in same dir the hugo binary.
    if the .tar.gz is containing a bin dir then the user should rather not say type
    is 'exe' but type is archive or so
    """
    import requests
    from devapp.app import app

    app.info('Downloading', url=url, to=local_filename)
    r = requests.get(url, stream=True)
    arch, fn = None, local_filename
    if auto_extract:
        for k in archives:
            if url.endswith(k):
                arch = k
                fn = local_filename + k
                break

    with open(fn, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    if arch:
        m = {'dir': fn.rsplit('/', 1)[0], 'cmd': archives[arch], 'frm': fn}
        m['cmd'] = m['cmd'] % m
        cmd = 'cd "%(dir)s" && %(cmd)s' % m
        app.info('Uncharchiving', cmd=cmd)
        os.system(cmd)
    return local_filename


_is_root = [None]  # True, False. None: undefined
_sudo_pw = [None]  # None: undef


def sudo_pw():
    fns = env.get('DA_FILE_SUDO_PASSWORD') or env['HOME'] + '/.sudo_password'
    return env.get('SUDO_PASSWORD') or read_file(fns, '').strip()


def sp_call(*args, as_root='false', get_all=False):
    """run command - as root if 'true' or True"""
    # todo: as_root = 'auto'
    sp = subprocess
    sudo = str(as_root).lower() == 'true'
    if sudo:
        if _is_root[0] == None:
            _is_root[0] = os.system('touch /etc/hosts 2>/dev/null') == 0
        if _is_root[0]:
            sudo = False
    if sudo:
        args = ('sudo', '-S') + tuple(args)
        if _sudo_pw[0] == None:
            _sudo_pw[0] = sudo_pw()
        pw = sp.Popen(('echo', _sudo_pw[0]), stdout=sp.PIPE)
        stdin = pw.stdout
    else:
        stdin = sys.stdin
    proc = sp.Popen(list(args), shell=False, stdin=stdin, stderr=sp.PIPE)
    out, err = proc.communicate()
    if not get_all:
        return err
    return {'exit_status': int(proc.wait()), 'stderr': err, 'stdout': '<term>'}


def exec_file(fn, ctx=None, get_src=None):
    ctx = ctx if ctx is not None else {}
    # allows tracebacks with file pos:
    ctx['__file__'] = fn
    src = read_file(fn)
    exec(compile(src, fn, 'exec'), ctx)
    if get_src:
        ctx['source'] = src
    return ctx


def funcname(f):
    while True:
        n = getattr(f, '__name__', None)
        if n:
            return n
        f = f.func


env = os.environ

clean_env_key = lambda s: ''.join(
    [c for c in s if c in string.digits + string.ascii_letters]
)


def restart_unshared(name):
    """
    Manual user start of daemons.
    Since we assemble filesystems we dont' want those hang around globally,
    but be gone with session end.
    Systemd does this as well.
    must be called at beginning of the process - sys.argv must be original
    """

    def set_linked_python_as_executable():
        """Systemd starts us with sourceing env then ../run/$DA_CLS -m devapp.run start
        sys.argv then: ['$DA_MAX_DIR/../python/devapp/run.py', 'start']
        When a user copies this from the unit file then a unshare is done.
        That calls the start args again after unshare -- ...
        WE have /bin/env python in hashbang - resulting in differences in the ps ax
        -> we replace:
        """
        if sys.argv[0].endswith('/run.py'):
            sys.argv.pop(0)
            for k in 'devapp.run', '-m', '%(DA_DIR)s/run/%(DA_CLS)s' % env:
                sys.argv.insert(0, k)

    n = name
    if sys.argv[-1] == 'unshared':
        sys.argv.pop()
        env['da_unshared'] = n
    if env.get('da_unshared') != n:
        sys.argv.append('unshared')
        print(
            'Restarting unshared. To prevent: export da_unshared="%s"' % n,
            file=sys.stderr,
        )
        c = ['unshare', '-rm', '--']
        set_linked_python_as_executable()
        c.extend(sys.argv)
        sys.exit(subprocess.call(c))


env, envget, exists = os.environ, os.environ.get, os.path.exists
ctx = {}

str8 = partial(str, encoding='utf-8')
is_str = lambda s: isinstance(s, str)

# not matches classes which are callable:
is_func = lambda f: isinstance(
    f, (types.FunctionType, types.BuiltinFunctionType, partial)
)

json_diff = lambda old, new: json.loads(js_diff(old, new, syntax='explicit', dump=True))


def into(d, k, v):
    """the return is important for e.g. rx"""
    d[k] = v
    return d


def setitem(m, k, v):  # for list comprehensions
    m[k] = v


def deep(m, dflt, *pth):
    """Access to props in nested dicts / Creating subdicts by *pth

    Switch to create mode a bit crazy, but had no sig possibilit in PY2:
    # thats a py3 feature I miss, have to fix like that:
    if add is set (m, True) we create the path in m

    Example:
    deep(res, True), [], 'post', 'a', 'b').append(r['fid'])
        creates in res dict: {'post': {'a': {'b': []}}}  (i.e. as list)
        and appends r['fid'] to it in one go
        create because init True was set

    """
    m, add = m if isinstance(m, tuple) else (m, False)
    keys = list(pth)
    while True:
        k = keys.pop(0)
        get = m.setdefault if add else m.get
        v = dflt if not keys else {}
        m = get(k, v)
        if not keys:
            return m


def start_of(s, chars=100):
    """ to not spam output we often do "foo {a': 'b'...."""
    s = str8(s)
    return s[:100] + '...' if len(s) > 100 else ''


cast_list = lambda v, sep=',': (
    [] if v == '[]' else [s.strip() for s in v.split(sep)] if is_str(v) else v
)


dt_precision = '%.2fs'


def dt_human(ts_start, ts_end=None):
    dt = time.time() - ts_start if ts_end is None else ts_end - ts_start
    if dt > 7200:
        return '%.2fh' % (dt / 3600.0)
    return dt_precision % dt


class AllStatic(type):
    'turn all methods of this class into static methods'
    new = None

    def __new__(cls, name, bases, local):
        for k in local:
            if k.startswith('_'):
                continue
            if is_func(local[k]):
                local[k] = staticmethod(local[k])
        # customization hook:
        if cls.new:
            cls.new(cls, name, bases, local)
        return type.__new__(cls, name, bases, local)


class _ctx:
    def __enter__(self, *a, **kw):
        pass

    __exit__ = __enter__


def parse_host(url, no_port=None):
    if not url.startswith('http'):
        raise Exception(url + ' is no url')
    host = '/'.join(url.split('/', 3)[:3])
    if no_port:
        host = ':'.join(host.split(':')[:2])
    return host


class LazyDict(dict):
    def get(self, key, thunk=None):
        return self[key] if key in self else thunk() if callable(thunk) else thunk

    def set_lazy(self, key, thunk=None, *a, **kw):
        return (
            self[key]
            if key in self
            else dict.setdefault(
                self, key, thunk(*a, **kw) if callable(thunk) else thunk
            )
        )


osenv = os.environ.get
HCOLS = {'M': '#8bd124', 'R': '#FF0000', 'L': '#333399', 'I': '#44FFFF'}

shl = 'shell'


def camel_to_snake(string):
    groups = re.findall('([A-z0-9][a-z]*)', string)
    return '_'.join([i.lower() for i in groups])


def url_to_dir(url):
    # url = url.replace('file://', '') # NO, leave
    for ft in '://', '?', ':':
        url = url.replace(ft, '_')
    return url


def html(s, col):
    return '<font color="%s">%s</font>' % (HCOLS[col], s)


def color(s, col, mode=shl):
    if not osenv(col):
        return str(s)
    # for col term
    if mode == 'html':
        return html(s, col)
    else:
        return str(s)


# faster than calling color func:
sm = '%s%%s\x1B[0m' % ('\x1B%s' % osenv('M', '')[2:])
si = '%s%%s\x1B[0m' % ('\x1B%s' % osenv('I', '')[2:])
sl = '%s%%s\x1B[0m' % ('\x1B%s' % osenv('L', '')[2:])
sr = '%s%%s\x1B[0m' % ('\x1B%s' % osenv('R', '')[2:])
sgr = '%s%%s\x1B[0m' % '\x1B[1;38;5;154m'


def M(s, mode=shl):
    if mode == shl:
        return sm % s
    return color(s, 'M', mode)


def I(s, mode=shl):
    if mode == shl:
        return si % s
    return color(s, 'I', mode)


def L(s, mode=shl):
    if mode == shl:
        return sl % s
    return color(s, 'L', mode)


def R(s, mode=shl):
    if mode == shl:
        return sr % s
    return color(s, 'R', mode)


def GR(s):
    return sgr % s


def check_start_env(req_env):
    """ can we run ? """

    def die(msg):
        print(msg)
        sys.exit(1)

    for k in req_env:
        rd = envget(k)
        if not rd:
            die('$%s required' % k)
    return 'Passed requirements check'


def read_file(fn, dflt=None, bytes=-1, strip_comments=False):
    """
    API function.
    read a file - return a default if it does not exist"""
    if not exists(fn):
        if dflt is not None:
            return dflt
        raise Exception(fn, 'does not exist')
    with open(fn) as fd:
        # no idea why but __etc__hostname always contains a linesep at end
        # not present in source => rstrip(), hope this does not break templs
        res = fd.read(bytes)
        res = res if not res.endswith('\n') else res[:-1]
        if strip_comments:
            lines = res.splitlines()
            res = '\n'.join([l for l in lines if not l.startswith('#')])
        return res


def write_file(fn, s, log=0, mkdir=0, chmod=None, mode='w'):
    'API: Write a file. chmod e.g. 0o755 (as octal integer)'
    from devapp.app import app

    fn = os.path.abspath(fn)

    if log > 0:
        app.info('Writing file', fn=fn)

    if isinstance(s, (list, tuple)):
        s = '\n'.join(s)
    if log > 1:
        sep = '\n----------------------\n'
        ps = (
            s
            if not 'key' in fn and not 'assw' in fn and not 'ecret' in fn
            else '<hidden>'
        )
        app.debug('Content', content=sep + ps + sep[:-1])
    e = None
    for i in 1, 2:
        try:
            with open(fn, mode) as fd:
                fd.write(s)
            if chmod:
                if not isinstance(chmod, (list, tuple)):
                    chmod = [int(chmod)]
                for s in chmod:
                    os.chmod(fn, s)
            return fn
        except IOError as ex:
            if mkdir:
                d = os.path.dirname(fn)
                os.makedirs(d)
                continue
            e = ex
        except Exception as ex:
            e = ex
        raise Exception('Could not write file: %s %s' % (fn, e))


def failsafe(meth, *a, **kw):
    """Spotted log errors at aggressively reconnecting clients, running in greenlets
    in the pytest progs. This allows to wrap these methods.
    """
    # spotted log
    try:
        meth(*a, **kw)
    except Exception as ex:
        print('Failed with %s: %s(%s %s)' % (str(ex), meth, str(a), str(kw)))


# ------------------------------------------------------------------------------- flags


FLG = flags.FLAGS


def set_flag(k, v):
    t = type(getattr(FLG, k))
    if t == list:
        v = cast_list(v)

    setattr(FLG, k, t(v))


def set_flag_vals_from_env():
    """allows so ref $foo as default var a flag"""
    # hmm. pytest -> nrtesting -> run_app in greenlet. How to pass flags, e.g. to drawflow
    ef = FLG.environ_flags or os.environ.get(
        'environ_flags'
    )  # if set we check all from environ
    for f in dir(FLG):
        if ef:
            v = os.environ.get(f)
            if v:
                set_flag(f, v)
                continue
        # wanted always from environ by developer - then he gave a default with $:
        v = getattr(FLG, f)
        if isinstance(v, str) and v.startswith('$'):
            setattr(FLG, f, os.environ.get(v[1:], v))


def shorten(key, prefix, maxlen, all_shorts=None, take=1):
    take, sold = 1, None
    while True:
        s = autoshort(key, prefix, maxlen, take)
        if not s in all_shorts:
            return s
        if s == sold:
            raise Exception('Unresolvable collision in autoshort names: %s' % key)
        sold, take, maxlen = s, take + 1, maxlen + 0


def autoshort(key, prefix, maxlen, take=1):
    ml = maxlen - len(prefix)
    parts = key.split('_')
    if prefix and not any([c for c in prefix if not c in parts[0]]):
        parts.pop(0)
    r = prefix + ''.join([parts.pop(0)[0:take].lower() for i in range(ml) if parts])
    return r[:maxlen]


# fmt:off
_ = [
    [type(None),    'boolean'     ] ,
    [str,           'string'      ] ,
    [int,           'integer'     ] ,
    [float,         'float'       ] ,
    [list,          'list'        ] ,
    [bool,          'boolean'     ] ,
    ['multi_string','multi_string'] ,
    ['multi_enum'  ,'multi_enum'  ] ,
]
_flag_makers = dict({k: getattr(flags, 'DEFINE_' + v) for k, v in _})
# fmt:on


def mk_enum(*a, vals, **kw):
    f = flags.DEFINE_multi_enum if isinstance(vals, tuple) else flags.DEFINE_enum
    a = list(a)
    a.insert(2, vals)
    return f(*a, **kw)


def flag_makers(t, m=_flag_makers):
    # the actual absl.flags.DEFINE_integer(..),... methods
    if isinstance(t, (list, tuple)):
        return partial(mk_enum, vals=t)
    else:
        return _flag_makers[t]


all_flag_shorts = {}


def make_flag(c, module, autoshort, default, sub=False, **kw):
    g = getattr
    key = orig_key = c.__name__
    # if key == 'verbose':
    #     breakpoint()  # FIXME BREAKPOINT
    if sub and not sub == 'Actions':
        key = sub + '_' + key
    d = g(c, 'd', default)  # when d is not given, what to do. Dictates the flag type.
    ml = kw.get('short_maxlen', 5)
    s = g(c, 's', None)
    mkw = {'module_name': module, 'short_name': s}
    if s is None and autoshort is not False:
        s = shorten(orig_key, prefix=autoshort, maxlen=ml, all_shorts=all_flag_shorts)
    if s is False:
        s = None
    else:
        all_flag_shorts[s] = key
        # when we parse the cli for action flags we also want to find shortened afs:
        af = action_flags.get(key)
        if af:
            action_flags[s] = af
    mkw['short_name'] = s
    define_flag = flag_makers(g(c, 't', type(d)))
    txt = g(c, 'n', human(key))
    if c.__doc__:
        ls = c.__doc__.replace(c.n, '').splitlines()
        txt += ' Details: %s' % ('\n'.join([l.strip() for l in ls]).strip())
    define_flag(key, d, txt, **mkw)


human = lambda key: ' '.join([k.capitalize() for k in key.split(' ')])


# this allows a module to "steal" the flags class of another module. e.g. lc client:
skip_flag_defines = []


have_flg_cls = set()
action_flags = {}


def have_subs(c):
    for s in [getattr(c, s) for s in dir(c) if not s.startswith('_')]:
        if isinstance(s, type):
            return True


def rm_absl_flags():
    FLG.remove_flag_values(
        ['v',]
    )


def define_flags(Class, sub=False, parent_autoshort=False):
    """
    Pretty classes to flag defs. See nrclient, devapp.app or structlogging.sl how to use
    All config in the top class
    2021/06: Subclassses allowed
    """

    if Class in have_flg_cls:
        from devapp.app import app

        return app.warn('Flag class defined already - skipping', Class=Class)
    have_flg_cls.add(Class)
    # TODO: Register docstrings here (markdown?), supplying even more detailed help
    g = getattr
    module = g(Class, 'module', Class.__module__)
    if module in skip_flag_defines:
        return
    # passed to make_flag as default for default
    default = g(Class, 'default', '')
    autoshort = parent_autoshort = g(Class, 'autoshort', parent_autoshort)
    l = dict(locals())
    cshrt, c_no_shrt = [], []
    for k in [i for i in dir(Class) if not i.startswith('_')]:
        c = g(Class, k)

        if not isinstance(c, type):
            continue
        if sub == 'Actions':
            setattr(c, 'd', False if not g(c, 'd', None) == True else True)
            action_flags[k] = {
                'flg_cls': c,
                'class': Class,
                'key': k,
                'autoshort': g(c, 'autoshort', autoshort),
                'is_default': c.d,
            }

        if not hasattr(c, 'n'):
            if not hasattr(c, 'd'):
                a = g(c, 'autoshort', parent_autoshort)
                if not a and not c.__name__ == 'Actions':
                    pref = c.__name__[0]
                # prbably group but no n, no d is allowed as well
                if have_subs(c):
                    r = define_flags(c, sub=c.__name__, parent_autoshort=a)
                    continue
            # alternative to stating n we allow a multline docstring, where first line
            # is n, rest is details:
            doc = c.__doc__ or ''
            if doc.strip():
                c.n = doc.strip().split('\n', 1)[0]
        # if g(c, 's', None) == 'x':
        #     breakpoint()  # FIXME BREAKPOINT
        cshrt.append(c) if g(c, 's', None) else c_no_shrt.append(c)
    # do the ones with shorts first, to collide only on autoshorts:
    [make_flag(c, **l) for c in cshrt + c_no_shrt]
    # [make_flag(c, **l) for k in [cshrt, c_no_shrt] for c in k]


# define_flags(Flags)  # ours


def FlagsDict(f):
    """
    Flags to Dicts
    allows:
    FLG.foo = 'bar' -> '%(foo)s' % FlagsDict(Flags) = 'bar'
    i.e. Allow values of Flags to reference values of other flags.
    """

    # class F:
    #     __init__ = lambda self, f: setattr(self, 'f', f)
    #     __getitem__ = lambda self, k: getattr(self.f, k)

    # return F(f)
    return FLG.flag_values_dict()


class project:
    """loads the project config

    Main app config put into project.cfg['app']
    An optional tool.lc.app section will be merged into that

    TODO: other formats than pyproject.toml

    """

    config, dir_home, fn_cfg = {}, None, None

    def root(no_fail=False):
        # r = FLG.project_directory or os.environ.get('project_directory')
        # if r:
        #     if not exists(r):
        #         from devapp.app import app

        #         os.makedirs(r)
        #         os.system('cd "%s"; git init' % r)
        #         app.warn('Created project (git) directory', dir=r)
        #     return r
        p = project.dir_home
        if not p:
            p = project.set_project_dir(no_fail=no_fail)
            if p:
                b = p + '/bin:'
                if not b in envget('PATH', ''):
                    env['PATH'] = b + envget('PATH', '')
            project.dir_home = p
        return project.dir_home

    def set_project_dir(dir=None, no_fail=False):
        """
        We search up and fail if we are not within the dir
        this is consistent with poetry (say poetry debug outside the dir ->
        Poetry could not find a pyproject.toml file in / or its parents
        """
        if dir:
            # hard set, e.g. from project initialize:
            project.dir_home = dir
            return

        d = os.getcwd()
        while len(d) > 3:
            for fn in 'pyproject.toml', 'setup.py', '.git':
                if os.path.exists(d + '/' + fn):
                    return d
            d = os.path.dirname(d)
        if no_fail:
            return
        from devapp.app import app

        app.die('could not determine project root dir')

    fn_resources = lambda: project.root() + '/.resources.json'

    fn_config = lambda: project.root() + '/pyproject.toml'

    def read_resources(filename=None):
        from devapp.app import app

        fn = filename or project.fn_resources()
        s = read_file(fn, dflt='')
        s = json.loads(s) if s else {}
        if s:
            app.info('loaded resources', filename=fn)
        project.resources = s
        return s

    def write_resources(rsc, filename=None):
        from devapp.app import app

        fn = filename or project.fn_resources()
        with open(fn, 'w') as fd:
            fd.write(json.dumps(rsc, indent=4))
        app.info('have written resources file', filename=fn)

    def get_present_resource(rsc, _have={}):
        from devapp.app import app

        if rsc in _have:
            return _have[rsc]
        r = project.read_resources()
        r = [i for i in r if i['name'] == rsc]
        if len(r) == 1 and r[0].get('installed'):
            _have[rsc] = r[0]
            return r[0]
        app.warn('Missing resource', resource=rsc)
        _have[rsc] = None

    def get_present_resource_location(rsc):
        r = project.get_present_resource(rsc)
        if r:
            r = r.get('installed')
            return r

    # TODO: understand also poetry and piptools:
    def load_config():
        from devapp.app import app

        fn = project.fn_config()
        if not exists(fn):
            app.die('no config found', fn=fn)

        cfg = toml.load(fn)
        app.info('loaded config', filename=fn)
        c = project.config
        c.update(cfg)
        if not 'project' in c:
            c['project'] = {'urls': {}}
        if 'tool' in c and 'poetry' in c['tool']:
            c['project'].update(c['tool']['poetry'])
            c['project']['urls']['homepage'] = c['project']['homepage']
            c['project']['urls']['repository'] = c['project']['repository']

        t = cfg['tool']
        # breakpoint()  # FIXME BREAKPOINT
        # c['app'] = t['poetry']
        # c['app'].update(t.get('lc', {}).get('app', {}))
        project.fn_cfg = fn
        # app.die('Did not find a pyproject.toml file with badges declared')
        return project.config

    def conf():
        return project.config or project.load_config()

    def name():
        p = project.conf()
        return p['project']['name']

    def urls():
        p = project.conf()['project']
        if 'urls' in p:
            return p['urls']
        urls = 'packagehome', 'discusshome', 'homepage', 'repository'
        return {k: p.get(k, '') for k in urls}

    def homepage():
        return project.urls().get('homepage', 'n.a.')

    def repository():
        return project.urls().get('repository', 'n.a.')

    def packagehome():
        return project.urls().get('packagehome', 'n.a.')

    def version():
        p = project.conf()['project']
        v = p['version']
        if isinstance(v, dict) and v.get('use_scm'):
            from pdm.pep517.scm import get_version_from_scm

            v = get_version_from_scm(project.root())
        return str(v)

    def dependencies():
        d = project.conf()['project']['dependencies']
        if isinstance(d, dict):
            # poetry:
            return d
        # pdm (pep)
        return parse_deps(d)

    def dev_dependencies():
        p = project.conf()['project']
        dd = p.get('dev-dependencies')
        if dd:
            if isinstance(dd, dict):
                # poetry - already dict:
                return dd
            return parse_deps(dd)

        r = [
            l
            for k in project.conf()['tool']['pdm']['dev-dependencies'].values()
            for l in k
        ]
        return parse_deps(r)

    def lock_data():
        fn = []
        for k in 'pdm', 'poetry':
            fn.insert(0, project.root() + '/%s.lock' % k)
            if exists(fn[0]):
                return toml.load(fn[0])
        die('No lock file in root', fn)


def parse_deps(deplist, seps='~<>!= '):
    m = {}
    for dep in deplist:
        h = False
        for s in seps:
            if s in dep:
                l = dep.split(s, 1)
                m[l[0]] = (s + l[1]).strip()
                h = True
                break
        if not h:
            m[dep] = ''
    return m


import re


is_sensitive = lambda key: re.match(FLG.sensitive_data_identifiers, key, re.IGNORECASE)
filter_passwords = lambda dct: {k: v for k, v in dct.items() if not is_sensitive(k)}


# --------------------------------------------------------------------- Not importable
def unavail(missing, req=None, warn=True):
    """We don't need everything always"""
    # TODO:Add a few pip install options
    def f(*a, _miss=missing, _req=req, _warn=warn, **kw):
        print('Function from package "%s" not available in your installation!' % _miss)
        if _req:
            print('Please run: ', _req)
        raise Exception('Cannot continue - missing %s' % _miss)

    if warn:
        print('Cannot import: %s' % missing)
    return f


try:
    from jsondiff import diff as jsondiff
except Exception as ex:
    jsondiff = unavail('jsondiff', req='pip install jsondiff', warn=False)


# ------------------------------------------------------------ decorators


# https://github.com/micheles/decorator/blob/master/docs/documentation.md
# preserve the signature of decorated functions in a consistent way across Python releases

try:
    from decorator import decorate, decorator
except ImportError as ex:
    decorate = decorator = unavail('decorator', req='pip install decorator', warn=False)

try:
    from tabulate import tabulate
except ImportError as ex:
    tabulate = unavail('tabulate', req='pip install tabulate', warn=False)


def _memoize(func, *args, **kw):
    if kw:  # frozenset is used to ensure hashability
        key = args, frozenset(list(kw.items()))
    else:
        key = args
    cache = func.cache  # public cache attribute added by memoize
    if key not in cache:
        cache[key] = func(*args, **kw)
    return cache[key]


def memoize(f):
    """
    A simple memoize implementation. It works by adding a .cache diction
    to the decorated function. The cache will grow indefinitely, so it i
    your responsibility to clear it, if needed.
    """
    f.cache = {}
    return decorate(f, _memoize)


class appflags:
    default = False
    autoshort = 'da'
    uc_dirwatch_flow = [
        'Running build app, monitoring flow.json, triggering plots on change',
        'build --plot_before --dirwatch .:flow',
    ]

    class dirwatch:
        n = 'Spawning helper process, sending reload, on changes in given directory. '
        n += 'The app itself keeps running normally, with full access at stdin,out, err. '
        n += 'You may deliver a match spec, colon seperated.'
        d = ''
        h = 'Format: <dir>[:match[:r]]. r for recursive. match w/o * will be enclosed in *, left and right.'
        s = 'dw'

    class redir_stderr:
        """There are process spawners which mix the streams (emacs call-process)
        Spawns sys.exit(os.system(cmd + ' 2>%s' % FLG.redir_stderr))"""

        n = 'Global redirect of stderr'
        d = ''

    class flat:
        n = 'Flatten output of nested structures'

    class sensitive_data_identifiers:
        n = 'Regexp which helps identify keys carrying sensitive information (for filtering out of logs). Case insensitive matching.'
        d = 'pass.*|.*secret.*'

    class help_call:
        n = 'Short help about a call'
        s = 'hh'

    class help_call_detailed:
        n = 'Detailed help about a call'
        s = 'hhh'

    class environ_flags:
        n = 'Respect environ first, for all flags'

    class port_offset:
        n = 'Set a global offset for any "port" argument of a function'
        d = 0

    class term_fixed_width:
        n = 'Sets terminal width to this. 0: auto.'
        d = term_fixed_width_env

    class term_fixed_height:
        n = 'Sets terminal size to this. 0: auto.'
        d = term_fixed_height_env

    # not needed to run os.system calls anymore:
    # class term_auto_width_recalc_every:
    #     n = 'When term with is auto we run stty size maximum every so many millisecs'
    #     d = 2000

    class help_output_fmt:
        s = False  #  must be long form, checked in absl_color_help
        t = [
            'plain',
            'simple',
            'github',
            'grid',
            'fancy_grid',
            'pipe',
            'orgtbl',
            'jira',
            'presto',
            'pretty',
            'psql',
            'rst',
            'mediawiki',
            'moinmoin',
            'youtrack',
            'html',
            'latex',
            'latex_raw',
            'latex_booktabs',
            'terminal',
            'textile',
        ]
        d = 'terminal'


define_flags(appflags)


if __name__ == '__main__':
    pass
    # r = P(
    #     {'a': [{'all': [{'a': 23, 'b': 23}, {'a': 2322, 'b': 232323}]}]},
    #     out=None,
    #     headered='all',
    # )
    # assert r == "{'a': [{'all': [['a', 'b'], 23, 23, 2322, 232323]}]}"
