"""

sys.argv: 
    build/bin/<run_script> --log_fmt=10 foo bar -baz

Remember: run_script func-calls our def app_run(), with these as sys.args

if we can import $app (checked in loader) -> we check app_mod for 'foo' function
if present we call it right away, via run_app(foo)

if not app_mod or not presnt than this is a subproc call, e.g. for bash.

-> we parse all flags before "foo" in devapps then Popen the rest

ALL FLAGS BEFORE THE APP FUNCTION HAVE TO BE GIVEN WITH =!

WRONG: --log_level info
RIGHT: --log_level=info

(otherwise we'll try to lookup 'info' in the app module)
"""
import json

# pylint: disable=E0211
import os
import shutil
import signal
import subprocess as sp
import sys
import time
from functools import partial
from inspect import _empty, signature

from devapp import load
from devapp.app import FLG, app, flag, run_app
from devapp.spec import tools as spec_tools
from devapp.tools import has_tty, write_file

try:
    import psutil
except ImportError as ex:
    psutil = None


exists = os.path.exists
FS = spec_tools.FS
pyenv = lambda k, dflt=None: load.py_env.get(k, dflt)
proc_argv = []
env = os.environ

flag.bool('show', False, 'Dry run, only show args')
m = 'Additional $PATH, added to :%s'
flag.string('add_path', '', (m % env['PATH']).replace(':', '\n-'))

# always good to have (for md renders and the like):
if not env.get('term_with'):
    try:
        c, r = os.get_terminal_size(0)
    except Exception as ex:
        c, r = 80, 25
    env['term_width'], env['term_height'] = str(c), str(r)

# prevent problems when user exported it with / at the end:
_ = 'DA_DIR'
if _ in env:
    while env[_].endswith('/'):
        env[_] = env[_][:-1]


class DAFunctions:
    """
    Functions accessible via devapps' `da` utility
    """

    @staticmethod
    def _da_dir(die=True):
        da_dir = env.get('DA_DIR') or []
        # len for security, we rm -rf below
        if not da_dir or len(da_dir) < 2:
            msg = 'No $DA_DIR. Provide --da_dir or --da_name'
            app.error(msg)
            sys.exit(0)
        if not da_dir:
            if die:
                sys.exit(1)
        return da_dir

    @staticmethod
    def status():
        """Infos about the devapps installation"""
        return {'status': 'installed'}

    class tools:
        """general tools"""

    class spec:
        @staticmethod
        def _fn():
            return DAFunctions._da_dir() + '/conf/SPEC.py'

        @staticmethod
        def edit():
            if not has_tty:
                app.die('Require tty')
            vim = env.get('EDITOR') or 'vim'
            spec = DAFunctions.spec._fn()
            os.system(vim + ' ' + spec)

        @staticmethod
        def dict(tree=True, src=False, links=False):
            """Prints a serialized version of the spec to stdout
            The spec is expected in $DA_DIR/conf/SPEC.py"""
            spec = DAFunctions.spec._fn()
            g = DAFunctions.tools.exec_file(spec, get_src=True)
            r = g['root']
            m = {}
            if tree:
                m['tree'] = g['to_dict'](r)
            if links:
                m['links'] = g['dump_links'](r)
            if src:
                m['src'] = g['source']
            return m

        @staticmethod
        def apps(run=None):
            """ 
            Printing all app starter files.  

            The `run` argument allows for further processing (e.g. da spec.apps sc.status).
            I.e. `run` is convenience, for a loop like 
            `while read -r n; do $n sc.status; done < <(da -n wifi_single spec.apps | jq -r .[] )`
            
            Example: da spec.apps sc.status
            """
            # TODO: understand run as a list, i.e. pass a full command with args
            da_dir = DAFunctions._da_dir(die=False)
            db = da_dir + '/build/bin'
            if not os.path.exists(db):
                app.error('Empty - no build', dir=db)
                return []
            apps = [db + '/' + d for d in os.listdir(db)]
            if not run:
                return apps
            else:
                for app_ in apps:
                    app.info(app_, running=run)
                    run_proc([app_, run])

        @classmethod
        def clean(cls, confirm=False, conda_envs=False, etc=False, keep_running=False):
            """
            Deletes everything related to current service which is built at spec build runs
            except conda_env, unless envs=True is given.

            This is useful for tests.
            """
            if not has_tty and not confirm:
                app.error('Have no tty and force not set - ignoring')
            D = env['DA_DIR']

            def rmd(d, do=False):
                if exists(d):
                    if do:
                        app.info('Removing', dir=d)
                        shutil.rmtree(d)
                    else:
                        app.info('Keeping', dir=d)

            rmd(D + '/build', True)
            # [ # we don't have that often:
            #    run_proc([s, 'devapp.clean', 'keep_running=%s' % keep_running])
            #    for s in cls.apps()
            # ]
            if len(D) > 4:
                for sw, d in (conda_envs, 'envs'), (etc, 'etc'):
                    rmd(D + '/' + d, sw)


