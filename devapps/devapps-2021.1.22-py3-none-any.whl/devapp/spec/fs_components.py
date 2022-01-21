#!/usr/bin/env python
"""

# Spec Building

## Dev
### Frequent abbrs:
- rt: runtime (e.g. systemd, docker, k8s,)
- cls: A class in a spec python file, denoting a config entity
- fid: Full id of an item (path in the spec : ['Wifi', 'NB01', 'Redis']
"""
# stream of specs - from anywhere, we will run as daemon some day:
# before that its just a one item stream, with item pushed at proc stasrt:

import os
import subprocess as sp

import rx
from devapp.app import app
from devapp.spec import find_paths_in_fs_components
from devapp.spec.tools import FS, full_url_and_path
from devapp.tools import (
    dirname,
    download_file,
    exists,
    into,
    is_,
    sp_call,
    to_list,
    url_to_dir,
)
from devapp.utils.rx_tools import chain, do_if, threaded
from rx import operators as op
from rx.operators import filter

base_dirs = 'var', 'data', 'conf', 'log', 'build', 'etc'

# filesystem components as declared in specs:
fs_comps = {}

default_methods = {'git': 'mount', 'oci': 'overlay', 'conda_env': 'activate'}

pass_ = lambda a: a

# fmt:off
d_oci         = lambda r: r['env']['DA_DIR_OCI']   + '/' + r['path']
props         = lambda r: r['spec']['props']
frm_to        = lambda frm, to: {'from': frm, 'to': to}
d_repo        = lambda r: r['env']['DA_DIR_REPOS'] + '/' + r['path']
comp_name     = lambda p: p if is_(p, str) else p['name']
rfs_comps     = lambda r: [fs_comps[comp_name(p)] for p in filesystem(r)]
filesystem    = lambda r: props(r).get('filesystem')
d_exe_bare    = lambda env: env['DA_DIR_OCI'] + '/executables'

# fmt:on
def d_checkout(repo):
    r = repo
    d, p = '', r['path']
    if '/' in p:
        d, p = p.rsplit('/', 1)
        d = '@' + d.replace('/', sep_slash)
    res = r.get('checkout_dir') or (
        r['env']['DA_DIR_CHECKOUTS']
        + '/'
        + p
        + d
        + sep_branch
        + r['branch'].replace('/', sep_slash)
    )
    return res


# we want one flat dir of checkouts. need to name them somewhat sensibly
# they should show the branch they are based on
sep_branch = '#'
sep_slash = '^'

root_fs_mount_ph = '$fs'

# Phase 1: FETCH FS COMPONENTS------------------------------------------------:
# The First Phase: Walking all filesysem components, independent of classes


