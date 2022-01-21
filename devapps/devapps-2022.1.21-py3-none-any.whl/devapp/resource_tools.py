#!/usr/bin/env python
"""
Common API for all resources

"""
# FIXME Do this as state table! Its crying for that

import os, sys
import json
import time
from functools import partial
import importlib
from devapp.app import app, do, run_app, system
from devapp.tools import (
    offset_port,
    to_list as listed,
    FLG,
    project,
    deindent,
    exists,
    repl_dollar_var_with_env_val,
    dirname,
    write_file,
    read_file,
)

T_unit = '''
[Unit]
Description      = %(descr)s %(name)s
Wants            = network-online.target
StopWhenUnneeded = false

[Service]
Type             = simple

ExecStart        = %(exec_start)s
KillSignal       = SIGTERM
PrivateTmp       = true
Restart          = always
RestartSec       = 5
SendSIGKILL      = yes
TimeoutStopSec   = 5
SyslogIdentifier = %(name)s

[Install]
WantedBy = default.target

# _MATCH_ (auto created %(ctime)s) 
'''
unit_match = 'DevApp Unit'
T_unit = T_unit.replace('_MATCH_', unit_match)


class S:
    """state"""

    rscs_defined = None  # from resource_list
    pkg_cmd = None
    rsc_modified = False
    name_to_func = {}
    conda_prefix = None  # env vars replaced
    fs_dir = None  # filesystem install dest
    constants = {}
    rsc_dirs = {}


def add_const(key, val, skip_exists=True):
    """import order matters, i.e. 4A's flows file will overrule lc-py"""
    v = S.constants.get(key)
    if v is not None:
        app.warn('Overwriting constant %s' % key, have=v, new=val)
    S.constants[key] = val


def constant(key, dflt=None):
    v = S.constants.get(key, dflt)
    if v is None:
        app.die('Expected constant not found', key=key)
    return v


def into(m, k, v):
    m[k] = v


environ = os.environ


def cur_prefix():
    cli = os.environ.get('CONDA_PREFIX', '').split('/envs/', 1)[0]
    if not cli:
        app.die('No $CONDA_PREFIX currently set')
    return cli


def set_conda_prefix():
    """
    Resources install location, except filesystem based ones. Env vars resolved.

    Aliases:
    - local|l: <project_dir>/conda
    - default|d: $HOME/miniconda3 (default path of conda)
    - current|c: Any current conda_prefix set when running.
    
    Note: Installing resources outside the project keeps the project relocatable and resources reusable for other products.
    """

    cli = repl_dollar_var_with_env_val(FLG.conda_prefix)
    if not cli:
        cli = 'default'
    if cli in ('current', 'c'):
        cli = cur_prefix()
    elif cli in ('local', 'l'):
        cli = project.root() + '/conda'
    elif cli in ('default', 'd'):
        cli = os.environ['HOME'] + '/miniconda3'
    cli = os.path.abspath(cli)
    S.conda_prefix = cli


def set_fs_dir():
    """
    Filesystem based resource location. Env vars resolved.
    Aliases:
    - local|l: <project_dir>/fs
    - default|d: $HOME/miniconda3/fs (default path of conda)
    - conda|c: Within conda_prefix/fs
    """
    cli = FLG.fs_dir or 'default'
    cli = repl_dollar_var_with_env_val(cli)
    if cli in ('local', 'l'):
        cli = project.root() + '/fs'
    elif cli in ('default', 'd'):
        cli = S.conda_prefix + '/fs'
    elif cli in ('conda', 'c'):
        cli = cur_prefix() + '/fs'
    cli = os.path.abspath(cli)
    S.fs_dir = cli


conda_prefix = lambda: S.conda_prefix or [set_conda_prefix(), S.conda_prefix][1]


class CommonFlags:
    autoshort = ''

    class install_state:
        n = 'show install state infos'
        d = False

    class conda_prefix:
        n = set_conda_prefix.__doc__
        d = 'default'

    class fs_dir:
        n = set_fs_dir.__doc__
        d = 'default'

    class log_resources_fully:
        n = 'Always output all settings of resources when logging'
        d = False


# --------------------------------------------------------------------- tools/  actions