# alias
DAFunctions.apps = DAFunctions.spec.apps


def verify_lib(lib):
    app.die('Missing library', lib=lib) if not lib in globals() else 0


def psutil_str_to_dict(v):
    s = str(v).replace('"', '').replace("'", '')

    try:
        kvs = s.split('(', 1)[1][:-1].split(', ')
        kvs = [kv.split('=', 1) for kv in kvs]
        return dict([(k, auto_type(v)) for k, v in kvs])
    except:
        return {}


def dump_proc(p, **kw):
    pu2s = psutil_str_to_dict
    m = {
        'pid': p.pid,
        'children_count': len(p.children()),
        '_pretty_': pu2s(p),
    }
    pa = [
        'cmdline',
        'connections',
        'cpu_affinity',
        'cpu_num',
        'cpu_percent',
        'cpu_times',
        'create_time',
        'cwd',
        'exe',
        'gids',
        'io_counters',
        'is_running',
        'memory_full_info',
        #'memory_info',
        #'memory_info_ex',
        'memory_percent',
        'name',
        'nice',
        'num_ctx_switches',
        'num_fds',
        'num_threads',
        'open_files',
        'parent',
        #'parents',
        'ppid',
        'status',
        'terminal',
        'threads',
        'uids',
        'username',
    ]
    subs = [
        'cpu_times',
        'gids',
        'io_counters',
        'memory_full_info',
        'num_ctx_switches',
        'parent',
        'uids',
    ]
    filter = kw.get('filter', '')
    if filter:
        pa = [k for k in pa if filter in k]
    if kw.get('env') or 'env' in filter:
        pa.append('environ')
    if kw.get('memory_maps') or 'memory_maps' in filter:
        pa.append('memory_maps')
    n = dict([(k, getattr(p, k)()) for k in pa])
    for s in subs:
        v = n.get(s)
        if v:
            n[s] = pu2s(v)
    for fn in 'threads', 'open_files':
        n[fn] = [pu2s(t) for t in n.get(fn, [])]

    ns = n.pop('connections', 0)
    if ns:
        try:
            n['conn'] = [{'l': pu2s(c.laddr), 'r': pu2s(c.raddr)} for c in ns]
        except Exception as ex:
            n['conn'] = []

    m.update(n)
    tree = kw.get('tree', 0)
    if tree:
        kw['tree'] = tree - 1
        m['c'] = [dump_proc(pc, **kw) for pc in p.children()]
    return m


