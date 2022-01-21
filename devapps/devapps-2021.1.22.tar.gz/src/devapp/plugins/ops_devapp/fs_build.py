#!/usr/bin/env python
"""
OCI Filesystem Creation
"""

# Could be done far smaller.
from datetime import datetime
from devapp import gevent_patched
from re import match
import hashlib
import json
from decorator import decorator
import os
import shutil
from copy import deepcopy
from functools import partial
import subprocess
import requests
from devapp.app import FLG, app, run_app, do, system
from devapp import tools
from operator import itemgetter


from devapp.tools import (
    now,
    exists,
    to_list,
    repl_dollar_var_with_env_val,
    project,
    read_file,
    have_tty,
    write_file,
    walk_dir,
)
import json
import time
from tempfile import mkdtemp
import fnmatch
from hashlib import md5


d_cache = os.path.abspath('.cache')
fn_last_state = d_cache + '/' + 'last_state.json'

FN_CONDA = 'Miniconda3-latest-Linux-x86_64.sh'
cleanups = []

hash_cmd = "fd . '%s' --type file --hidden %s -0 | sort -z | xargs -0 sha1sum"
hash_cmd += ' | sha1sum'


def hash_dir(d, depth=''):
    """hashing all which is relevant incl. files dir, but no other subfolders"""
    if depth:
        depth = '-d %s' % depth
    cmd = hash_cmd % (d, depth)
    h0 = os.popen(cmd).read().split()[0]
    h0 += ''.join([hash_dir(d + '/' + i) for i in os.listdir(d) if 'files' in i])
    return md5(h0.encode('utf-8')).hexdigest()


def make_cache_dir():
    if not exists(d_cache):
        os.makedirs(d_cache)


class Flags:
    autoshort = ''

    class Actions:
        class list:
            d = True
            n = 'Display parsed tree'

            class verbose:
                d = False

        class clear_cache:
            short = 'cc'

        class build:
            class remove:
                n = 'Remove existing images with same name (only before commit of successfully built new one)'
                d = False

        class enter:
            n = 'Enter currently building image with terminal. Disables "run". To run another command than the shell use --cmd. When the cmd is not present we fallback to /bin/sh'
            d = False

            class cmd:
                n = 'Enter currently building image with given command'
                d = '/bin/bash'

        class delete:
            a = True
            n = 'Delete image, i.e. allows rebuild. Will also remove old versions and remove all running containers'

    class name:
        n = 'Exactly match an image name, e.g. "arch_conda"'
        d = ''

    class match:
        n = 'Fuzzy match images, e.g. "cond" (using grep -E)'
        d = ''

    class parents:
        n = 'Include parents of selected image(s) at any operation'
        d = False

    class repeat_from:
        n = 'Repeat last build steps - even if they were succesful. 1: repeat all except first, -2: repeat last 2 successful'
        d = ''

    class mount_home_dir:
        n = 'Mount user home directory at each buildah run'
        d = False

    class yes:
        n = 'All questions: y'
        d = False


g = lambda o, k, d=None: getattr(o, k, d)


class Action:
    _post = cleanups

    def _pre():
        make_cache_dir()
        verify_have_tools()
        if not FLG.clear_cache:
            do(S.load_last_build_cache)
        S.filter_matching()
        S.hash_spec_dirs()
        buildah.images()

    def list():
        return S.dict() if not g(FLG, 'list_verbose') else S.verbose_dict()

    def build():
        # build top down (->sorted):
        for spec in sorted(S.work_tree['specs'], key=lambda i: i['dir']):
            st = spec['status']
            if st == st_current:
                return app.info('Local image is up to date', **spec)
            S.d_cur = d = spec['dir']
            do(img.build, spec)

    def enter():
        pass

    def delete():
        pass

    def clear_cache():
        system('rm -f "%s"' % fn_last_state)


# def run():
#     breakpoint()  # FIXME BREAKPOINT
#     make_cache()
#     verify_have_tools()
#     if FLG.clear_cache:
#         os.system('rm -f "%s"' % fn_last_state)
#     do(S.load_last_build_cache)
#     S.set_matching(match=FLG.name)
#     buildah.images()

#     if FLG.list:
#         return S.dict()

#     if FLG.enter:
#         verify_have_one()
#         return do(img.enter, dir=S.d_cur, cmd=FLG.cmd)