simple_types = (bool, int, float, str, list)
to_struct = lambda s: (to_list if s.name == 'resources' else to_dict)(s)
to_list = lambda rscs: [to_dict(rsc) for rsc in rscs]
to_dict = lambda rsc: {
    k: getattr(rsc, k)
    for k in dir(rsc)
    if not k.startswith('_') and isinstance(getattr(rsc, k), simple_types)
}


# # get some nice respresentation of the rsc classes:
# class Resource(type):
#     # print the resources always fully - too much spam:
#     # __repr__ = __str__ = lambda s: json.dumps(to_struct(s), sort_keys=True, indent=2)
#     __repr__ = __str__ = (
#         lambda s: rsc_repr(s)
#         if not FLG.log_resources_fully
#         else json.dumps(to_struct(s), sort_keys=True, indent=2)
#     )


# class R(metaclass=Resource):
#     listed = classmethod(lambda s: rsc_classes(s))


# def representable(name, *bases):
#     return type(name, (R,) + bases, {'__metaclass__': Resource})


# api:
g = lambda rsc, key, default='': getattr(rsc, key, default)


def gf(rsc, key, default=''):
    """Get function if it was a callable"""
    v = g(rsc, key, default)
    return S.name_to_func.get('.'.join((rsc.name, v)), v)


# ------------------------------------ Setting Directories project dir and conda_prefix


# def matching_resource(match, exact=False):
#     if not S.rscs_defined:
#         find_resource_defs()
#     if exact:
#         rsc = [r for r in S.rscs_defined.listed() if match == r.name]
#     else:
#         app.info('trying fuzzy match', match=match)
#         rsc = [r for r in S.rscs_defined.listed() if match in str(to_dict(r)).lower()]
#         app.debug('matches', rsc=rsc)
#         if len(rsc) > 1:
#             prov = to_list(g(rsc, 'provides', ''))
#             rsc = [r for r in rsc if match in r.name.lower() or match in str(prov)]
#             if len(rsc) > 1:
#                 rsc = [r for r in rsc if match == r.name or match in prov]
#     if not rsc or len(rsc) > 1:
#         app.die('No unique match', match=match, defined=S.rscs_defined, found=len(rsc))

#     return rsc[0]


is_fs = lambda rsc: str(g(rsc, 'pkg')).startswith('layers:')


def dir_rsc_cfg(rsc):
    """configured directory of the resource"""
    if is_no_pkg_rsc(rsc):
        return project.root() + '/bin'
    elif is_fs(rsc):
        return S.fs_dir + '/' + rsc.name
    else:
        return S.conda_prefix + '/envs/%s/bin' % (g(rsc, 'conda_env', rsc.name))


def rsc_path(rsc, verify_present=False):
    """
    Find path of resource (e.g. /home/joe/miniconda3/envs/myrsc/bin)
    Return nothing if not present

    We are intrested in the path not the file itself because we'll export it before running.
    """
    path = dir_rsc_cfg(rsc)
    if not verify_present:
        return path
    v = gf(rsc, 'verify_present')
    if v:
        return path if v(rsc=rsc, path=path) else None
    if is_no_pkg_rsc(rsc):
        return path if exists(path + '/' + rsc.name) else None
    exe = g(rsc, 'exe') or g(rsc, 'cmd')
    if not exe:
        return path if exists(path) else None
    else:
        return path if exists(path + '/' + exe) else None


interactive = lambda: '-y' if FLG.force else ''
# resources without a package (e.g. client)
is_no_pkg_rsc = lambda rsc: g(rsc, 'pkg') == False


