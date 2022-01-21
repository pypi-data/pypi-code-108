#!/usr/bin/env python
"""

# Spec Building

## Dev
### Frequent abbrs:
- rt: time (e.g. systemd, docker, k8s,)
- cls: A class in a spec python file, denoting a config entity
- fid: Full id of an item (path in the spec : ['Wifi', 'NB01', 'Redis']
"""
# stream of specs - from anywhere, we will  as daemon some day:
# before that its just a one item stream, with item pushed at proc stasrt:


# fmt:off
import json
import os
import shutil
import sys
import uuid
from functools import partial

import rx
from devapp.app import FLG, app
from devapp.spec import fs_components as fs
from devapp.spec import os_tools, tools
from devapp.spec.templ import SmartAdapt, align_by_eq, exec_templ, r_objs_by_fid
from devapp.tools import (
    abspath,
    camel_to_snake,
    dirname,
    exec_file,
    exists,
    into,
    read_file,
    to_list,
    write_file,
)
from devapp.utils.py_source_env import source
from devapp.utils.rx_tools import Ops, chain, do_if, map_diff_log
from rx import operators as op
from rx.operators import filter, flat_map
from tree_builder import full_id, struct_props
from tree_builder.links import conns_by_cls_dependent
from tree_builder.links import map_connections_to_all_classes as map_connections

# fmt:on


here = abspath(dirname(__file__))

FS = tools.FS

# Our default mapping op should log diffs:
Ops.default = map_diff_log

env = os.environ

environ = os.environ
# flag.string('spec_file', '', 'Spec file')
#
# flag.string('cls_match', '$DA_CLS', 'Restrict operation to matching classes')
# flag.string('log_time_fmt', 'dt', 'Time format of logs. E.g. "ISO", "%m:%s"')
# flag.string('dir', '$DA_DIR', 'Solution directory')
# flag.string(
#    'from_dir',
#    '',
#    'Source directory, witch conf/SPEC.py.\nWill be copied over to dir before install.',
#    short_name='f',
# )
#

# fmt:off
fidstr       = lambda r: '.'.join(r['spec']['fid'])  # fullid (path) as str
pfidstr      = lambda r: fidstr(r).rsplit('.', 1)[0] # parent full id
props        = lambda r: r['spec']['props']
is_svc       = lambda r: props(r)['type'] == 'Service'
is_app       = lambda r: props(r)['type'] == 'App'
is_exe       = lambda r: is_svc(r) or is_app(r)
dir_setup    = lambda r: app.var_dir + '/' + fidstr(r)
da_dir       = lambda r: r['env']['DA_DIR']          # DevApps Dir (=CondaPrefix)
runtime      = lambda r: props(r).get('runtime', 'systemd' if is_exe(r) else None)
slfn         = lambda fn: ('/' + fn) if fn else ''
build_dir    = lambda r: r['env']['build_dir']
comp_dir     = lambda r, fn='': build_dir(r) + '/fs_components' + slfn(fn)
unit_name    = lambda r: '%(name)s-%(DA_PREFIX)s.service' % r['env']
registry_url = env.get('DA_URL_REGISTRY','')
# fmt:on


def load_spec():
    g = exec_file(app.da_dir + '/conf/SPEC.py', get_src=True)
    return {'root': g['root'], 'src': g['source']}


# if not set we install the whole project - into a container:
def ldd(r):
    breakpoint()
    return r


# we push the 'r' dicts, built from the spec a few times through, mutating
# This is the list we'll use within rx.from_:
r_objs = []