class AppFunctions:
    """The app API, within a daemon env"""

    class systemctl:
        def __init__(self, m, *a):
            getattr(self.__class__, m)(*a)

        @staticmethod
        def cmd(_cmd):
            """called from to stop, start, ..."""
            l = ['systemctl', '--no-pager', _cmd, pyenv('name_unit')]
            l.insert(1, '--user') if os.geteuid() else ''
            return run_proc(l)

    sc = systemctl

    class os:
        @classmethod
        def _proc(cls, all=False):
            # we do not need to rely on the pid file but have the process name:
            # 16 bytes proces names in unix
            verify_lib('psutil')
            n = AppFunctions.os.name()
            # we do not use the pid file but the process name:
            ps = [
                proc
                for proc in psutil.process_iter()
                if proc.name() == n and 'start' in proc.cmdline()
            ]
            if all:
                return ps
            # e.g. '/home/gk/devapps/test/wifi_single/run/AXWiFi.Hub'
            n = pyenv('app_run_exe_link')
            # loop thru ALL processes and find the one matching exe_link and 'start':
            return [pi for pi in ps if n in pi.cmdline()]

            return ps

        @classmethod
        def proc(
            cls,
            pid=-1,
            env=False,
            memory_maps=False,
            filter='',
            tree=0,
            parent=False,
            all=False,
        ):
            """Extensive process info

            pid: Main app process if not given
            env: Include process environ
            memory_maps: Include memory_maps (loaded libs)
            filter: filter on substring
            tree: Include children down to this level 
            
            """
            l = dict(locals())
            ps = [psutil.Process(pid)] if pid > -1 else cls._proc(all=all)
            if parent:
                ps = [psutil.Process(p.parent().pid) for p in ps]

            return [dump_proc(p, **l) for p in ps]

        @classmethod
        def name(cls):
            """"""
            # e.g. hub.axwifi
            # 16 bytes proces names in unix
            return pyenv('app_run_script')[:15]

        @classmethod
        def pid(cls, all=False):
            """
            Returns pid of process matching $app_run_exe_link and 'start'
            
            all: Return ALL started processes with our name, in a list
            (started in any DA_DIR, within the pid namespace)
            """
            ps = AppFunctions.os._proc(all=all)
            if not all:
                return ps[0].pid if ps else None
            else:
                return [pi.pid for pi in ps]

        @classmethod
        def signal(cls, sig=int(signal.SIGTERM), ignore_not_found=False, all=False):
            """Send a signal to the running process"""
            sig = int(sig)
            ps = AppFunctions.os._proc(all=all)
            if ps:
                pids = [p.pid for p in ps]
                app.info('Sending signal', pid=pids, signal=sig)
                [os.kill(p, sig) for p in pids]
            else:
                if not ignore_not_found:
                    app.error('Process not found')

        @classmethod
        def poll(cls, freq=100, max=60000, on_success=None):
            p, t1, maxm = None, time.time(), max / 1000.0
            while time.time() < (t1 + maxm):
                p = cls.pid()
                if p:
                    break
                time.sleep(freq / 1000.0)
            if not p:
                sys.exit(1)
            if on_success:
                app.info('Running on_success handler', cmd=on_success)
                if os.system(on_success):
                    app.error('on_success handler failed', cmd=on_success)
                    sys.exit(1)
            return p

    class devapp:
        @staticmethod
        def env():
            return load.py_env

        @staticmethod
        def fs():
            with open(pyenv('build_dir') + '/fs_stack.json') as fd:
                return json.loads(fd.read())

        @staticmethod
        def links():
            with open(pyenv('build_dir') + '/links.json') as fd:
                return json.loads(fd.read())

        @staticmethod
        def clean(keep_running=False):
            un = pyenv('name_unit')
            if not keep_running:
                AppFunctions.systemctl.stop()
                AppFunctions.stop(ignore_not_found=True)
            for k in 'build', 'var':
                bd = pyenv(k + '_dir')
                if os.path.exists(bd) and len(bd.split('/')) > 3:
                    app.info('Removing directory', dir=bd)
                    run_proc(['rm', '-rf', bd])
            sd = units_dir() + '/' + un
            if os.path.exists(sd):
                app.info('Removing unit', unit=sd)
                os.unlink(sd)

    @staticmethod
    def status(short=True):
        p = AppFunctions.os._proc()
        app.info('Running') if p else app.die('Not running')

    # alias
    d = devapp