class Run:
    def get_full_cmd(rsc, sel):
        cmd_pre = ''
        if is_no_pkg_rsc(rsc):
            f = gf(rsc, sel, sel)
            d = project.root()
        else:
            d = rsc_path(rsc, verify_present=True)
            if not d:
                # d = rsc_path(rsc, verify_present=True)
                app.die('Not installed', **to_dict(rsc))

            spec = {}
            # find a function to call:
            f = gf(rsc, sel, sel)
            if not callable(f):
                f = gf(rsc, 'run')
                if not callable(f):
                    f = gf(rsc, 'cmd')
        # else just take the command string:
        cmd = gf(rsc, 'run') or gf(rsc, sel, sel)
        if callable(f):
            spec = f(cmd=sel, rsc=rsc, pth=d, api=api())
            i = isinstance
            if i(spec, dict):
                # e.g.: export LD_...
                cmd_pre = spec.get('cmd_pre', '')
            cmd = spec if i(spec, str) else (spec or {}).pop('cmd', cmd)
            if callable(cmd):
                # cmd was a function which e.g. just changed dir:
                cmd = cmd.__name__

        # app.info('Adding PATH', path=d)
        # os.environ['PATH'] = d + ':%s' % os.environ.get('PATH')
        if cmd.startswith(':'):
            cmd = cmd[1:]
        else:
            cmd = d + '/' + cmd
        cmd = cmd_pre + cmd
        # if not cmd.split(' ')[0] == orig_cmd.split(' ')[0]:
        #     app.info('completing command', given=orig_cmd, completed=cmd)
        return cmd, spec