def classes_stream(spec):
    def create_classes(obs, _, spec=spec, cls=None):
        """from root scan thru, pump out"""
        cls = spec['root'] if cls is None else cls
        fid = full_id(cls)
        fids = fidstr({'spec': {'fid': fid}})
        app.warn(cls.name, fid=fids, type=cls.type)
        props = dict(struct_props(cls))
        props['filesystem'] = cls.filesystem = to_list(props.get('filesystem'))
        for k in props['filesystem']:
            # can be given as string, then we find the rest
            if isinstance(k, str):
                fs.fs_comps[k] = {'name': k}  # will be filled by fs
                # strings only we DO normalize to lists:
            else:
                n = k.get('name')
                # leave like it was in spec:
                fs.fs_comps[n] = dict(k)

        r = {
            'cls': cls,
            '___': fids,  # it should show up on top when we pp r objs
            'env': {},  # will go to env.sh, sourced by systemd
            'spec': {'props': props, 'fid': fid},
            'links': {},  # links.json
            'fs': {},  # fs.json
        }
        r_objs.append(r)
        r_objs_by_fid[fids] = r
        obs.on_next(r)
        [create_classes(obs, _, spec, c) for c in cls._childs]
        if cls._root == cls:
            obs.on_completed()

    return rx.create(create_classes)


def add_init_env(r, da_env):
    r['env'].update(dict(da_env))
    r['env']['DA_CLS'] = r['___']
    return r


def run_rs_filtered(msg, *obs, cls_match=''):
    """
    filter: prefix match
    """

    def matched(o, cls_match=cls_match):
        if not cls_match:
            return o
        return o if o['___'].startswith(cls_match) else None

    matched = lambda o: o
    if cls_match:
        if not any([o for o in r_objs if matched(o)]):
            app.die('No spec classes match', match=cls_match, mode='startswith')
    app.info(msg)
    p = rx.from_(r_objs).pipe(filter(matched))
    return chain(p, *obs)


# ----------------------------------------------------------------------- links


def build_connections(r):
    """
    Our job: Add 'links', as pure data, telling the
    template exactly what to do
    That data is provided by interfaces and meta information of the repos
    interfacing with each other...
    """
    r['links'] = conns_by_cls_dependent(r['cls'])
    return r


def add_base_dir_vars(r):
    fid, e = fidstr(r), r['env']  # AXWiFi.Dispatcher
    for d in fs.base_dirs:
        bd = da_dir(r) + '/%s' % d  # /opt/axwifi/log
        # /opt/axwifi/log/AXWiFi.Dispatcher:
        e[d + '_dir'] = '%s/%s' % (bd, fid)
    SD = e.get('DA_DIR_STATS')
    e['stats_dir'] = e['var_dir'] if not SD else '%s/%s' % (SD, fid)
    e['pidfile'] = r['env']['var_dir'] + '/pidfile'
    return r


def trace_if(match):
    def t(r, match=match):
        print(r.get('___'))
        breakpoint() if match.lower() in str(r).lower() else 0
        return r

    return t


def find_cfg_dir(r):
    """where are the templates and all that"""
    rfs = r.get('fs_comps')
    if not rfs:
        # no rfs
        return r
    rfs = rfs[-1]  # last one, its a stack and last one must have config
    # the last one is it:
    r['env']['run_dir'] = rfs['run_dir']
    # remember
    dco = r['env']['DA_DIR_CHECKOUT'] = rfs['checkout_dir']
    # trace_if('nginx')(r)
    if exists(dco + '/recipe'):
        r['dir_cfg_checkout'] = dco + '/recipe'
    sd = 'daemon' if is_svc(r) else 'exe' if is_exe(r) else ''
    if not sd:
        return r
    # n = '' when /daemon or /exe contains the config
    # todo: have to see more variants to find that dir
    tries = (props(r)['name'], props(r).get('base'), rfs['base_name'], '')
    for nt in tries:
        if not nt:
            continue
        nt = camel_to_snake(nt)
        h = []
        for n in nt, nt.replace('_', ''):
            if n in h:
                continue
            h.append(n)
            ns = ('/' + n) if n else ''
            cd = '%s/%s%s' % (dco, sd, ns)
            if sd == 'daemon':
                cd += 'd'
            if exists(cd):
                r['dir_cfg_checkout'] = cd
                r['env']['cfg_path'] = pth = cd[len(dco) + 1 :]
                r['env']['daemon_dir'] = r['env']['run_dir'] + '/' + pth
                r['daemon_name'] = n
                return r
    return r


