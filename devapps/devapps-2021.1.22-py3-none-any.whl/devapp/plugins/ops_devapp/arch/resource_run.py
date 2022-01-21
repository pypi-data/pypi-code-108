#!/usr/bin/env python
"""
Running installed resources.

"""


import os, sys, json, time
from functools import partial

from devapp import app
from . import _resources_api as api
from devapp.tools import (
    FLG,
    project,
    exists,
    jsondiff,
    write_file,
    read_file,
    offset_port,
    wait_for_port,
)

app, run_app, do, system = app.app, app.run_app, app.do, app.system
from . import resources_list as rscsl
from subprocess import Popen

g = api.g
S = api.S


class Flags(rscsl.Flags):
    """Simple Process Start/Stop, Intended for Dev and Py-Testing"""

    autoshort = ''

    class dir:
        n = 'Run command after changing to this directory'

    class cmd:
        n = 'Command. Must be last argument, argv after -- will be added. You can also encluse a full command into a string, e.g. "npm -h >/dev/null".'

    class background:
        s = 'bg'
        n = 'Run in background'
        d = False

    class await_port:
        n = 'Block until port is reachable, when run in background'

    class await_port_timeout:
        d = 10

    class show:
        n = 'Print out, not run the full command'
        d = False

    class kill:
        n = 'Kill matching running resource.'
        d = False

    class killall:
        s = 'ka'
        d = False

    class shell:
        n = 'Start a shell instead of running the command - but with the environment set.'
        d = False


# --------------------------------------------------------------------------- app

fn_run = lambda: project.root() + '/.running_resources.json'


def check_running():
    S.fn_run = fn = fn_run()
    r = json.loads(read_file(fn, dflt='{}'))
    S.running_at_start = r = {k: v for k, v in r.items() if alive(v)}
    write_file(fn, json.dumps(r, indent=4))


def alive(p):
    try:
        return not os.kill(p['pid'], 0)
    except:
        return False


def kill_resource():
    fn, r = S.fn_run, S.running_at_start
    for k, v in r.items():
        if not FLG.cmd in k and not FLG.killall:
            continue
        app.warn('Killing resource', cmd=k, **v)
        os.kill(v['pid'], 15)


def find_resource_by_cmd(cmd):
    a, args = sys.argv, []
    orig_cmd = cmd
    if '--' in sys.argv:
        args = a[a.index('--') + 1 :]
    cmd += ' ' + ' '.join(args)
    scmd, args = cmd.split(' ', 1)
    rsc = api.matching_resource(scmd)

    have = [rsc.cmd] + g(rsc, 'provides', [])
    sel = [c for c in have if scmd in c]
    if len(sel) > 1:
        app.info('more matches, trying exact match', matches=sel)
        sel = [c for c in sel if scmd == c]
    if not sel or len(sel) > 1:
        app.die('No match found', have=have)
    sel = sel[0]
    breakpoint()  # FIXME BREAKPOINT
    cmd = api.Run.find_resource_cmd(rsc, sel)
    breakpoint()  # FIXME BREAKPOINT
    return cmd


def create_run_file_entry(cmd, rsc, pid):
    fn, r = S.fn_run, S.running_at_start
    r[cmd] = {
        'pid': pid,
        'rsc': api.to_dict(rsc),
        'at': time.ctime(),
        'ts': time.time(),
    }
    write_file(fn, json.dumps(r, indent=4, sort_keys=True))


def run_foregrounded(cmd, rsc):
    do(create_run_file_entry, cmd=cmd, rsc=rsc, pid=os.getpid())
    return do(system, cmd)


def run_backgrounded(cmd, rsc):
    app.info('Backgrounding', cmd=cmd)
    fnull = open(os.devnull, 'w')
    p = Popen(cmd, stderr=fnull, stdout=fnull, shell=True, close_fds=True)
    do(create_run_file_entry, cmd=cmd, rsc=rsc, pid=p.pid)
    port = FLG.await_port or g(rsc, 'wait_port') or g(rsc, 'port')
    if port:
        port = offset_port(port)
        to = max(FLG.await_port_timeout, g(rsc, 'port_wait_timeout', 0))
        wait_for_port(port, timeout=to)
        app.info('Port open', port=port, cmd=cmd)
        time.sleep(0.2)


def run():
    if FLG.dir:
        os.chdir(FLG.dir)
    cmd = FLG.cmd
    check_running()

    if not cmd and not FLG.killall:
        return S.running_at_start
    if offset_port(1) != 1:
        app.warn('GLOBAL PORT OFFSET', offset=offset_port(0))
    if FLG.kill or FLG.killall:
        return kill_resource()

    cmd, rsc = do(find_resource_by_cmd, cmd=cmd)
    if cmd in S.running_at_start:
        return app.warn('Already running', cmd=cmd, **S.running_at_start[cmd])

    if FLG.show:
        return cmd
    if FLG.shell:
        if FLG.background:
            app.die('Cannot run a shell backgrounded')
        print('Running bash instead of:\n"%s"' % cmd)
        return os.system('bash')

    return do(run_backgrounded if FLG.background else run_foregrounded, cmd, rsc)


main = partial(run_app, run, flags=Flags)
