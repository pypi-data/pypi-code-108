#!/usr/bin/env python
"""
source env.sh
python -m devapp.run start

"""
import importlib
import json
import os
import subprocess as sp
import sys
import time

import psutil
from devapp.spec import tools as spec_tools
from devapp.tools import read_file, restart_unshared, write_file

[sys.path.append(p) for p in os.environ.get('sys_path_append', '').split(':')]


env = os.environ
exists = os.path.exists
FS = spec_tools.FS
Proc = psutil.Process


def out(msg, kw):
    print(
        msg, ', '.join(['%s=%s' % (k, str(v)) for k, v in kw.items()]), file=sys.stderr,
    )


# we don't have logging before we have the fileystem(flags)
def info(msg, **kw):
    out('Info: %s' % msg, kw)


def warn(msg, **kw):
    out('Warning: %s' % msg, kw)


def dbg(msg, **kw):
    out('Dbg : %s' % msg, kw)


def die(msg, **kw):
    out('Fatal: %s' % msg, kw)
    sys.exit(1)


class InitApp:
    """mocks devapp.app while we not yet have it on app initializing"""


InitApp.die = die
InitApp.dbg = InitApp.debug = dbg
InitApp.info = info


def verify_env_sourced():
    try:
        db = FS.d_build()
        fn_env = db + '/env.sh'
    except:
        die('Please source an env.sh file before running')
    if not exists(fn_env):
        die('App is not built yet, missing file', env_file=fn_env)
    # cur = env.get('build_dir', '')

    # if cur and cur == db:
    #    # already sourced via source env.sh (e.g. systemd - unit):
    #    return
    # from devapp.spec import os_tools

    # env.update(os_tools.source(fn_env, set_sys_path_from_py_path=True))


now = lambda: int(time.time() * 1000)
is_svc = lambda: env['type'] == 'Service'
dirname = os.path.dirname
pidfile = lambda: env['var_dir'] + '/pidfile'
pidmain = lambda: env['var_dir'] + '/pidfile.main'
unit_name = lambda: env.get('name_unit')


def from_pidfile():
    i = int(read_file(pidfile(), -1))
    return i if psutil.pid_exists(i) else 0


# default if user provided nothing else:
bash = lambda: ['bash', '--rcfile', '%(DA_DIR_DEVAPPS)s/shell/bashrc' % env]


def write_pid(pid=None):
    # is given for spawned ones else its ours:
    pid = pid or os.getpid()
    # for devapps both are ident:
    for fn, p in (pidfile(), pid), (pidmain(), LifeCycle.main_pid):
        write_file(fn, str(p) + '\n', mkdir=True)


def run_exit(args):
    # TODO: basic support for && and pipes
    args = [str(l) for l in args]
    proc = sp.Popen(args)
    write_pid(proc.pid)
    proc.communicate()
    sys.exit(proc.returncode)


def js_to_struct(s, dflt=list):
    r = dflt() if not s else s
    return json.loads(r) if isinstance(r, str) else r


def is_in_run_dir(mod):
    dr = env['run_dir']
    if exists(dr + '/%s.py' % mod):
        sys.path.insert(0, dr) if not dr in sys.path else 0
        return True