def _try_add_single_conffile(e, r_cfg):
    d = r_cfg

    # set conffile automatically if there is only one pointint to conf_dir:
    if exists(d + '/templates'):
        for k in ('conf', 'etc'):
            cd = k + '_dir__'
            l = [
                c.split(cd, 1)[1]
                for c in os.listdir(d + '/templates')
                if c.startswith(cd)
            ]
            # no subdir, we take exactly one file in conf_dir, no axc subdir:
            # (hashi understands conf_dir and parses all .json, so we put into axc)
            l = [c for c in l if not '__' in c]
            if len(l) == 1 and 'conffile' not in e:
                e['conffile'] = e[k + '_dir'] + '/' + l[0]


def req_unshare(r):
    # systemd seems to not export the mounts :-)
    return False


def add_app_env(r):
    """ man systemd.directives """
    e, da_dir = r['env'], env['DA_DIR']
    s = 'service_'
    if not e.get('app'):
        return r
    e[s + 'working_directory'] = wd = da_dir + '/run'

    _ = 'app_run_script'
    r['env'][_] = rnr = '.'.join(reversed(r['___'].lower().split('.')))
    e['app_run_exe_link'] = '%s/%s' % (wd, e['DA_CLS'])
    e['functions'] = e.get('functions', {})
    if not 'start' in e['functions']:
        e['functions']['start'] = [e['app']] + e.get('app_args', [])

    se = s + 'exec_start'
    if not se in e:
        app.info('Adding exec start directive', se='start')
        e[se] = 'start'
    e['app_run_script_path'] = da_dir + '/build/bin/' + rnr
    return r


def_paths = lambda r: (
    # apps can render templates into this;
    r['env']['etc_dir'] + '/bin',
    # E.g. the 'app' tool
    r['env']['DA_DIR_DEVAPPS'] + '/bin',
    # Suprocesses (.e.g bash) or poll success handler should have easy access to the starters:
    r['env']['DA_DIR'] + '/build/bin',
    '/usr/bin',
    '/bin',
    '/usr/sbin',
    '/sbin',
)

def_py_paths = lambda r, v=sys.version_info: (
    r['env']['DA_DIR_DEVAPPS'] + '/python',
    r['env']['DA_DIR_ENV_DEVAPPS']
    + '/lib/python%s.%s/site-packages' % (v.major, v.minor),
)


def set_env(r):
    """adding repo props (via its env.sh), then spec props to final env.sh"""
    e = r['env']
    ce = _is_not_in_conda_base_env(r)
    if ce:
        # good to know, e.g. in tempaltes(nginx)
        e['DA_DIR_ENV'] = ce

    # setting DA_DATACENTER, DA_NODE ...:
    # cls = r['cls']
    # for p in cls._parents[1:]:
    #    e['DA_%s' % p.type.upper()] = fidstr(p)
    r_cfg = r.get('dir_cfg_checkout')
    if r_cfg:
        _try_add_single_conffile(e, r_cfg)
        fn = r_cfg + '/env.sh'
        env_sh = read_file(fn, '', strip_comments=True)
        if env_sh:
            app.debug('reading', fn=fn)
            if '%(' in env_sh:
                try:
                    env_sh = env_sh % SmartAdapt(r, fn)
                except Exception as ex:
                    if not sys.stdin.isatty():
                        raise
                    print(ex)
                    print('breakpoint set at env render')
                    breakpoint()
                    keep_ctx = True
            # real sourcing, i.e. executing functions, interpreting vars
            try:
                fn = '/tmp/devapp_build.%s.%s' % (r['___'], uuid.uuid4())
                fn = write_file(fn, env_sh)
                e.update(os_tools.source(fn))
            except SystemExit as ex:
                msg = ''
                if ' =' in env_sh or '= ' in env_sh:
                    msg = 'Note that key=val assignments in bash '
                    msg += 'must be done w/o spaces'
                    msg += ' (have found " = ").'
                app.die('Could not shell source', fn=fn, msg=msg)
            finally:
                os.unlink(fn)

    # add the paths which the fs components loader found, per component:
    # for $PATH: systemd does not replace $PATH - i.e. we must add ours at
    # runtime.:
    rfs = fs.rfs_comps(r)
    for k in 'PATH', 'PYTHONPATH':
        P = []
        # all components, e.g. repos
        for comp in rfs:
            P.extend(comp.get('env_' + k, []))
        if P:
            have = e.get(k, '')
            if have:
                # hard set? that rules:
                P.insert(0, have)
        # TODO: We must do all 4, suse has different /bin then /usr/bin
        # better way is to set e.g. add_PATH and add only at runtime:
        if k == 'PATH':
            for p in def_paths(r):
                P.append(p) if not p in P else 0
            for p in solution_libs('bin', r):
                P.insert(0, p)
        elif k == 'PYTHONPATH':
            for p in def_py_paths(r):
                P.append(p) if not p in P else 0
            for p in solution_libs('python', r):
                P.insert(0, p)
        if P:
            e[k] = ':'.join(P)

    # TODO: Add repo meta.py props of all filesystem(?)
    e.update(r['spec']['props'])
    rt = props(r).get('runtime')
    if not rt:
        return r
    elif rt == 'systemd:boot':
        # todo: normalize this with other rts, this seems a bit too hardcoded:
        e['app'] = 'systemd-nspawn'
        l = ['--register=false', '-D', e['build_dir'] + '/fs', '--boot']
        e['app_args'] = l
    e['name_unit'] = unit_name(r)
    return r