class FSComponents:
    """
    Namespace for Component Specific Methods
    We often use the word repo for component, for analogy with git
    """

    class Defaults:
        # ready to be adapted, e.g. by flags
        exe_fs_method = 'symlink'
        local_unknown_comptype = 'ext_dir'

    class host_system:
        """host packages"""

        def prepare(repo):
            repo['bare_have'] = True
            repo['skip_completion'] = True
            repo['skip_add_fs_presence_infos'] = True
            repo['packages'] = to_list(repo['packages'])
            # just something meaningful, packages are handled by the distri:
            repo['checkout_dir'] = '/usr/bin'
            return repo

        def get_bare(repo):
            return repo

        def _detect_inst_cmd():
            ps = 'dnf', 'yum', 'apt-get'
            for c in ps:
                cmd = getattr(app.sh, c, None)
                if cmd:
                    break
            if not cmd:
                app.die('Could not derive a package installer', tried=ps)

            return (c, 'install', '-y')

        @classmethod
        def into_fs(pkg, repo):
            inst_cmd = pkg._detect_inst_cmd()
            inst_cmd += tuple(repo['packages'])
            st = sp_call(*inst_cmd, as_root=True, get_all=True)
            if st['exit_status']:
                app.die('Package install failed', **st)
            return repo

    class git:
        def get_bare(repo):
            app.sh.git.clone('--bare', repo['url'], d_repo(repo))
            repo['bare_have'] = True
            return repo

        def checkout(repo):
            d = d_checkout(repo)
            app.sh.git.clone(d_repo(repo), d)
            app.sh.git.checkout(repo['branch'], _cwd=d)
            repo['checkout_have'] = True
            return repo

        def set_remotes(repo):
            d = d_checkout(repo)
            # have = app.sh.git.remotes('-v', _cwd=d)
            app.sh.git.remote.rename('origin', 'local', _cwd=d)
            app.sh.git.remote.add('origin', repo['url'], _cwd=d)
            return repo

        into_fs = [checkout, set_remotes]

    class oci:
        def prepare(repo):
            repo['branch'] = 'oci'
            repo['run_dir'] = root_fs_mount_ph  # will be replaced later
            # oci always are overlayed, no matter the run_dir:
            repo['fs_method'] = repo.get('fs_method') or default_methods['oci']
            return repo

        def pull_layers(repo):
            url = repo['url']
            # app.sh.dpull('-d', repo['bare_dir'], '--repo', url)
            err = sp.call(['dpull', '-d', repo['bare_dir'], '--repo', url])
            if err:
                app.die('could not pull layers', **repo)
            repo['bare_have'] = True
            return repo

        def merge_layers(repo):
            b, c = repo['bare_dir'], repo['checkout_dir']
            err = sp.call(['dmerge', '-d', b, '--method', 'tar', '-t', c])
            if err:
                app.die('could not merge layers', **repo)
            repo['checkout_have'] = True
            return repo

        get_bare = pull_layers
        into_fs = merge_layers

    class mount:
        def prepare(repo):
            repo['branch'], n, D = 'mount', repo['name'], repo['env']['DA_DIR']
            repo['base_name'] = repo['name']
            repo['fs_method'] = 'mount'  # checkout will be mounted to run
            repo['run_dir'] = repo['to']
            repo['checkout_dir'] = repo['bare_dir'] = repo['from']
            repo['bare_have'] = repo['checkout_have'] = True
            repo['skip_completion'] = True
            return repo

        def get_bare(repo):
            return repo

    class conda_env:
        def prepare(repo):
            repo['branch'], n, D = 'env', repo['name'], repo['env']['DA_DIR']
            repo['base_name'] = repo['name']
            repo['checkout_dir'] = repo['bare_dir'] = D + '/envs/' + n
            repo['run_dir'] = repo['checkout_dir']
            repo['bare_have'] = True
            repo['skip_completion'] = True
            repo['fs_method'] = 'pass'  # done via link to env's python (in build.sh)
            return repo

        def get_bare(repo):
            return repo

        def into_fs(repo):
            D = repo['env']['DA_DIR']
            cmds = [
                '-p',
                D + '/envs/%s' % repo['name'],
                '-y',
                *[l for l in to_list(repo['packages']) if is_(l, str)],
            ]
            for c in to_list(repo.get('add_channels')):
                cmds.insert(0, c)
                cmds.insert(0, '-c')

            app.info('conda create', args=' '.join(cmds))
            app.sh.conda.create(*cmds)
            l = [(l[0], to_list(l[1:])) for l in repo['packages'] if not is_(l, str)]
            icmd = app.sh.conda.install
            if l:
                for chan, ps in l:
                    app.info('conda.install', args=' '.join(cmds))
                    icmd('-c', chan, '-n', repo['name'], '-y', *ps)
            pips = repo.get('pips', ())
            if pips:
                m = {'DA_DIR': repo['env']['DA_DIR'], 'name': repo['name']}
                pc = '%(DA_DIR)s/envs/%(name)s/bin/pip' % m
                for pip in pips:
                    if sp.call([pc, 'install', pip]):
                        app.die('Pip failed', pip=pip)
            repo['checkout_have'] = True
            return repo

    class ext_dir:
        """Using anywhere on the filesystem"""

        @classmethod
        def get_bare(sl, repo):
            for d in 'bare_dir', 'checkout_dir', 'run_dir', 'path':
                repo[d] = repo['url'].replace('file://', '')
            return repo

    class exe:
        """Simple static binaries, gitlab runner, hashitools in go...
        We pull to bare, copy to checkout, mount or copy to run_dir
        """

        _dest_dir = '/bin/'

        @classmethod
        def fn(exe, where, repo):
            fn = repo[where] + exe._dest_dir + repo['name']
            if not exists(dirname(fn)):
                os.makedirs(dirname(fn))
            return fn

        def prepare(repo):
            repo['branch'], env = 'exe', repo['env']
            d = url_to_dir(repo['url'])
            for k, m in (('bare_dir', d_exe_bare),):
                repo[k] = '/'.join((m(env), d))
            repo['branch'] = 'exe'
            repo['fs_method'] = repo.get(
                'fs_method', FSComponents.Defaults.exe_fs_method
            )
            return repo

        @classmethod
        def get_bare(exe, repo):
            fn = exe.fn('bare_dir', repo)
            download_file(repo['url'], local_filename=fn)
            return repo

        @classmethod
        def into_fs(exe, repo):
            fn = exe.fn('checkout_dir', repo)
            app.sh.cp('-f', exe.fn('bare_dir', repo), fn)
            app.sh.chmod('+x', fn)
            return repo

    class lib(exe):
        _dest_dir = '/'