# sc.start, sc.stop:..
AF = AppFunctions
[
    setattr(AF.systemctl, k, partial(AF.sc.cmd, _cmd=k))
    for k in ('stop', 'start', 'restart', 'status', 'reload')
]

# reload, stop:.. (start is always mapped within the app module or to app_start)
[
    setattr(AF, k, partial(AF.os.signal, sig=sig))
    for k, sig in (
        ('stop', signal.SIGTERM),
        ('quit', signal.SIGQUIT),
        ('kill', signal.SIGQUIT),
        ('reload', signal.SIGHUP),
    )
]


def units_dir():
    return (
        os.environ['HOME'] + '/.config/systemd/user'
        if os.geteuid()
        else '/etc/systemd/system'
    )


def unit_files(da_name):
    d = units_dir()
    return [d + '/' + i for i in os.listdir(d) if '-%s.service' % da_name in i]


def da_name():
    return os.environ['DA_DIR'].rsplit('/', 1)[-1]


def set_da_dir_by_da_name(name, nofail=False):
    """This is questionable: Attempting to provide the convenient -n wifi to da util
    and rely on it deriving the right DA_DIR
    We had the option to write a $HOME/.local/devapps file at spec build mapping names to dirs
    but what if the spec is built elsewhere?
    So for now we look into the unit files.
    # todo: won't work for unit less utility builds though, then we need the mapping file for this

    Called by the CLI parser before run_app, i.e. we don't have app logging yet.
    """
    units = unit_files(name)
    if not units:
        if nofail:
            return None
        raise Exception('Cannot derive DA_DIR - no units')

    with open(units[0]) as fd:
        s = fd.read()

    env['DA_DIR'] = dd = (
        s.split('\nExecStart ', 1)[1].split('/build')[0].rsplit(' ', 1)[-1]
    )
    return dd


def import_and_expose_da_level_modules():
    """ import of modules only for da utility, not for apps"""
    from devapp.spec import build as sb
    from devapp.tools import exec_file

    DAFunctions.spec.build = sb.build
    DAFunctions.tools.exec_file = exec_file


def devapps_run():
    """
    The 'da' utility, wich is controlling the solution, not an app

    From setup.py: 'da=devapp.run:devapps_run',
    """
    import_and_expose_da_level_modules()

    flag.string('da_dir', '$DA_DIR', 'Solution directory', short_name='d')
    flag.string('da_name', '$DA_NAME', 'Solution name', short_name='n')
    args = sys.argv
    parse_flags_funcname_and_args(args, for_devapps=True)
    if not 'DA_DIR' in env:
        set_da_dir_and_name_from_current_directory()
    # special case: Help required:
    # the or is for: da -n wifi_single -h
    if is_help_intent() or RUN['func_name'] == 'bash' and not RUN['func_args']:
        f = DAFunctions
    else:
        f = get_func(DAFunctions)
    if callable(f):
        f = with_args(f)
        # sys.argv = RUN['argv']
        return run_app(f, wrapper=wrapped_app_func)
    # he called a command line program:
    f = partial(run_exit, parametrize_external_process())
    run_app(f, wrapper=partial(wrapped_app_func, ext_proc=True))


is_help_intent = lambda: len(sys.argv) == 2 and sys.argv[-1] in [
    '-h',
    '-hh',
    '--help',
    '-hhh',
    '--helpfull',
]


def wrapped_app_func(f, ext_proc=False):
    """apps have the PATH in their environ. Only via this flag we can allow
    additional PATH entries within apps processes
    """
    if FLG.show:
        if not ext_proc:
            from theming.absl_color_help import call_doc

            call_doc(f, level=3, render=True)
            return

    if FLG.add_path:
        have = env['PATH'].split(':')
        [have.insert(0, i) for i in reversed(FLG.add_path.split(':')) if not i in have]
        env['PATH'] = ':'.join(have)
    return f()