def solution_libs(typ, r, have={'_scanned_da_dir_lib': 0}):
    if have['_scanned_da_dir_lib']:
        return have.get(typ) or ()
    d = env['DA_DIR'] + '/lib'
    if os.path.exists(d):
        for l in os.listdir(d):
            have[l] = [d + '/' + l]
    have['_scanned_da_dir_lib'] = 1
    return solution_libs(typ, r)


def ld(r):
    return r


def get_devapps_env_vars():
    # those will end in env.sh and are parametrizing our build - nothing else:
    daenv = dict([(k, env[k]) for k in env if k.startswith('DA_')])
    d = daenv['DA_DIR']
    # prefix is the directory name we run in, not the full path.
    # if people want two version of foo then they must say foo.lab, foo.14.1:
    daenv['DA_PREFIX'] = daenv.get('DA_PREFIX', d.rsplit('/')[-1])
    return daenv


def render_templates(r):
    e = r['env']
    d = r.get('dir_cfg_checkout')
    if not d:
        return r
    for td, ends in (d, '.tmpl'), (d + '/templates', ''):
        if not exists(td):
            continue
        for fn in os.listdir(td):
            if (
                not '__' in fn  # dir sep. always there
                or fn.startswith('.')
                or not fn.endswith(ends)
                or fn.endswith('.bak')
                or '__pycache__' in fn
            ):
                app.debug('Ignoring', fn=fn)
                continue
            res = exec_templ(td + '/' + fn, r)
            fnr = fn
            for k in 'etc', 'conf':
                fnr = fnr.replace(k + '_dir__', e[k + '_dir'] + '/')
            if 'conda_env_dir' in fnr:
                cd = [
                    c['checkout_dir'] for c in r['fs_comps'] if c['type'] == 'conda_env'
                ]
                if not cd:
                    raise Exception('No conda env', fnr)
                fnr = fnr.replace('conda_env_dir', cd[0])
            fnr = fnr.replace('__', '/')
            fnt = comp_dir(r, fn)
            write_file(fnt, res, mkdir=1)
            r['fs'][fnr] = {'from': fnt, 'meth': 'symlink'}

    return r


# def _add_base_site_packages_to_pypath(env):
#    """Base utilities of the base / devapps conda python setup should be there
#    always and are py3.x compat"""
#    sv = '%s.%s' % (sys.version_info.major, sys.version_info.minor)
#    bp = env['DA_DIR'] + '/lib/python%s/site-packages' % sv
#    # systemd unit starts -m devapp.run -> devapp nededs to be seen:
#    md = abspath(env['DA_DIR_DEVAPPS'] + '/../python')
#    for pp, p in ('sys_path_append', bp), ('PYTHONPATH', md):
#        env[pp] = ':'.join((env[pp], p)) if env.get(pp) else p
#