def fetch_fs_comps(env, processing=[]):
    """At spec loading we walked thru all classes and generated the list of
    fs components in use in the spec"""
    # todo: Node local only comps filter, either here or at spec walk.

    return chain(
        # sort just to get same download behaviour(order) everywhere:
        rx.from_(sorted(fs_comps.items())),
        filter(lambda kv: kv[0] not in processing),
        op.do_action(lambda kv: processing.append(kv[0])),  # don't do twice
        lambda kv: kv[1],  # we drop the name, was just to sort
        lambda repo, env=env: into(repo, 'env', env),
        do_if(_flow_by_type, which=_guess_component_type),
        # ldd, # uncomment to check produced infos per component
    )


# --------------------------------------------------- Helpers for the main flow
def _guess_component_type(repo_as_from_spec):
    """for group by"""
    repo = repo_as_from_spec
    if 'xhello' in str(repo):
        breakpoint()
    un, f = repo.get('url') or repo['name'], 'file://'
    # local?
    un, type = un.replace(f, ''), repo.get('type')
    # yes we allow even relative paths:
    if un.startswith('/') or un.startswith('./'):
        d = FSComponents.Defaults.local_unknown_comptype
        if not os.path.exists(un):
            app.die('Not found', url=un)
        if os.path.exists(un + '/.git') or un.endswith('.git'):
            repo['type'] = type = type or 'git'
        elif os.path.exists(un + '/.hg'):
            app.die('Mercurial not yet supported', d=un)
        elif not type:
            repo['type'] = type = type or d
    return (
        type
        if type
        else 'git'
        if (un.endswith('.git') or '.git#' in un)
        else 'oci'
        if len(un.split(':')) == 2
        else None
    )


def _flow_by_type(comp_type):
    """flows are so similar, we offer this for oci and git
    """
    cls = getattr(FSComponents, comp_type)
    ifs = getattr(cls, 'into_fs', pass_)
    into_fs = [ifs] if callable(ifs) else ifs
    return [
        lambda repo: into(repo, 'type', comp_type),
        getattr(cls, 'prepare', pass_),
        _complete_repo_infos,
        _add_fs_presence_infos,
        do_if(cls.get_bare, threaded(10), if_=lambda comp: not comp.get('bare_have'),),
        # do_if(*into_fs, if_=lambda comp: not comp.get('checkout_have')),
        do_if(*into_fs, if_=checkout_missing),
        _find_auto_env_paths,
        _drop_env,
    ]


def checkout_missing(comp):
    return not comp.get('checkout_have')


def _complete_repo_infos(repo):
    """Repo as derived from initial spec walk
    If in spec there was only string, then it has only 'name' set.
    """
    type, env, url = repo['type'], repo['env'], repo.get('url') or repo['name']
    if repo.get('skip_completion'):
        return repo
    app.debug('Repo type', type=type, url=url)
    repo['base_name'] = url.rsplit('/', 1)[-1].replace('.git', '')
    url += '#' + repo.get('branch', 'master')
    url, repo['branch'] = url.split('#')[:2]
    # d = url.split('/')
    # if len(d) > 1 and exists(d[1]):
    #    d = 'file://' + d
    repo['url'], repo['path'] = full_url_and_path(env, url, mode=repo['type'])
    repo['bare_dir'] = repo.get('bare_dir') or (
        d_repo(repo) if type == 'git' else d_oci(repo)
    )
    repo['checkout_dir'] = dc = d_checkout(repo)
    rd = repo.get('run_dir')
    if rd and rd != dc:
        # if there is a run_dir set, we have to mount over:
        rd = rd if rd[0] in ('/', '$') else ('%(DA_DIR)s/run/' % env + rd)
        repo['run_dir'] = rd
        repo['fs_method'] = repo.get('fs_method') or default_methods[type]
    else:
        # otherwise we'll just run from the checkout dir:
        # no mount required, then, for git
        repo['run_dir'] = dc
    return repo