def add_app_functions_for_usage_help():
    """-h lists all app functions - we want these here as well:"""
    procs = []
    for k, v in pyenv('functions', {}).items():
        # convention: {'foo': ['a', 'b']} -> a is a process ,b param for it - python functions
        # will be anyway in the list:
        if isinstance(v, list):
            f = partial(app_run_exit, v)
            setattr(AppFunctions, k, partial(app_run_exit, v))
            procs.append(k)
    return procs


def app_run(args):
    """
    The app_run scripts in build/bin call this - from python

    - Unsharing done outside of us
    - FS is built (we dropped building at start up time - not yet sure regarding unshared changes, os.system unshare -> FS run, recall from caller

    Find what to run:
    e.g. for sys.argv = '--log_level=10 start':

    - We do not support supplying an app.module on the cli, i.e. for devapp all cmds must be in app module as funcs
    - We do support a nested api within the app module though

    """
    # func_names: 'start', 'metrics.get', 'stop', 'redis-server'
    # dash flags before and after
    # procs = add_app_functions()
    # this builds the aliases:

    # TODO: This is a mess and needs rework when the app is NOT a function - parametrize_external_process should not be needed
    # or be simpler, i.e. this must do that work already:
    parse_flags_funcname_and_args(args)
    func_name = RUN['func_name']

    ApplicationFunctions = AppFunctions

    if load.app_mod:

        if func_name == 'start':
            # app was importable, for devapps run['start'] = '<modulename>' -> ignored:
            add_prod_flagfile()
            register_signals(proc_signal_handler)
            return run_app(load.app_mod.start, wrapper=wrapped_app_func)

        appns = getattr(load.app_mod, 'Functions', None)
        if appns:

            class ApplicationFunctions(appns, AppFunctions):
                pass

    f = get_func(ApplicationFunctions)

    if is_help_intent():
        add_app_functions_for_usage_help()
        f = ApplicationFunctions

    if callable(f):
        f = with_args(f)
        add_prod_flagfile()
        return run_app(f, wrapper=wrapped_app_func)

    # this is a subproc run. Lets run it under an initiazlied dev_app proc, i.e. get
    # the flags:
    f = partial(app_run_exit, parametrize_external_process())
    run_app(f, wrapper=partial(wrapped_app_func, ext_proc=True))


pidfile = lambda: env['pidfile']
pidstarter = lambda: env['var_dir'] + '/pidfile.starter'


def add_prod_flagfile():
    pf = pyenv('etc_dir') + '/prod.flags'
    if exists(pf) and '--flagfile' not in sys.argv:
        sys.argv.append('--flagfile')
        sys.argv.append(pf)


def write_pid(sp_pid=None, remove=False):
    # is given for spawned ones else its ours:
    pidst = os.getpid()
    # for devapps both are ident:
    for fn, p in (pidfile(), sp_pid), (pidstarter(), pidst):
        if remove:
            if os.path.exists(fn):
                os.remove(fn)
        else:
            write_file(fn, str(p) + '\n', mkdir=True)


def app_run_exit(args):
    return run_exit(args, for_app=True)


def run_exit(args, for_app=False):
    """Run a subprocess"""
    # TODO: basic support for && and pipes
    # User called another function or process but we do warn him about that:
    # only now we can report this:
    if not for_app and os.path.exists(FLG.da_dir):
        app.debug('cd', dir=FLG.da_dir)
        os.chdir(FLG.da_dir)

    if load.app_import_err:
        app.error('App import error', exc=load.app_import_err)

    sys.exit(run_proc(args, for_app=for_app, handle_sigs=True))


def run_helper(args):
    """args can refer to inner commands, in order to gather values"""
    proc = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
    res = proc.communicate()
    if proc.returncode != 0:
        app.die('Failing', args=args, out=res[0], err=res[1])
    r = res[0].decode('utf-8')
    if r and r[-1] == '\n':
        r = r[:-1]
    return r