class LifeCycle:

    main_pid = None

    def run(argv_cmd=None):
        """argv_cmd != None if user just wants to enter filesystem
        If so and servie is nspawn -> we nspawn without boot.
        otherwise we run his cmd (default bash)
        """
        breakpoint()
        LifeCycle.main_pid = os.getpid()
        env['DA_INITTED'] = ''  # $PATH exports done in init

        FS.initapp = InitApp
        FS.build_from_fs_stack()

        appl, app_mod = [env.get('app')], None
        if (not '/' in appl[0] and '.' in appl[0]) or is_in_run_dir(appl[0]):
            try:
                # exists not -> must be devapp module:
                app_mod = importlib.import_module(appl[0])
            except Exception as ex:
                warn('Cannot import app_module', mod=appl[0], exc=ex)

                # die('Cannot import %s:' % appl[0], error=ex)

        app_args = js_to_struct(env.get('app_args'), list)
        # the pid we keep is not ours and also not that of the inner init
        # but that of nspawn, which propagates graceful termination of inner services:
        if argv_cmd:
            if appl == ['systemd-nspawn']:
                for b in '--boot', '-b':
                    app_args.remove(b) if b in app_args else ''
                argv_cmd = appl + app_args + argv_cmd
            run_exit(argv_cmd)

        if not app_mod:
            run_exit(appl + app_args)

        # ok - inline (r/f)un:
        write_pid()  # yup, thats us :-)
        flagfile, flags = '', env.get('DA_FILE_FLAGS', 'prod')
        if '/' in flags:
            flagfile = flags
            if not exists(flagfile):
                die('Not found', flagfile=flagfile)
        else:
            for d in 'conf_dir', 'etc_dir':
                fn = env.get(d) + '/%s.flags' % flags
                if exists(fn):
                    flagfile = fn
                    break
        if flagfile:
            # The implicit find-by-presence of flagfiles is nice but absl-py
            # must see the --flagile argument. Not PC but we have to tune the
            # sys.argv for this. Oh, and being at it, lets streamline $0 as
            # well:
            # DA_CLS results in app.name which determines the folder where
            # secrets are searched, e.g. hub -> LEAVE!:
            sys.argv.insert(1, flagfile)
            sys.argv.insert(1, '--flagfile')
            # sys.argv.insert(0, env['DA_CLS'])
        info('DevApp', app=appl, args=sys.argv)
        # sys.path.append('/data/f3/repos/axess-4/streampipes.git/src')
        app_mod.run()

    def procs():
        """
        Main: This is us - the python program which runs inline - OR spawns the
        child process, like nspawn
        Enter: The proc for nsenter. For nspawn:boot the grand child, i.e. init
        = Main for devapps.
        Kill: This is the one in the pid file.
        The pid which gracefully terminates all childs, i.e. nspawn for those
        (not init).  Main for devapps.
        """

        pkill, pmain = read_file(pidfile(), 0), read_file(pidmain(), 0)
        # don't trust pidfiles:
        try:
            PK, PM = Proc(int(pkill)), Proc(int(pmain))
            # proc is running
            rt = env.get('runtime', '')
            PE = PK
            if rt == 'systemd:boot':
                PE = PK.children()[0]
        except:
            PM, PK, PE = None, None, None
        return {'proc_main': PM, 'proc_kill': PK, 'proc_enter': PE}

    def is_systemd(procs=None):
        P = (procs if procs else LifeCycle.procs())['proc_main']
        return None if not P else True if P.parent().pid == 1 else False

    is_running = lambda: bool(LifeCycle.procs()['proc_kill'])

    def pids():
        m = {}
        for k, P in LifeCycle.procs().items():
            m[k.replace('proc_', 'pid_')] = P.pid if P else 0
        return m

    def enter():
        ep = LifeCycle.pids()['pid_enter']
        if not ep:
            die('Not running', process=env['DA_CLS'])
        env['DA_INITTED'] = ''  # causes init. (for PATH). nsenter keeps env
        c = ('nsenter -t %s -m -u -i -n -p --' % ep).split(' ')
        c.extend(argv_cmd())
        sys.exit(sp.call(c))

    def status():
        """ for linux """
        LC, pids = LifeCycle, dict(LifeCycle.pids())
        pids['unit'], runs = unit_name(), pids['pid_main']
        m, msg = (app.info, 'Is Running') if runs else (app.warn, 'Is stopped')
        m(msg, **pids)
        sys.exit(0 if runs else 1)

    def show():
        """Svc started by systemd OR manually - then we check pidfile"""
        st = ['systemctl', 'show', unit_name(), '--no-page']
        out, err = sp.Popen(st, stdout=sp.PIPE, stderr=sp.PIPE).communicate()
        out = out.decode('utf-8').splitlines()
        d = dict([(k, v) for k, v in [l.split('=', 1) for l in out]])
        d.update(LifeCycle.pids())
        return d

    def stop():
        # nginx needs special stopping:
        stp = js_to_struct(env.get('service_exec_stop', []))
        if stp:
            sys.exit(sp.call(stp))
        procs = LifeCycle.procs()
        if LifeCycle.is_systemd(procs):
            # he can do it better than us. Plus we don't want auto-restarts:
            sys.exit(sp.call(['systemctl', 'stop', unit_name()]))
        if not procs['proc_kill']:
            return info('Not running')
        os.kill(procs['proc_kill'].pid, 13)

    def fs(*args):
        """just build the fs of a service"""
        LifeCycle.start(argv_cmd())

    def not_impl():
        raise Exception('Not Supported')

    def pstree(depth=2):
        procs = LifeCycle.procs()
        if not procs['proc_kill']:
            return {}

        def walk(P):
            tree = {}
            tree[P.pid] = m = {'proc': P}
            childs = P.children()
            if childs:
                m['tree'] = mc = []
                for c in childs:
                    mc.append(walk(c))
            return tree

        return walk(procs['proc_main'])

    def systemctl(*args):
        """Adding the unit name to systemctl when it makes sense"""
        if not args:
            args = ('status',)
        args = list(args)
        if args[0] == 'status' or (
            len(args) == 1 and not args[0][:4] in (['list', 'daem'])
        ):
            args.append(unit_name())
        if os.geteuid():
            args.insert(0, '--user')
        app.info(' '.join(['/usr/bin/systemctl', *args]))
        sys.exit(sp.call(['/usr/bin/systemctl', *args]))

    sc = systemctl  # shortcut