def _add_fs_presence_infos(repo):
    if repo.get('skip_add_fs_presence_infos'):
        return repo
    d = repo['bare_dir']
    if exists(d):
        repo['bare_have'] = True
        repo['bare_is_up_to_date'] = 'maybe'
    # the co have check dir feature enables to detail when a checkout is considered present.
    # usefual for e.g. gitlab_runner/hugo, with bin and themes repos:
    d = repo.get('checkout_have_check_dir') or repo['checkout_dir']
    if exists(d):
        repo['checkout_have'] = True
        repo['checkout_is_up_to_date'] = 'maybe'
    return repo


def _find_auto_env_paths(repo):
    """A filesystem layer usually contains stuff processes want to use ;-)
    Find and define those here
    """
    cod = repo['checkout_dir']
    sds = [cod]  # searchdirs
    dd = cod + '/daemon'
    # if 'gbase' in str(repo):
    #    breakpoint()
    finders = find_paths_in_fs_components
    if exists(dd):
        [sds.insert(0, dd + '/' + d) for d in os.listdir(dd)]
    chain(
        rx.from_([(repo, cod, s) for s in sds]),
        finders.find_bin_paths,
        finders.find_py_paths,
    ).run()
    return repo


def _drop_env(repo):
    repo.pop('env')
    return repo


def check_mk_dirs(env):
    for k in ('DA_DIR_OCI', 'DA_DIR_CHECKOUTS'):
        if not k in env:
            env[k] = env['DA_DIR'] + '/' + k.rsplit('_', 1)[-1].lower()
    for k in ('DA_DIR_REPOS',):
        if not k in env:
            app.die('Require', env_key=k)
    dirs = ('DA_DIR_REPOS', 'DA_DIR_OCI', 'DA_DIR_CHECKOUTS')
    [app.sh.mkdir('-p', env[k]) for k in dirs if not exists(env[k])]


# Phase 2: Apply Per Class ----------------------------------------------------
# 'r' dicts are sent in per class of the spec:
def set_run_and_checkout_dirs(rc):
    r, comp = rc
    for d in 'run_dir', 'checkout_dir':
        r['env'][d] = comp[d]
    return rc


def set_mount(rc):
    r, comp = rc
    rd, cd = (comp['run_dir'], comp['checkout_dir'])
    if comp['type'] == 'exe':
        rd, cd = rd + '/' + comp['name'], cd + '/' + comp['name']
    if not FS.can_mount():
        app.warn('Require bindfs', frm=rd, to=cd)
    r['fs'][rd] = {'meth': 'mount', 'from': cd}
    return rc


def set_overlay(rc):
    r, comp = rc
    mp = comp['run_dir']
    have, cd = r['fs'].get(mp), comp['checkout_dir']
    if have:
        have['from'].append(cd)
    else:
        r['fs'][mp] = {'meth': 'overlay', 'from': [cd]}
    return rc


def add_framework_dirs(rc):
    r, comp = rc
    e, D = r['env'], r['env']['DA_DIR']
    r['fs']['$fs' + D] = {'meth': 'mount', 'from': D}
    bds = list(base_dirs)
    bds.append('repos')
    for d in bds:
        db = e.get('DA_DIR_%s' % d.upper())
        # outside one:
        if db and not db.startswith(D):
            r['fs']['$fs' + db] = {'meth': 'mount', 'from': db}
    return rc


fs_methods = {'mount': set_mount, 'overlay': [set_overlay, add_framework_dirs]}


def ldd(r):
    breakpoint()
    return r


def define_fs_stack(r):
    chain(
        rx.from_([(r, c) for c in r['fs_comps']]),
        set_run_and_checkout_dirs,
        do_if(fs_methods, which=lambda rc: rc[1].get('fs_method')),
    ).run()
    return r