def run_proc(args, for_app=False, handle_sigs=False):
    args = [run_helper(a) if isinstance(a, list) else a for a in args]
    args = [str(l) for l in args]
    if FLG.show:
        s = lambda i: '"%s"' % i if not i.startswith('-') else i
        app.info('Dry Run', cmdline=' '.join([s(a) for a in args]))
        return 0
    # raises:
    try:
        proc = sp.Popen(args)
    except Exception as ex:
        app.error(
            'Command run error',
            cmd=args[0],
            args=args[1:],
            err=ex,
            pid_starter=os.getpid(),
        )
        raise
    app.debug(args[0], args=args[1:], pid=proc.pid, pid_starter=os.getpid())
    if handle_sigs:
        # for app:
        register_signals(partial(proc_signal_handler, pid=proc.pid))

    proc.communicate()
    return proc.returncode


# SIGKILL we would not see, anyway:
termsigs = signal.SIGINT, signal.SIGTERM, signal.SIGQUIT

app_sig_catchers = {
    signal.SIGHUP: 'reload',
    signal.SIGQUIT: ['quit', 'stop'],
    signal.SIGTERM: 'stop',
    signal.SIGINT: ['interrupt', 'stop'],
}


def get_handler(mod, catcher):
    if not catcher:
        return
    if isinstance(catcher, str):
        return getattr(mod, catcher, None)
    return getattr(mod, catcher[0], None) or getattr(mod, catcher[1], None)


def proc_signal_handler(sig, frame, pid=None):
    if load.app_mod:
        c = app_sig_catchers.get(sig)
        f = get_handler(load.app_mod, c)
        if f:
            fn = getattr(f, '__qualname__', f)
            app.warn('Calling %s' % fn, signal=sig, func=fn)
            f()
        else:
            app.warn('No signal handler for %s' % str(c), signal=sig)

    if pid:
        try:
            # kill -QUIT <this master process pid> should -9 the child:
            if sig == signal.SIGQUIT:
                app.warn('KILLING HARD (SIGKILL)', pid=pid)
                os.kill(pid, signal.SIGKILL)
            else:
                # forwarding:
                app.warn('Signal', signal=sig, pid=pid)
                os.kill(pid, sig)
        except Exception as ex:
            app.error('Could not send signal', pid=pid, signal=sig, exc=ex)
    if sig in termsigs:
        if pid:
            write_pid(pid, remove=True)
        sys.exit(1)


def register_signals(handler):
    # signal.SIGTSTP is forwarded to the child (tested: redis)
    [signal.signal(s, handler) for s in termsigs]
    signal.signal(signal.SIGHUP, handler)


# process = [proc for proc in psutil.process_iter() if proc.name == "YourProcess.exe"].


if __name__ == '__main__':
    app_run(args=sys.argv)


# cheap function finder and sig mapper.
# TODO: re-use the stuff from axc2, with parametrz.
# classes and recursive defaults.
# attrs or dataclasses ?

RUN = {'argv_orig': [], 'argv': [], 'func_args': [], 'func_name': None}


def parametrize_external_process():
    """ External process -> all flags before "func_name" (which is the process) belong to flags, 
    rest is process args, e.g. --log_level debug tree -L 2"""
    argv = RUN['argv_orig']
    pos = argv.index(RUN.get('func_name_aliased') or RUN['func_name'])
    sys.argv.clear()
    sys.argv.extend(argv[:pos])
    return argv[pos:]