#     if FLG.delete:
#         verify_have_one()
#         do(img.delete_all, dir=S.d_cur)

#     if FLG.run:
#         verify_have_one()
#         cleanups.extend([cleanup_write_state, clean_temp_dir])
#         spec = img.spec(S.d_cur)
#         if FLG.repeat_from:
#             i = int(FLG.repeat_from)
#             actions = spec.get('actions', [])
#             spec['actions'] = actions[:i]

#         if '0' in FLG.run:
#             app.warn('Forgetting build container - rebuilding')
#             spec['C'] = None

#         m = {0: img.set_delete_before_commit, 1: img.build, 2: img.commit, 3: img.run}
#         last = True
#         app.info('Running steps: %s' % FLG.run)
#         for i in [0, 1, 2, 3]:
#             if i == 2 and last == False:
#                 app.info('skipping commit, no build')
#                 continue
#             if str(i) in FLG.run:
#                 last = do(m[i], dir=S.d_cur)
#     return S.dict()


# partial(app.die, example='./my_reg.com[:port]::library/base1/base2')


class State:
    # _delete_before_commit = False
    # by_img = None
    d_root = '.'
    # img_by_dir = None
    _d_tmp = None
    # d_cur = None
    # _selected_spec_dirs = None
    work_tree = None
    # buildah images results:
    _commited_local_images = None

    def __init__(s):
        # s.by_img, s.d_matching, s.img_by_dir, s.work_tree = {}, [], {}, {}
        s.work_tree = {}
        s._d_tmp = mkdtemp()

    def load_last_build_cache(s):
        ls = read_file(fn_last_state, dflt='')
        if ls:
            ls = json.loads(ls)
            [setattr(s, k, v) for k, v in ls.items()]

    def hash_spec_dirs(s):
        for m in S.work_tree['specs']:
            d = m['dir']
            m['hash'] = hash_dir(m['dir'], depth=1)[:6]

    def filter_matching(s):
        """Set to build directory, if match is unique"""
        s.d_cur, s._selected_spec_dirs = False, []

        cs = (
            os.popen('fd -t d | grep -v "\.files" | grep -E "%s"' % FLG.match)
            .read()
            .splitlines()
        )
        w = S.work_tree
        w['filters'] = {'match': FLG.match, 'name': FLG.name}
        dirs = set()
        root_dirs = set(os.listdir())  # registry, not image spec on top level
        for c in cs:
            # c like 'artifacts.foo.com::devapps/arch/arch_conda'
            parts = c.split('/')
            s._selected_spec_dirs.append(c)
            n = parts[-1]
            if not FLG.name or n == FLG.name:
                if not c in root_dirs:
                    dirs.add(c)
            if FLG.parents:
                while '/' in c:
                    c = c.rsplit('/', 1)[0]
                    if not c in root_dirs:
                        dirs.add(c)
        # status fixed for local ones in subsequent images run:
        w['specs'] = [{'dir': i, 'status': 'nonlocal'} for i in sorted(dirs)]

    #        # if len(dirs) == 1:
    #        #     app.info('Exact match -> setting image dir', dir=r[0])
    #        #     s.d_cur = r[0]

    #    # def spec(s, dir=None):
    #    #     d = dir or s.d_cur
    #    #     i = s.img_by_dir[d]
    #    #     return s.by_img[i]

    #    def remember(s, fn, args, kw):
    #        cur = s.spec()
    #        cur.setdefault('actions', []).append(ser_act(fn, args, kw))

    def dict(s):
        g, c = getattr, callable
        return {k: g(S, k) for k in dir(S) if not k.startswith('_') and not c(g(S, k))}

    def verbose_dict(s):
        d = s.dict()
        s.add_git_log(d)
        return d

    def add_git_log(s, d):
        cmd = 'git log --oneline %s --name-status "%s"'
        for s in reversed(d['work_tree']['specs']):
            days, d = s.get('age', 'd')[:-1], s['dir']
            if days:
                days = '--since "%s days ago" ' % days
            gl = cmd % (days, d)
            ls = os.popen(gl).read().strip()
            if not ls:
                app.warn('Not git managed')
                return
            ls = ls.splitlines()
            r = []
            while ls:
                l = ls.pop()
                if '\t' in l[:10] and d in l:
                    l = l.replace(d + '/', '')
                    if '/' in l:
                        if not 'files' in l.split('/', 1)[0]:
                            continue
                r.append(l.replace('\t', ' '))
            s['git log since'] = r

    __repr__ = lambda s: json.dumps(s.dict(), indent=2)