class Install:
    """Install methods"""

    _ = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh'
    conda_installer_url = _

    def no_pkg(rsc):
        app.info('No package resource - no install')

    def resource(rsc):
        """Api entry: install a resource"""
        Install.requirements(g(rsc, 'req'))
        if not rsc.installed or g(FLG, 'force_reinstall', ''):
            if g(rsc, 'pkg') == False:
                install_mode = Install.no_pkg
            elif is_fs(rsc):
                install_mode = Install.FS.filesystem
            else:
                install_mode = Install.Conda.conda_env

            do(install_mode, rsc=rsc)
        else:
            app.debug('already installed', rsc=rsc.name)
        do(Install.post, rsc=rsc, ll=10)
        do(Install.write_starter_and_unit_file, rsc=rsc, ll=10)
        rsc.installed = True
        S.rsc_modified = True

    class Tools:
        def download(url, dest):
            # TODO
            cmd = 'curl "%s" -o "%s"' % (url, dest)
            do(system, cmd)
            app.info('downloaded', dest=dest)

    class FS:
        def filesystem(rsc):
            if not rsc_path(rsc, verify_present=True):
                pass
            d = S.fs_dir + '/%s' % rsc.name
            img = rsc.pkg.split('layers:', 1)[1]
            system('ops container_pull --repo "%s" --dir "%s.img"' % (img, d))
            s = '--skip_filesystem_adaptions'
            system('ops container_build --dirs "%s.img" --target_dir "%s" %s' % (d, d, s))

    def write_unit_file(name, fn, rsc):
        pn = project.root().rsplit('/', 1)[-1]
        m = {
            'name': name,
            'descr': '%s %s ' % (g(rsc, 'n', name), pn),
            'ctime': time.ctime(),
            'exec_start': fn,
        }
        d = os.environ['HOME'] + '/.config/systemd/user'
        if not exists(d):
            app.info('creating systemd user dir', dir=d)
            os.makedirs(d)
        n_svc = '%s-%s.service' % (name, pn)
        sfn = d + '/' + n_svc
        unit = T_unit % m
        have = read_file(sfn, dflt='')
        if unit != have:
            write_file(sfn, unit)
            app.info('have written unit file', fn=sfn)
        else:
            app.debug('unit file unchanged', fn=sfn)
        return n_svc

    def write_starter_and_unit_file(rsc):
        env = os.environ
        env['d_conf'] = project.root() + '/conf'
        env['d_bin'] = project.root() + '/bin'

        def write(cmd, fcmd, spec):
            # if cmd == 'dot':
            #    breakpoint()  # FIXME BREAKPOINT
            if isinstance(spec, str):
                spec = {}
            app.debug('writing bin/' + cmd, cmd=fcmd)
            pre_exec = spec.pop('pre_exec', '')
            spec_env = spec.pop('env', {})
            fn = project.root() + '/bin/%s' % cmd
            have = read_file(fn, '')
            marker = '-AUTOCREATED- '
            if have and len(have.split('\n' + marker, 1)[0].splitlines()) > 8:
                return app.warn(
                    'Skipping write of starter file, marker was manually removed',
                    fn=fn,
                    marker=marker,
                )
            call = sys.argv[0]
            args = ' '.join(sys.argv[1:])
            if call.endswith('/ops'):
                call = call.rsplit('/', 1)[-1] + ' ' + args
            else:
                call = call + '\\\n' + args
            r = [
                '#!/usr/bin/env bash',
                '',
                '# Delete line containing "%s" to avoid overwrites of this file at project init'
                % marker,
                "_='%s" % time.ctime(),
                marker,
                '%s' % call,
                "'",
            ]
            add = r.append
            units = g(FLG, 'init_create_unit_files', [])
            if g(FLG, 'init_create_all_units'):
                units.extend(listed(g(rsc, 'systemd', None)))

            has_unit = False
            if any([u for u in units if u == cmd]):
                has_unit = True
                n_svc = Install.write_unit_file(cmd, fn, rsc)
                s = '''

                case "${1:-}" in
                    start|restart|stop|status)
                        systemctl --user --no-pager $1 "%s"
                        exit $?
                        ;;
                esac
                '''
                add(deindent(s % n_svc))

            # env['PATH'] = '%s:$PATH' % g(rsc, 'path')
            add('')
            add("H='__HOME__'")
            add('export PROJECT_ROOT="%s"' % project.root())
            add('')
            add('# Resource settings:')
            # for whoever needs that:
            allk = set()
            for m in to_dict(rsc), spec, spec_env:
                for k, v in m.items():
                    allk.add(k)
                    if k == 'port':
                        v = offset_port(v)
                    exp = 'export ' if m == env else ''
                    add('%s%s="%s"' % (exp, k, str(v)))
            add('')
            if 'logdir' not in allk:
                add('export logdir="$PROJECT_ROOT/log"')
            if 'logfile' not in allk:
                add('export logfile="$logdir/%s.log"' % cmd)

            add('')
            # only for services. Tools not: (e.g. cd mydir && git status -> bum, differentdir)
            if has_unit:
                add('cd "%s"' % project.root())
            # for client but also possibly other python resources:
            env['PYTHONPATH'] = env.get('PYTHONPATH', '')
            add('export PYTHONPATH="%(d_conf)s:%(PYTHONPATH)s"' % env)
            # to just call w/o virtenv activation:
            # we remove all d_bin refs and put them to the end, to avoid circulars,
            # e.g. for npm - find it first in conda env
            d, p = env['d_bin'], env['PATH']
            for k in ':', '':
                p = p.replace(d + k, '')
            p += ':' + d
            add('export PATH="$path:%s"' % p)
            add('')

            add('return 2>/dev/null # when sourced\n')

            if pre_exec:
                for c in listed(pre_exec):
                    add(c)
                add('')
            postproc = g(FLG, 'add_post_process_cmd', '')
            if not has_unit:
                postproc = ''
            add('%s "$@" %s\n\n' % (fcmd, postproc))

            h = os.environ['HOME']
            s = '\n'.join(r).replace(h, '$H').replace('__HOME__', h)

            if have and have.split(marker, 1)[-1] == s.split(marker, 1)[-1]:
                app.debug('No change', cmd=cmd)
            else:
                write_file(fn, s, chmod=0o755)

        for cmd in rsc_cmds(rsc):
            fcmd, spec = Run.get_full_cmd(rsc, cmd)
            cmd = cmd.rsplit('/', 1)[-1]  # /usr/bin/seagull -> bin/seagull
            write(cmd, fcmd, spec)

    def requirements(req):
        if not req:
            return
        app.info('Installing requirements', req=req)
        for r in to_list(req):
            rsc = matching_resource(r, exact=True)
            Install.resource(rsc)

    class Conda:
        def conda_env(rsc):
            D = S.conda_prefix

            # return False if not dp else all([exists(dp + '/' + p) for p in rsc.provides])
            if not exists(D + '/bin/'):
                do(Install.Conda.base, location=D)

            if str(rsc.path).startswith(D):
                return app.debug('already installed - skipping', rsc=rsc)

            env = g(rsc, 'conda_env', rsc.name)
            ctx = dict(D=D, name=env, yes=interactive())
            # source is not working for $0 = sh:
            cmd = [
                '. "%(D)s/etc/profile.d/conda.sh"',
                'conda create %(yes)s -n "%(name)s"',
                'conda activate "%(name)s"',
            ]
            pth = '%(D)s/envs/%(name)s/bin/' % ctx

            if g(rsc, 'typ') == 'pip':
                ctx['cmd'] = rsc.cmd
                cmd += ['conda install python; %p/pip install %%(cmd)s' % pth]
            else:
                icmd = g(rsc, 'conda_inst', '')
                if icmd:
                    cmd += [icmd]
                else:
                    p = g(rsc, 'conda_pkg') or g(rsc, 'pkg') or ' '.join(rsc.provides)
                    chan = g(rsc, 'conda_chan', '')
                    if chan:
                        chan = '-c ' + chan
                    ctx['chan'] = chan
                    ctx['pkg'] = p
                    cmd += ['conda install %(yes)s %(chan)s %(pkg)s']
            cmd = ' && '.join(cmd) % ctx
            rsc.path = g(rsc, 'path') or pth
            return do(system, cmd)

        def base(location):
            app.warn('conda dir not found', dir=location)
            if not FLG.force:
                q = 'Confirm: Install miniconda at %s? [y/N]'
                if not input(q % location).lower() == 'y':
                    app.die('unconfirmed')
            fn = os.environ['HOME'] + '/install_miniconda.sh'
            url = Install.conda_installer_url
            if not exists(fn):
                Install.Tools.download(url, fn)
            if not exists(fn):
                app.die('download failed', fn=fn)
            os.system('chmod +x "%s"' % fn)
            os.makedirs(os.path.dirname(location), exist_ok=True)
            do(system, '%s -b -p "%s"' % (fn, location))

    def post(rsc):
        pf = gf(rsc, 'post_inst')
        if not pf:
            return
        # when post_inst_verify is True they have been installed. When not present there are none:
        if g(rsc, 'post_inst_verify') and not g(FLG, 'force_reinstall'):
            return

        if callable(pf):
            app.info('postinstall function', name=rsc.name)
            # they may be requirements for the post install as well:
            Install.requirements(gf(rsc, 'post_inst_req'))
            # run it:
            pth, here = environ['PATH'], os.getcwd()
            try:
                if rsc.path.endswith('/bin'):
                    environ['PATH'] = rsc.path + ':' + pth
                res = pf(rsc, install=True, api=api())
            finally:
                os.chdir(here)
                environ['PATH'] = pth

            # Usually pf installs - except:
            # special case for tools, it has not a single cmd but a list of provides.
            # no cmd -> not yet install_conda_env was run. we do it now via this conventin:
            if res == 'install_conda_env':
                return Install.Conda.conda_env(rsc)
        else:
            app.die('Unsupported postinstall method', method=pf)