def parse_flags_funcname_and_args(sys_argv, for_devapps=False):
    """Fills the RUN structure """

    def get_all_flags():
        from absl import app

        m = app.FLAGS.flags_by_module_dict()
        l = {}
        for k, v in m.items():
            for f in v:
                l['--%s' % f.name] = f
                l['-%s' % f.short_name] = f
        return l

    fn = None
    RUN['argv_orig'].extend(sys_argv)
    defined_flags = get_all_flags()
    RUN['argv'].append(sys_argv[0])  # the main program (this)
    l = sys_argv[1:]
    while l:
        a = l.pop(0)
        if a.startswith('-'):
            if for_devapps:
                set_da_dir_and_name_from_cli_param(a, args=l)
            RUN['argv'].append(a)
            f = defined_flags.get(a)
            if f and not 'Bool' in str(f):
                if not l:
                    raise Exception('Value required for %s' % a)
                RUN['argv'].append(l.pop(0))
        else:
            if not fn:
                aliased = pyenv('functions', {}).get(a)
                if aliased:
                    av = RUN['argv_orig']
                    avo = list(av)
                    av.clear()
                    av.extend(avo[: len(RUN['argv'])])
                    av.extend(aliased)
                    av.extend(l)
                    RUN['func_name_aliased'] = aliased[0]
                RUN['func_name'] = fn = a
            else:
                RUN['func_args'].append(a)
    if not fn:
        RUN['func_name'] = 'bash'
        # add the da path into the environ if not in yet for the bash env:
        RUN['argv_orig'] = RUN['argv'] + [
            'bash',
            '--rcfile',
            '%s/shell/activate' % devapps_dir(),
        ]


def _cli_val(a, args):
    return a.split('=', 1)[1] if '=' in a else args[0]


def set_da_dir_and_name_from_current_directory():
    p = os.getcwd()
    while len(p) > 2:
        if exists(p + '/conf/SPEC.py'):
            env['DA_DIR'] = p
            return
        p = p.rsplit('/', 1)[0]


def set_da_dir_and_name_from_cli_param(a, args):
    # Already before run_app is called we export DA_DIR and DA_NAME
    # if given - since they are fundamental
    if a.startswith('--da_dir') or a == '-d':
        env['DA_DIR'] = _cli_val(a, args)
        env['DA_NAME'] = env['DA_DIR'].rsplit('/', 1)[-1]
    elif a.startswith('--da_name') or a == '-n':
        env['DA_NAME'] = _cli_val(a, args)
        if not 'DA_DIR' in env:
            set_da_dir_by_da_name(env['DA_NAME'], nofail=True)


def devapps_dir():
    """returning the directory of the devapps repo, i.e. where shell, python, ... directories are"""
    import structlog

    # we run da to get here, i.e. our env is base/envs/devapps -> structlog is within
    # Only restriction: the devapps env must be in default location of the base env
    # (and devapps always the repo version, which is in the base package)
    return structlog.__file__.rsplit('/envs/')[0] + '/repos/devapps'


def get_func(ns):
    fn = RUN['func_name']
    parts, h = fn.split('.'), []
    while parts:
        h.append(parts.pop(0))
        ns = getattr(ns, h[-1], None)
        if not ns:
            return None if len(h) == 1 else '.'.join(h)
    return ns


def auto_type(v):
    for k, b in ('true', True), ('false', False):
        if str(v).lower() == k:
            return b
    for typ in int, float:
        try:
            return typ(v)
        except:
            pass
    if not v:
        return ''
    return str(v)


def with_args(f):
    """f is a function an we have its args -> return a parametrized version, ready for run_app"""
    # get command args:
    sig = signature(f).parameters
    sigv = list(sig.values())
    a, kw, have = (), {}, []

    def sig_type(v, P):
        if not P:
            return auto_type(v)
        elif P.default is None:
            return v
        elif P.default is _empty:
            return auto_type(v)
        # foo=bool (type w/o a value. mypy later. maybe)
        elif isinstance(P.default, type):
            return P.default(v)
        elif isinstance(P.default, bool):
            return str(v).lower() in ['1', 'true']
        else:
            try:
                return type(P.default)(v)
            except Exception as ex:
                print('breakpoint set')
                keep_ctx = True

    # argv:
    for p in RUN['func_args']:
        if '=' in p:
            k, v = p.split('=', 1)
            P = sig.get(k)
            kw[k] = sig_type(v, P)

        else:
            P = None
            while sigv and not P in have:
                P = sigv.pop(0)
                have.append(P)
            a += (sig_type(p, P),)
    # wrap command function with args:
    f = partial(f, *a, **kw)
    return f
