#!/usr/bin/env python
"""
Service Lifecycle Operations

Only for services where systemd units had been created
"""
# Could be done far smaller.
from re import match
from devapp import gevent_patched
import hashlib
import json
import os
import shutil
from copy import deepcopy
from functools import partial
import sys

import requests
from devapp.app import FLG, app, run_app, do, system
from devapp import tools
from devapp.tools import (
    exists,
    to_list,
    repl_dollar_var_with_env_val,
    project,
    read_file,
    write_file,
)
import devapp.resource_tools as api


class Flags(api.CommonFlags):
    autoshort = ''

    class match:
        n = 'Restrict to matching units'
        d = ''

    class stop_all:
        n = 'When given we kill ALL processes occupying the port of a service'
        d = False


S = api.S


def run():
    argv = sys.argv[2:]
    if FLG.match:
        argv = argv[2:]

    d = project.root()
    db = d + '/bin'
    if not exists(db):
        app.die('Not in project dir with bin directory', required=db)
    wrappers = {}
    units = []
    for u in os.listdir(db):
        s = wrappers[u] = read_file(db + '/' + u, dflt='')
        if 'systemctl ' in s and FLG.match in u:
            units.append(u)
    if not units:
        msg = 'No units - we can only manage services where unit files had been created'
        app.die(msg)
    app.info('units', units=units)
    if FLG.stop_all:
        argv = ['stop']
        app.warn('Stop all is set - we stop everything at unit ports')
    else:
        if not argv:
            argv = ['status']

    cmd = ' '.join(argv)
    for u in units:
        if cmd == 's':
            cmd = 'start'
        app.info(cmd + ' ' + u)
        do(system, db + '/' + u + ' ' + cmd, no_fail=True)

    if cmd == 'start':
        show_failing(units, db)
    elif FLG.stop_all:
        [stop_all(unit, wrappers[unit]) for unit in units]


def get_unit(pid):
    u = os.popen('systemctl --user status %s | head -n 1 | cut -d " " -f 2' % pid)
    return u.read().strip()


def stop_all(unit, wrapper):
    port = wrapper.split('port=', 1)
    if not len(port) - 1:
        return
    port = int(port[1].split('\n', 1)[0].replace('"', '').replace("'", ''))
    pids = os.popen('lsof -ti tcp:%s' % port).read().strip().splitlines()
    if not pids:
        return
    app.info('killing other %s at port %s' % (unit, port), pids=pids)
    for p in pids:
        unit = get_unit(p)
        if unit:
            do(system, 'systemctl --user stop "%s"' % unit)
            continue
        os.kill(int(p), 15)
        app.info('killed', pid=p)


def show_failing(units, db):
    errs = []
    for u in units:
        err = os.system(db + '/' + u + ' status >/dev/null')
        if err:
            os.system(db + '/' + u + ' status')
            errs.append(u)
    if errs:
        app.die('Could not start', services=errs)


main = lambda: run_app(run, flags=Flags)


if __name__ == '__main__':
    main()