S = State()
# ser_act = lambda fn, args, kw: '%s %s %s' % (fn, str(args), str(kw))

##spec_by_dir = lambda dir: S.by_img.get(S.img_by_dir.get(dir))


die = lambda *a, **kw: app.die(*a, **kw)


def repo_and_ns(s):
    m = {}
    lns = s.split('::')
    if not len(lns) == 2 or not '.' in lns[0]:
        die('first part of dir must be registry:namespace')
    m['repository'] = lns[0]
    m['namespace'] = lns[1]
    return m


# @decorator
# def remembered(func, maxms=60000, *args, **kw):
#    """Writing image building steps into our log which is written at exitted
#    So that we can remember what was already run for a certain build and skip it.
#    """
#    remb = kw.pop('remember', True)
#    t0 = now()
#    fn = func.__name__
#    sa = ser_act(fn, args, kw)
#    if remb:
#        for a in S.spec().get('actions', []):
#            if a == sa:
#                return app.warn('skip: %s' % fn, args=args, **kw)
#    result = func(*args, **kw)
#    if not remb:
#        return result
#    S.remember(fn, args, kw)
#    S._dt_last_cmd = dt = now() - t0
#    w = app.warn if dt > maxms else app.info
#    w('%s took %d ms' % (fn, dt))
#    return result


B = 'buildah '

strptime = datetime.strptime
unix0 = datetime(1970, 1, 1)

st_current, st_outdated, st_unknown = 'current', 'outdated', 'unknown'


class buildah:
    def images():
        now = time.time()
        p, j = os.popen, json.loads
        l = S._commited_local_images = j(p(B + 'images --json').read().strip()) or []

        def gb(s):
            s, u = s.split()
            return float(s) if u == 'GB' else float(s) / 1024.0 if u == 'MB' else 0

        m = {'count': len(l), 'total': '%s GB' % int(sum([gb(i['size']) for i in l]))}
        app.info('Local images', **m)
        specs = S.work_tree['specs']
        S.work_tree['local images'] = m
        for i in l:
            ns = i['names']
            ns = [n.split(':') for n in ns if not ':latest' in n or len(ns) < 2]
            ns = sorted(ns, key=itemgetter(1))[-1]
            f = '%Y-%m-%dT%H:%M:%S'
            utc_dt = datetime.strptime(i['createdatraw'].split('.', 1)[0], f)
            ts = i['ts'] = (utc_dt - unix0).total_seconds()
            n = i['name'] = ns[0].rsplit('/', 1)[-1]
            t = i['tag'] = ns[1]
            s = [k for k in specs if k['dir'].endswith('/' + n)]
            assert len(s) < 2
            if s:
                s = s[0]
                s['age'] = '%sd' % int((now - ts) / 86400)
                s['status'] = st_current if s['hash'] in t else st_outdated
                s['size'] = i['size']

    def test_build_avail(C):
        if not C:
            return
        if os.popen(B + 'run %s -- ls /' % C).read().strip():
            app.info('build present', cont=C)
            return C


#    def from_(spec):
#        cmd = 'buildah from "%(from)s"' % spec
#        app.debug(cmd)
#        C = os.popen(cmd).read().strip()
#        app.info('container', container_name=C)
#        return C

#    def pull(img, **kw):
#        # err = do(system, 'buildah pull "%s"' % img, no_fail=True)
#        return do(system, 'buildah pull "%s"' % img, **kw)

#    def copy(frm, to):
#        # updated always
#        cmd = 'buildah copy --add-history "%s" "%s" "%s"' % (S.C, frm, to)
#        app.info(cmd)
#        do(system, cmd)

#    def exists(fn):
#        cmd = B + 'run %s -- ls "%s" 2>/dev/null 1>/dev/null'
#        return not os.system(cmd % (S.C, fn))

#    def has_command(cmd):
#        cmd = B + 'run %s -- /bin/sh -c "command -v %s" 2>/dev/null 1>/dev/null'
#        return not os.system(cmd % (S.C, cmd))

#    @remembered
#    def run(cmd, add_history=True, **kw):
#        app.info('%s (inside)' % cmd.split(' ')[0].replace('/.work/', ''), cmd=cmd)
#        h = '--add-history' if add_history else ''
#        cmd = 'buildah run %s %s %s -- %s' % (volmounts(), h, S.C, cmd)
#        app.info(cmd)
#        do(system, cmd)

