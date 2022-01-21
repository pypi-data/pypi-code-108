#!/usr/bin/env python
"""
Installing Local Resources (e.g. Databases and Tools)

Does install into directories without affecting the host setup

Uses
- Miniconda 
- Container image pulling

Maintains a .resources file within the project root for looking up install state from elsewhere

API:
    - python: E.g. pytest can run: get_redis_exe = lambda: project.get_present_resource_location('redis-server')
    - shell:  Use jq
"""


import os
from functools import partial

from devapp import app
from devapp.tools import FLG, project, exists, jsondiff, write_file, to_list

from . import _resources_api as api

app, run_app, do, system = app.app, app.run_app, app.do, app.system
g = api.g
inst_modes = ['', 'host', 'conda']

# resources = ['miniconda', 'redis-server', 'graph-easy']


class Flags(api.CommonFlags):
    autoshort = ''

    class force:
        n = '-y on all questions at install/uninstall'
        d = False

    class do_list:
        n = 'Output list of resources'
        d = True

    class do_install:
        n = 'Install comma seperated list of resources (match is enough)'
        d = []


S = api.S

# ------------------------------------------------------------------------ tools
present = lambda cmd: bool(os.popen('type "%s" 2>/dev/null' % cmd).read())


# ------------------------------------------------------------------------ actions


def install(match):
    rsc = api.matching_resource(match)
    return api.Install.resource(rsc)


# pkg_cmds = ['apt-get', 'dnf', 'yum']
# def pkgcmd():
#     c = S.pkg_cmd
#     if not c:
#         c = [k for k in pkg_cmds if present(k)]
#         c = c[0] if c else app.die('no package command', tried=pkg_cmds)
#     if c == 'dnf':
#         c += ' --color=false '
#     return c
# def install_host(rsc):
#     if rsc.installed:
#         return app.warn('already installed - skipping', rsc=rsc)
#     cmd = 'sudo %s install %s "%s" ' % (pkgcmd(), interactive(), rsc.pkg)
#     return do(system, cmd)


import json


def write_installed_resources(rscs):
    j = {}
    fn = project.fn_resources()

    # for rsc in rscs:
    #     j[rsc.name] = m = {'location': rsc.installed, 'present': True}
    #     v = api.g(rsc, 'post_inst_verify', 'x')
    #     if v != 'x':
    #         m['post_inst_verify'] = rsc.post_inst_verify
    r = [api.to_dict(i) for i in rscs if i.installed]
    write_file(fn, json.dumps(r, indent=2))
    app.warn('have written resources file', fn=fn)
    return j


# --------------------------------------------------------------------------- app


def run():
    rscs = api.find_resource_defs()
    if not FLG.do_install:
        FLG.do_list = True
    else:
        if not FLG.install_state:
            api.add_install_state(rscs)

    if FLG.do_install:
        [do(install, match=k) for k in FLG.do_install]
        if S.rsc_modified:
            api.add_install_state(rscs)
        return do(
            write_installed_resources, rscs=[c for c in rscs.listed() if c.installed]
        )

    if FLG.do_list:
        return api.to_list(rscs)


main = partial(run_app, run, flags=Flags)