def _add_path(env, conda_env):
    """Binaries (non devapp modules) are childs of the python starter - need to
    be found in run.py"""
    p = conda_env + '/bin'
    env['PATH'] = p + ':' + env['PATH'] if env.get('PATH') else p


# def write_env(r):
#    e = r['env']
#    conda_env = _is_not_in_conda_base_env(r)
#    if conda_env:
#        # _add_base_site_packages_to_pypath(e)
#        _add_path(e, conda_env)
#    # DIR again, its already in run but easy access via env sourcing:
#    # if one is sourceing THIS he wants it exported, e.g. a unit:
#    s = ['#!', 'set -a', 'DA_DIR="%(DA_DIR)s"' % e]
#    ses = 'service_exec_start'
#    if is_exe(r) and not ses in e and not props(r).get('runtime') == 'user':
#        raise Exception('No $service_exec_start defined')
#
#    for k, v in sorted(e.items()):
#        # we source this to get in, if initted would be there then we could not
#        if k in ('DA_DIR', 'DA_INITTED'):
#            continue
#        v = (
#            "'%s'" % json.dumps(v)
#            if isinstance(v, (list, dict))
#            else '"%s"' % v
#        )
#        # we support in spec to say e.g.
#        # app_args = ['-c', '%(etc_dir)s/nginx.conf']
#        if '%(' in v:
#            v = v % e
#        kv = '%s=%s' % (k, v)
#        s += [kv]
#    s += ['set +a', '']
#    fn = e['build_dir'] + '/env.sh'
#    write_file(fn, s, mkdir=True)
#    return r
#

# fmt: off
env_defaults = {
    'unit_stop_when_unneeded'  : 'false',
    'service_type'             : 'simple',
    'service_kill_signal'      : 'SIGTERM',
    'service_send_SIGKILL'     : 'yes',
    'service_private_tmp'      : 'true',
    'service_timeout_stop_sec' : '5',
}
# fmt: on
def add_unit_vars(r):
    """these are added after env.sh written -> only make it into rendering ctx"""
    e = r['env']
    e['unit_description'] = (
        e.get('unit_description') or '%(type)s %(name)s [%(DA_CLS)s]' % e
    )
    [into(e, k, e.get(k, v)) for k, v in env_defaults.items()]
    e['service_PID_file'] = e['var_dir'] + '/pidfile'
    # not unit_name, since that would end in the unitfile:
    return r


def render_unit(r):
    res = exec_templ(here + '/templates/unit', r)
    res = align_by_eq(res.splitlines())
    fn = units_dir().replace('/', '__') + '__' + r['env']['name_unit']
    fnt = comp_dir(r, fn)
    write_file(fnt, res, mkdir=1)
    r['unit_file'] = fnt
    return r


units_dir = (
    lambda: '/etc/systemd/system'
    if not os.geteuid()
    else '%(HOME)s/.config/systemd/user' % env
)


def link_unit_in_parent_or_host(r):
    """Where to write the unit file to. We go back all parents - if one has
    a runtime which boots then we add our unit file there - else on the host
    Remember that parents can be isolation abstractions only - w/o actual rts
    """
    d_systemd = units_dir() + '/'

    pfid, pr = r['___'], None
    while len(pfid.split('.')) > 1:
        pfid = pfid.rsplit('.', 1)[0]
        _ = r_objs_by_fid[pfid]
        if props(_).get('runtime'):
            pr = _
            break
    # if no parent has a runtime we create the host link now:
    run_fn = d_systemd + r['env']['name_unit']
    r['env']['unit_file'] = run_fn
    if not pr:
        # no parent - we write unit into host:
        if not exists(d_systemd):
            err = os.system('mkdir -p "%s"' % d_systemd)
            if err:
                app.die('Could not create', d=d_systemd)

        # too many levels of symbolic links -> copy:
        app.info('Copying', frm=r['unit_file'], to=run_fn)
        FS.copy_file(r['unit_file'], run_fn)
    else:
        # have parent - we write unit into build dir of parent:
        rt = props(pr)['runtime']
        if ':boot' in rt:
            # write our link into the parent, so when it builds its fs before start
            # we are were we should be:
            # (grand..)parent runtime boots
            # fs.root_fs_mount_ph: '$fs', placeholder for root fs mount point
            root = fs.root_fs_mount_ph
            pr['fs'][root + run_fn] = {'from': r['unit_file'], 'meth': 'mount'}
            for target in ('devapps', 'multi-user'):
                pr['fs'][
                    root
                    + '%s%s.target.wants/' % (d_systemd, target)
                    + r['env']['name_unit']
                ] = {'from': run_fn, 'meth': 'symlink'}
        else:
            app.die('Not supported nesting into', runtime=rt)
    return r