#    @remembered
#    def env(vars):
#        e = ' '.join([' -e %s=%s ' % (k, v) for k, v in vars.items()])
#        do(system, 'buildah config --add-history %s %s' % (e, S.C))

#    @remembered
#    def entrypoint(ep):
#        b = 'buildah config'
#        do(system, b + ''' --add-history --entrypoint '[ "%s" ]' %s''' % (ep, S.C))

#    @remembered
#    def add_to_buildenv(vars):
#        fn = S._d_tmp + '/build_env.step'
#        s = '\n'.join(['export %s="%s"' % (k, v) for k, v in vars.items()])
#        write_file(fn, s)
#        buildah.copy(fn, '/.work/build_env.step')
#        add_script('add_to_buildenv.sh', add_to_buildenv)
#        buildah.run('/.work/add_to_buildenv.sh')

#    @remembered
#    def commit(img, build_img):
#        x = datetime.now()
#        tagged = '%s:latest %s:%s.%s.%s' % (img, img, x.year, x.month, x.day)
#        if S._delete_before_commit:
#            for k in img, tagged:
#                do(
#                    system,
#                    'buildah rmi -f "%s" 2>/dev/null; echo ok' % k,
#                    no_fail=True,
#                )
#        do(system, 'buildah commit %s %s' % (build_img, img))
#        do(system, 'buildah tag ' + tagged)


# def volmounts():
#    v = ''
#    if FLG.mount_home_dir:
#        v = ' -v "%(HOME)s:%(HOME)s"' % os.environ
#    return v


# def add_script(name, script=None):
#    dir = '/.work'
#    if name.startswith('/'):
#        dir, name = name.rsplit('/', 1)
#    fn = S._d_tmp + '/%s' % name
#    if script:
#        write_file(fn, script, chmod=0o755)
#    else:
#        os.system('chmod 755 "%s"' % name)
#    buildah.copy(fn, dir + '/' + name)


# class steps:
#    """Steps we log in the cache and won't repeat if done already """

#    def copy_workdir(dir, **kw):
#        """
#        Copying an image definition dir (w/o it't sub img definitions) into a container.

#        - We go via the tempdir on the host, so that we can delete the sub img folders.
#        - We detect runnable scripts and chmod +x them, plus add #!/bin/sh if not given
#        """
#        cmd = 'cp -a "%s/"* "%s/"' % (dir, S._d_tmp)
#        do(system, cmd)
#        for sub in os.listdir(S._d_tmp):
#            fn = S._d_tmp + '/' + sub
#            if os.path.isdir(fn) and sub[0] == ':':
#                os.system('rm -rf "%s"' % fn)
#            if is_runnable(sub):
#                s = read_file(fn)
#                if not s.startswith('#!'):
#                    app.info('Adding #!/bin/sh', fn=sub)
#                    s = '#!/bin/sh\n' + s
#                l = s.split('\n', 1)
#                s = '%s\n\n. /.work/build_env\n. /enter_env\n%s' % (l[0], l[1])
#                write_file(fn, s, chmod=0o755)
#        buildah.copy(S._d_tmp, '/.work')
#        buildah.run('touch /.work/build_env')
#        app.debug('copied workdir into image')


# is_runnable = lambda n: n.endswith('.sh') or '.run:' in n