def rsc_cmds(rsc):
    r = []
    cmd = g(rsc, 'exe') or g(rsc, 'cmd')
    if cmd:
        r.append(cmd)
    for p in g(rsc, 'provides', ()):
        r.append(p)
    return r


def api():
    from devapp import resource_tools as api

    return api


def check_installed(rscs):
    """Sets the installed flag"""

    def check_installed_path(rsc):
        rsc.path = rsc_path(rsc, verify_present=True) or False

    def check_post_installed(rsc):
        # funnily we cannot import this module there, hash(S) is different then :-/
        # guess because of dynamic imports / freezing. So we pass ourselves over:
        cp = gf(rsc, 'post_inst')
        if callable(cp):
            res = cp(rsc, verify=True, api=api())
            rsc.post_inst_verify = res
        elif cp:
            raise NotImplementedError

    for rsc in listed(rscs):
        d = partial(do, rsc=rsc, ll=10)
        # if g(rsc, 'pkg') == False:
        #     rsc.installed = False
        #     continue
        d(check_installed_path)
        d(check_post_installed)

        rsc.installed = bool(rsc.path and g(rsc, 'post_inst_verify', 'y'))


add_install_state = check_installed


def find_resources_files_in_sys_path():
    files = {}

    def find_file_in_pth(pth, d, files=files):
        fn = '%s/%s/operations/resources.py' % (pth, d)
        if exists(fn) and not d in files:
            files[d] = fn
            S.rsc_dirs[fn] = pth + '/' + d

    def find_files_in_sys_path(pth):
        [find_file_in_pth(pth, d) for d in os.listdir(pth)]

    [find_files_in_sys_path(pth=pth) for pth in sys.path if os.path.isdir(pth)]
    return files