fn_app_run_script = '%(DA_DIR)s/build/bin/%(app_run_script)s'


def add_app_run_script_to_build_dir(r):
    """
    DA_DIR/build/bin/ scripts.
    This should be in $PATH, for the user not for systemd
    Single commands, runnable from even outside conda:
    TODO: we could replace this thing with a 2 liner function per service as well
    """
    s = '''#!%(DA_DIR)s/run/%(DA_CLS)s
    # Offers to be run from the host w/o conda, w/o env.sh sourced, like in
    # systemd-unit => We source the env in python:
    import sys
    sys.path.append("%(DA_DIR_DEVAPPS)s/python")
    from devapp import load
    load.app_load(fn_env="%(DA_DIR)s/build/%(DA_CLS)s/env.json")
    from devapp import run
    run.app_run(args=sys.argv)
    '''
    s = s.replace('\n    ', '\n')
    fn = fn_app_run_script % r['env']
    write_file(fn, s % r['env'], mkdir=True)
    # os.chmod(fn, stat.S_IEXEC)
    os.chmod(fn, 0o755)
    return r


_ = [
    add_unit_vars,
    render_unit,
    link_unit_in_parent_or_host,
    add_app_run_script_to_build_dir,
]
render_runtime_starters = {'systemd': _, 'systemd:boot': _}


def _write_file(r, name, param):
    bd = build_dir(r)
    if not exists(bd):
        os.mkdir(bd)
    s = json.dumps(r[param], indent=4, default=str)
    # _cfg = ['-c', '%(etc_dir)s/runner.toml']
    if '%(' in s:
        # this will fail with any % in it -> then need to double replace:
        # or insert by string splits or re sub
        s = s % r['env']
    write_file(bd + '/' + name, s)
    return r


# fmt:off
write_env = lambda r: _write_file(r, 'env.json', 'env')
write_links = lambda r: _write_file(r, 'links.json', 'links')
write_fs_stack = lambda r: _write_file(r, 'fs_stack.json', 'fs')
# fmt:on


def create_var_dir(r):
    app.sh.mkdir('-p', r['env']['var_dir'])
    return r


def execute_persistent_fs_changes(r):
    fs = r.get('fs', {})
    if not fs:
        return r
    FS.build_from_fs_stack(mode='shared', app_env=r['env'], fs=fs)
    return r


def _is_not_in_conda_base_env(r):
    fsc = r.get('fs_comps', ())
    envs = [e for e in fsc if e.get('type') == 'conda_env']
    if len(envs) > 1:
        app.die('Cannot have 2 conda envs at same time', envs=envs)
    if envs:
        return envs[0]['run_dir']


def named_link_to_python(r):
    """This is for the app starters' shebang. We take the python from devapps env if no
    python in service env"""
    p = _is_not_in_conda_base_env(r) + '/bin/python'
    if not exists(p):
        p = env['DA_DIR_ENV_DEVAPPS'] + '/bin/python'
    FS.symlink(p, r['env']['app_run_exe_link'])
    return r


def clean_old_build(env):
    shutil.rmtree(env['DA_DIR'] + '/build/bin', ignore_errors=True)