class img:
    def build(spec):
        """Recursively pull or build parents"""
        img.complete_spec(spec)

        for step in sorted(os.listdir(spec['dir'])):
            breakpoint()  # FIXME BREAKPOINT
            if not ':' in step:
                step += ':'
            typ, n = step.split(':', 1)
            if not '.' in typ:
                continue
            nr, mode = typ.split('.', 1)
            if not nr.isdigit():
                continue
            mode = {'from': 'from_'}.get(mode, mode)
            # if not spec['local']['build'] and not mode == 'from_':
            # from is the first - if present. If not, we use the parent
            if not mode == 'from_':
                do(img.pull_or_build_parent, spec=spec)
                modes.from_('', spec)
            moderunner = getattr(modes, mode, None)
            if not moderunner:
                app.die('Mode not supported', step=step, mode=mode)
            r, p = repl_dollar_var_with_env_val(step, ask_on_fail=True, get_vals=True)
            if p:
                buildah.add_to_buildenv(p)
            app.info('build step: %s' % step)
            breakpoint()  # FIXME BREAKPOINT
            moderunner(step, spec)

    def complete_spec(spec):
        """Analyse and take appart a directory in the tree, adding infos which list did not show"""
        breakpoint()  # FIXME BREAKPOINT
        m = spec
        # if m:
        #     S.C = m.get('C')
        #     img.check_is_local(m)
        #     return m
        dir = m['dir']
        app.debug('analyzing', dir=dir)
        l = dir.split('/')
        m['name'] = l[-1]
        m.update(repo_and_ns(l[0]))
        frm = [k for k in os.listdir(dir) if '.from:' in k]
        m['img'] = '%(repository)s/%(namespace)s/%(name)s' % m
        if len(frm) > 1:
            app.die('More than 1 from statements', dir=dir, frms=frm)
        if not frm:
            m['dir_parent'] = dp = '/'.join(l[:-1])
            p = img.spec(dp)
            m['from'] = p['img']
        else:
            s = frm[0].split('.from:', 1)[1].rsplit(':', 1)
            m['from'] = s[0].replace('::', '/') + '/' + s[1]
        i = m['img']
        m['version'] = 'latest'
        m['from'] += ':%(version)s' % m
        img.check_is_local(m)
        app.debug(i, **m)
        m['ts_analyzed'] = now()
        S.by_img[i] = m
        S.img_by_dir[dir] = i
        S.C = m.get('C')
        return m

    #    # def spec(dir):
    #    #     """Analyse and take appart a directory in the tree"""
    #    #     m = spec_by_dir(dir)
    #    #     if m:
    #    #         S.C = m.get('C')
    #    #         img.check_is_local(m)
    #    #         return m
    #    #     app.debug('analyzing', dir=dir)
    #    #     l = dir.split('/')
    #    #     m = {'dir': dir, 'name': l[-1]}
    #    #     m.update(repo_and_ns(l[0]))
    #    #     frm = [k for k in os.listdir(dir) if '.from:' in k]
    #    #     m['img'] = '%(repository)s/%(namespace)s/%(name)s' % m
    #    #     if len(frm) > 1:
    #    #         app.die('More than 1 from statements', dir=dir, frms=frm)
    #    #     if not frm:
    #    #         m['dir_parent'] = dp = '/'.join(l[:-1])
    #    #         p = img.spec(dp)
    #    #         m['from'] = p['img']
    #    #     else:
    #    #         s = frm[0].split('.from:', 1)[1].rsplit(':', 1)
    #    #         m['from'] = s[0].replace('::', '/') + '/' + s[1]
    #    #     i = m['img']
    #    #     m['version'] = 'latest'
    #    #     m['from'] += ':%(version)s' % m
    #    #     img.check_is_local(m)
    #    #     app.debug(i, **m)
    #    #     m['ts_analyzed'] = now()
    #    #     S.by_img[i] = m
    #    #     S.img_by_dir[dir] = i
    #    #     S.C = m.get('C')
    #    #     return m

    def check_is_local(spec):
        breakpoint()  # FIXME BREAKPOINT
        m = spec.setdefault('local', {})
        m['build'] = b = bool(buildah.test_build_avail(spec.get('C')))
        if b:
            app.info('%s' % spec['C'])
        m['img'] = f = img.is_local(spec['img'])
        m['from'] = i = img.is_local(spec['from'])
        app.info('local', **m)
        # if not b:
        # app.debug('resetting build actions')
        # spec['actions'] = []

    #    # def pull_or_build_parent(spec):
    #    #     if img.is_local(spec['from']):
    #    #         return
    #    #     err = do(buildah.pull, img=spec['from'], no_fail=True)
    #    #     if err:
    #    #         do(img.build, dir=spec['dir_parent'])
    #    #     buildah.images()
    #    #     assert img.is_local(spec['from'])

    def is_local(n):
        breakpoint()  # FIXME BREAKPOINT
        for h in S._commited_local_images:
            ns = h.get('names') or ()
            if n in ns or n + ':latest' in ns:
                return True
        return False