argv_cmd = lambda: sys.argv[2:] or bash()


def _main():
    verify_env_sourced()
    m = getattr(LifeCycle, sys.argv[1], LifeCycle.not_impl)
    res = m(*sys.argv[2:])
    return res


def main():
    a = sys.argv
    # auto on no args:
    if len(a) == 1 or not getattr(LifeCycle, a[1], None) or a[1] == 'main':
        # main is auto: enter or fs, depending on running or not
        # if LifeCycle.is_running():
        #    a.insert(1, 'enter')
        # else:
        # Changed that to always just enter filesystem (nsenter requires root):
        # also when he entered before the start it would be confusingly different
        a.insert(1, 'fs')

    if sys.argv[1] in ('start', 'fs'):
        # we assume the user who builds is the user who starts. If root we allow unshare requiring fs components
        # for user we are not there yet, examining bubblewrap or podman user mode... but not yet supported
        # I.e. we only need to unshare when we are root right now:
        if not os.geteuid():
            # if not int(os.getppid()) == 1 and (not os.geteuid() or 1):
            # if systemd starts us we took care that the unit file has unshare in the
            # ExecStart - IF needed. For normal users we unshare when he goes into
            # daemon FS:
            # If normal user does absolutely not want unshared entries he can export
            # da_unshared=$DA_CLS (see this restart_unshared func):
            restart_unshared(env['DA_CLS'])

        # not parse flags yet if this is start:
        if sys.argv[1] in ('start',):
            sys.exit(_main())
    # ok this is not a start action where devapp.app must be the target app
    # (there can be ony one, alone for flags parsing)
    # So, WE are the one app:
    global app
    from devapp.app import app, run_app

    run_app(_main, flags_parser=extract_app_flags)


def extract_app_flags(args):
    """
    We solve the tricky problem that we want for non start runs, i.e. where
    WE are the devapp the parsing of standard flags like --log_level - but also
    not crash for "flag-style" args like -lta in `fs --log-level=10 ls -lta`
    The solution is this custom parser, which stops at first non '-' arg when
    handing over to FLAGS
    """
    from absl import flags

    a, meth_args = args[:2], []
    into = a
    for p in args[2:]:
        if not p.startswith('-'):
            into = meth_args
        into.append(p)
    res = flags.FLAGS(a)
    sys.argv.clear()
    sys.argv.extend([*res[:2], *meth_args])
    return sys.argv


if __name__ == '__main__':
    main()
