#!/usr/bin/env python
"""
Simple process maintainance tools (intended for CI tests)

"""


import os, sys, json, time
from functools import partial

from devapp import app
from devapp.tools import (
    FLG,
    project,
    exists,
    jsondiff,
    write_file,
    read_file,
    offset_port,
    wait_for_port,
    repl_dollar_var_with_env_val,
)

now = time.time
app, run_app, do, system = app.app, app.run_app, app.do, app.system
from subprocess import Popen


class Flags:
    """Simple Process Start/Stop, Intended for Dev and Py-Testing"""

    autoshort = ''

    class dir:
        n = 'Change to this dir before running. env vars supported'

    class cmd:
        n = 'Process to run, with args - will be evalled'

    class background:
        s = 'bg'
        n = 'Run in background'
        d = False

    class await_port:
        n = 'Block until port is reachable, when run in background'
        d = 0

    class await_port_timeout:
        d = 10

    class kill_by_port:
        n = 'Kill matching running resource. Requires lsof'
        d = 0

    class kill_signal:
        d = 15


# --------------------------------------------------------------------------- app


fn_run = lambda: project.root() + '/tmp/running_processes.json'

run_file = lambda: json.loads(read_file(fn_run(), dflt='{}'))


def create_run_file_entry(cmd, pid):
    r = run_file()
    r[cmd] = {
        'pid': pid,
        'at': time.ctime(),
        'ts': time.time(),
    }
    # todo: maintain the file here(check pids, remove)
    write_file(fn_run(), json.dumps(r, indent=4, sort_keys=True), mkdir=True)


def run_foregrounded(cmd):
    pid = os.getpid()
    create_run_file_entry(cmd, pid)
    return do(system, cmd)


def run_backgrounded(cmd):
    app.info('Backgrounding', cmd=cmd)
    fnull = open(os.devnull, 'w')
    t0 = now()
    p = Popen(cmd, stderr=fnull, stdout=fnull, shell=True, close_fds=True)
    port = FLG.await_port
    if port:
        to = FLG.await_port_timeout
        wait_for_port(port, timeout=to)
        if now() - t0 > to:
            app.error('Port not open - killing hard', port=port, cmd=cmd)
            os.kill(p.pid, 9)
            app.die('App did not start', cmd=cmd)
        app.info('Port open', port=port, cmd=cmd)
        time.sleep(0.2)
        do(create_run_file_entry, cmd=cmd, pid=p.pid)


def kill_by_port(port):
    cmd = 'lsof -n -i :%s |grep LISTEN' % port
    r = os.popen(cmd).read().split()
    if len(r) > 2 and r[1].isdigit():
        sig = FLG.kill_signal
        app.warn('killing', port=port, pid=int(r[1]), signal=sig)
        try:
            os.kill(int(r[1]), sig)
        except Exception as ex:
            app.die('Could not kill', port=port, pid=int(r[1]), signal=signal)
    else:
        app.die('Not found open', port=port)


def run():
    if FLG.dir:
        os.chdir(repl_dollar_var_with_env_val(FLG.dir))
    p = FLG.kill_by_port
    if p:
        do(kill_by_port, port=p)
    cmd = FLG.cmd
    if cmd:
        return do(run_backgrounded if FLG.background else run_foregrounded, cmd)


#     check_running()

#     if not cmd and not FLG.killall:
#         return S.running_at_start
#     if FLG.kill or FLG.killall:
#         return kill_resource()

#     cmd, rsc = do(find_resource_by_cmd, cmd=cmd)
#     if cmd in S.running_at_start:
#         return app.warn('Already running', cmd=cmd, **S.running_at_start[cmd])

#     if FLG.show:
#         return cmd
#     if FLG.shell:
#         if FLG.background:
#             app.die('Cannot run a shell backgrounded')
#         print('Running bash instead of:\n"%s"' % cmd)
#         return os.system('bash')


main = partial(run_app, run, flags=Flags)


# def check_running():
#     S.fn_run = fn = fn_run()
#     r = json.loads(read_file(fn, dflt='{}'))
#     S.running_at_start = r = {k: v for k, v in r.items() if alive(v)}
#     write_file(fn, json.dumps(r, indent=4))


# def alive(p):
#     try:
#         return not os.kill(p['pid'], 0)
#     except:
#         return False


# def kill_resource():
#     fn, r = S.fn_run, S.running_at_start
#     for k, v in r.items():
#         if not FLG.cmd in k and not FLG.killall:
#             continue
#         app.warn('Killing resource', cmd=k, **v)
#         os.kill(v['pid'], 15)


# def find_resource_by_cmd(cmd):
#     a, args = sys.argv, []
#     orig_cmd = cmd
#     if '--' in sys.argv:
#         args = a[a.index('--') + 1 :]
#     cmd += ' ' + ' '.join(args)
#     scmd, args = cmd.split(' ', 1)
#     rsc = api.matching_resource(scmd)

#     have = [rsc.cmd] + g(rsc, 'provides', [])
#     sel = [c for c in have if scmd in c]
#     if len(sel) > 1:
#         app.info('more matches, trying exact match', matches=sel)
#         sel = [c for c in sel if scmd == c]
#     if not sel or len(sel) > 1:
#         app.die('No match found', have=have)
#     sel = sel[0]
#     breakpoint()  # FIXME BREAKPOINT
#     cmd = api.Run.find_resource_cmd(rsc, sel)
#     breakpoint()  # FIXME BREAKPOINT
#     return cmd