#    # def enter(dir, cmd):
#    #     m = S.spec(dir=dir)
#    #     app.info('Entering container', json=m)
#    #     app.warn('Your changes will NOT be recorded!')
#    #     if not buildah.has_command(cmd):
#    #         app.warn('Missing inside', cmd=cmd, fallback='/bin/sh')
#    #         cmd = '/bin/sh'
#    #         app.warn('No bash - using sh')
#    #     buildah.run(cmd, add_history=False, remember=False)
#    #     app.info('exitted', cont=m['C'])

#    # def commit(dir):
#    #     spec = img.spec(dir)
#    #     if not spec['local']['build']:
#    #         return app.info('nothing to commit', reason='no build')
#    #     do(buildah.commit, img=spec['img'], build_img=S.C)
#    #     system('buildah images | grep "%s"' % spec['img'])

#    # def set_delete_before_commit(dir):
#    #     spec = img.spec(dir)
#    #     S._delete_before_commit = True

#    # def run(dir):
#    #     spec = img.spec(dir)
#    #     if not spec['local']['img']:
#    #         app.die('Not present', img=img)
#    #     c = 'podman' if not os.system('command -v podman') else 'docker'
#    #     do(system, c + ' run -ti --rm %s "%s" /bin/bash' % (volmounts(), spec['img']))

#    # def delete_all(dir):
#    #     spec = img.spec(dir)
#    #     r = []
#    #     for i in S._commited_local_images:
#    #         if any([spec['img'] in n for n in (i.get('names') or ())]):
#    #             r.append(i)
#    #     if not r:
#    #         return
#    #     app.info('Will remove', json=r)
#    #     if have_tty() and not FLG.yes:
#    #         if not 'y' in input('Ok to delete [y/N]? ').lower():
#    #             app.die('unconfirmed')
#    #     for i in r:
#    #         do(system, 'buildah rmi -f "%s"' % i['id'])


# class modes:
#    def from_(step, spec):
#        S.C = spec['C'] = buildah.from_(spec=spec)
#        do(steps.copy_workdir, **spec)
#        if not buildah.exists('/enter_env'):
#            add_script('/enter_env', enter_env)
#            add_script('/enter.sh', enter)
#            buildah.env({'LC_ALL': 'en_US.UTF-8', 'LANG': 'en_US.UTF-8'})
#            buildah.entrypoint(('/enter.sh'))
#        spec['local']['build'] = True

#    def pkgs(step, spec, typ='distri'):
#        u = 'updated' if 'updated:' in step else ''
#        step = step.replace('updated:', '')
#        args = '"' + (step.split(':', 1)[1].replace('+', '" "') + '"')
#        add_script('pkg_inst.sh', pkg_inst)
#        buildah.run(cmd='/.work/pkg_inst.sh %s %s %s' % (typ, u, args))

#    def pip(step, spec):
#        return modes.pkgs(step, spec, typ='pip')

#    def yarn(step, spec):
#        return modes.pkgs(step, spec, typ='yarn')

#    def conda(step, spec):
#        return modes.pkgs(step, spec, typ='conda')

#    def add_user(step, spec):
#        add_script('useradd.sh', useradd)
#        username = step.split(':')[1]
#        buildah.run(cmd='/.work/useradd.sh %s' % username)

#    def run(step, spec):
#        buildah.run(cmd='/.work/%s' % step)

#    def files(step, spec):
#        if step.endswith(':'):
#            step = step[:-1]
#        s = ['#!/bin/sh', '( cd "/.work/%s/" && tar cf - . ) | tar xfv - -C /' % step]
#        add_script(step + '.sh', '\n'.join(s))
#        buildah.run(cmd='/.work/%s.sh' % step)

#    def add_path(step, spec):
#        P = step.split(':', 1)[-1]
#        s = ['#!/bin/sh']
#        for p in P.split('+'):
#            p = '/' + p.replace('__', '/')
#            s.append('''echo -e 'export PATH="%s:$PATH"' >> /enter_env''' % p)
#        add_script('add_path.sh', '\n'.join(s))
#        buildah.run('/.work/add_path.sh')

#    def install_conda(step, spec):
#        fn = FN_CONDA
#        ffn = d_cache + '/' + fn
#        if not buildah.exists('/.work/conda.sh'):
#            if not exists(ffn):
#                cmd = 'curl "https://repo.anaconda.com/miniconda/%s" > "%s"' % (fn, ffn)
#                if os.system(cmd):
#                    app.die('could not download conda')
#            os.system('chmod +x "%s"' % ffn)
#            buildah.copy(ffn, '/.work/conda.sh')
#        add_script('conda_inst.sh', conda_inst)
#        buildah.run(cmd='/.work/conda_inst.sh')