def complete_attrs(rsc, fn):
    def to_name(rsc, p):
        if callable(p):
            n = p.__name__
            S.name_to_func['.'.join((rsc.name, n))] = p
            return n
        return p

    def repl_callable(rsc, k, v):
        listed_attrs = ['provides']  # allow to say provides= npm
        if isinstance(v, list):
            vn = [to_name(rsc, i) for i in v]
        else:
            vn = to_name(rsc, v)
        if k in listed_attrs and not isinstance(vn, list):
            vn = [vn]
        if vn != v:
            setattr(rsc, k, vn)

    rsc.doc = rsc.__doc__ or ''
    rsc.name = rsc.__name__
    rsc.module = rsc.__module__.replace('.operations.resources', '')
    rsc.__repr__ = lambda r: str(to_dict(r))
    rsc.__str__ = lambda r: to_str(r)
    rsc.module_dir = S.rsc_dirs[fn]
    rsc.disabled = g(rsc, 'disabled', g(rsc, 'd', False))
    rsc.installed = g(rsc, 'installed', False)
    [repl_callable(rsc, k, getattr(rsc, k)) for k in dir(rsc) if not k.startswith('_')]


def to_str(rsc):
    svc = g(rsc, 'systemd')
    i = 'i' if g(rsc, 'installed') else ' '
    d = 'd' if rsc.disabled else ' '
    s = 's' if svc else ' '
    n = svc if svc else rsc.name
    return '%s %s %s %s %s' % (s, i, d, n, g(rsc, 'provides', ''))


def rsc_repr(rsc):
    return rsc.name + ('[i]' if g(rsc, 'installed', '') else '')


# ------------------------------------------------------------------------    API entry
def find_resource_defs(_have_mod={}):
    """

    Delivers back a list of resources with unique classnames, i.e. w/o parents of same name

    (class mysql of 4A overwrites mysql of python)

    Identical ones are also possible and are removed:

        class rsc(other_rsc):
            pass


    """
    set_conda_prefix()
    set_fs_dir()
    m = {}
    for k in 'fs_dir', 'conda_prefix':
        f, s = g(FLG, k), g(S, k)
        m[k] = s if f == s else '%s(%s)' % (s, f)
    app.info('Directories', **m)

    rsc_files = find_resources_files_in_sys_path()

    def rsc_classes(rsc_cls_of_resources_module):
        """rscs is class rsc (with resource classes as attrs"""
        _ = rsc_cls_of_resources_module
        rsc_clses = [g(_, k) for k in dir(_) if not k.startswith('_')]
        rsc_clses = [r for r in rsc_clses if isinstance(r, type)]
        return rsc_clses

    rscs = []

    def find_cls_in_pth(d, fn, rscs=rscs):
        try:
            n_mod = '%s.operations.resources' % d
            if n_mod in _have_mod:
                app.info('%s' % n_mod, conflict=fn, taken=_have_mod[n_mod])
                return
            _have_mod[n_mod] = fn
            mod = importlib.import_module(n_mod)
        except Exception as ex:
            return app.die('Cannot import', fn=fn, exc=ex)
        mod.rsc._package = d
        mod.rsc._filename = fn

        rsc_clses = rsc_classes(mod.rsc)
        [complete_attrs(r, fn) for r in rsc_clses]

        rscs.extend(rsc_clses)

    {find_cls_in_pth(d, fn) for d, fn in rsc_files.items()}

    def remove_redefined_rscs(rscs=rscs):

        # this removes the identical ones:
        all = set(rscs)
        # assert len(all) == len(rscs)
        for r in all:
            for p in r.mro()[1:]:
                if p in all:
                    n = p.__name__
                    d = {'redefined by': r.module, 'was': p.module + '.' + n}
                    app.info('Resource redefined: %s' % n, **d)
                    rscs.remove(p)

        i, j = len(all), len(rscs)
        if i > j:
            app.info('%s resources redefined' % (i - j))

    remove_redefined_rscs()
    # remove dubs (through class rsc(other_rsc))
    rscs = set(rscs)
    # sort by name:
    rscs = sorted([r for r in rscs], key=lambda x: x.name)
    # now we make singletons for __repr__ w/o metaclass hacks
    rscs = [r() for r in rscs]
    for k in rscs:
        app.debug(k.name, **to_dict(k))
    S.rscs_defined = rscs
    return rscs