def source_da_dir_env():
    D = env['DA_DIR']
    # env.sh shall understand any DA_ var in the build environ:
    d = source(D + '/env.sh', ign_missing=True, insert_env_vars=('DA_*',))
    env.update(d)


def source_devapps_env_if_not_activated(dir=None):
    """We may call da spec.build from the host, w/o
    properly activating base conda -> missing the sourcing of activate.d/devapps.sh
    -> do that now:
    """
    dir = env['DA_DIR'] = app.da_dir = dir or FLG.da_dir
    if env.get('DA_DIR_REPOS') and env.get('DA_DIR_DEVAPPS'):
        return
    d_base = sys.argv[0].split('/envs/', 1)[0]
    fn = d_base + '/etc/conda/activate.d/devapps.sh'
    if not exists(fn):
        raise Exception(
            'Missing DEVAPPS vars. Properly install devapps into a conda environ and activate it'
        )
    env['PATH'] = d_base + '/bin:%(PATH)s' % env
    env.update(source(fn, insert_env_vars=('PATH',)))


def copy_over_on_from_dir(d):
    if not d:
        return
    d = abspath(d)
    if not exists(d + '/conf/SPEC.py'):
        app.die('Not found', dir=d + 'conf/SPEC.py')
    FS.tarpipe(d, env['DA_DIR'], create=True)


def build(dir=None, from_dir=None, cls_match=None):
    source_devapps_env_if_not_activated(dir)
    copy_over_on_from_dir(from_dir)
    source_da_dir_env()
    devapp_env = get_devapps_env_vars()
    # this creates an iterable of all spec classes, serialized (into 'r' dicts),
    # which is # repeatedly used as a base observable, in run_rs invokations
    # below:
    run_rs = partial(run_rs_filtered, cls_match=cls_match)
    chain(
        rx.just(load_spec()),
        op.do_action(lambda spec: map_connections(spec['root'])),
        flat_map(classes_stream),
    ).run()
    clean_old_build(devapp_env)
    fs.check_mk_dirs(devapp_env)
    if not fs.fs_comps:
        app.warn('Nothing to build, no components. Bye.')
        sys.exit(0)
    fs.fetch_fs_comps(devapp_env).run()
    run_rs(
        'Preparation',
        partial(add_init_env, da_env=devapp_env),
        build_connections,
        add_base_dir_vars,
        do_if(
            # add OUR filesystem components into our data:
            lambda r: into(r, 'fs_comps', fs.rfs_comps(r)),
            find_cfg_dir,
            set_env,
            add_app_env,
            fs.define_fs_stack,
            if_=lambda r: props(r).get('filesystem'),
        ),
    ).run()
    run_rs(
        'Configuration',
        render_templates,
        do_if(render_runtime_starters, which=lambda r: runtime(r)),
    ).run()
    run_rs(
        'Writing files',
        write_fs_stack,
        write_links,
        execute_persistent_fs_changes,
        write_env,
        create_var_dir,
        do_if(named_link_to_python, if_=lambda r: r['env'].get('app_run_exe_link'),),
    ).run()
    # only outside possible:
    if os.environ.get('CONTAINER_NAME'):
        mode = 'container'
    else:
        if os.geteuid():
            mode = 'systemd(user mode)'
            app.sh.systemctl('--user', 'daemon-reload')
        else:
            mode = 'systemd(system mode)'
            app.sh.systemctl('daemon-reload')
    from tree_builder import UserInput

    UserInput.store()
    app.info('Spec Built', mode=mode)
    # run_rs('Pull Filesystem Resources', group_by(props('fil


# def set_cli_flags():
#    # user or config.cls did not set this environ var, then we assume we
#    # are root:
#    if FLG.cls_match == '$DA_CLS':
#        FLG.cls_match = ''
#    env['DA_DIR'] = FLG.dir
#    return
#
#
# main = lambda: run_app(
#    build,
#    {'log_dev_fmt_coljson': ['r', 'rdiff']},
#    flags_validator=set_cli_flags,
# )
#
if __name__ == '__main__':
    main()