#    # def is_runnable(step, spec):
#    #     cmd = '/.work/' + step
#    #     app.info(step)
#    #     system('cat "%s/%s"' % (spec['dir'], step))
#    #     buildah.run(cmd=cmd)


# def cleanup_write_state():
#    print('dumping state', fn_last_state)
#    write_file(fn_last_state, json.dumps(S.dict(), indent=4), mkdir=True)


# def clean_temp_dir():
#    d = S._d_tmp
#    if exists(d) and ('tmp' in d or 'temp' in d):
#        os.system('rm -rf "%s"' % d)


def verify_have_tools(required=['buildah', 'fd', 'curl']):
    miss = lambda t: os.system('command -v %s >/dev/null' % t)
    [app.die('Required tool missing', tool=t) for t in required if miss(t)]


# def verify_have_one():
#    if not S.d_cur:
#        m = 'Require exactly one matching image (d_cur)'
#        app.die(m, found=len(S._selected_spec_dirs))


main = lambda: run_app(Action, flags=Flags)


if __name__ == '__main__':
    main()

# enter_env = '''
# export LC_ALL=en_US.UTF-8
# export LC_CTYPE=en_US.UTF-8
# export LANG=en_US.UTF-8
# export LANGUAGE=en_US.UTF-8
#'''


# enter = '''#!/bin/sh
# . /enter_env
# eval "$@"
#'''
# add_to_buildenv = '''#!/bin/sh
# cat /.work/build_env.step >> /.work/build_env || true
#'''

# useradd = '''#!/bin/sh
# set -e
# . /.work/build_env || true
# username="$1"
# userdel $username && rm -rf /home/$username || true
# useradd -m -u 1000 -g users -d /home/$username -s /usr/bin/fish $username
# command -v sudo && echo "$username ALL=(ALL) ALL" >> /etc/sudoers
# echo -e ''$userpw'\n'$userpw'' | passwd $username
#'''

# pkg_inst = '''#!/bin/sh
# set -ex
# . /.work/build_env || true

# function set_packager {
#    command -v "apt-get" && { pkger="apt"; return; }
#    command -v "yum"     && { pkger="yum"; return; }
#    command -v "pacman"  && { pkger="pacman"; return; }
#    echo "no package manager"
#    exit 1
# }

# function update_pacman {
#   echo "updating pacman"
#   pacman --noconfirm -Syu
# }

# function install_pacman {
#   pacman --noconfirm -S "$@"
# }


# function update_yum {
#   echo "updating yum"
#   yum -y update
# }

# function install_yum {
#   yum -y install "$@"
# }

# function update_apt {
#   echo "updating apt"
#   apt-get -y update
# }

# function install_apt {
#   apt-get -y install "$@"
# }

# function install_yarn {
#    yarn global add "$@"
# }

# function install_pip {
#    pip install "$@"
# }

# function install_conda {
#    conda install -y "$@"
# }

# function main {
#    . /enter_env # possibly path -> e.g. pip elsewhere
#    if [ "$1" == "distri" ]; then
#        set_packager
#    else
#        pkger="$1"
#    fi
#    shift
#    test "$1" == updated && { update_$pkger; shift; }
#    install_$pkger "$@"

# }


# main "$@"
#'''

# conda_inst = '''#!/bin/sh
# set -x
# rm -rf /opt/conda
# /.work/conda.sh -b -p /opt/conda
# rm -f /etc/profile.d/conda.sh
# ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh
# echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc
# echo "conda activate base" >> ~/.bashrc
# find /opt/conda/ -follow -type f -name '*.a' -delete
# find /opt/conda/ -follow -type f -name '*.js.map' -delete
# /opt/conda/bin/conda clean -afy
# echo -e '
# export PATH="/opt/conda/bin:$PATH"
# export CONDA_EXE="/opt/conda/bin/conda"
# export CONDA_PREFIX="/opt/conda"
# export CONDA_PROMPT_MODIFIER="(base)"
# export CONDA_SHLVL="1"
# export CONDA_PYTHON_EXE="/opt/conda/bin/python"
# export CONDA_DEFAULT_ENV="base"
# export _CE_M=
# export _CE_CONDA=
# export _CONDA_SHLVL="1"
#' >> /enter_env
#'''
