#!/usr/bin/env python
import os
from json import loads

from devapp.app import app
from devapp.tools import abspath, clean_env_key, dirname, exists, read_file, sp_call

env = os.environ
is_svc = lambda: env['type'] == 'Service'


def fs_build_dirs():
    m = dict([('$' + k, v % env) for k, v in d_fs])
    m['$fs'] = '' if is_svc() else m['$bd'] + '/fs'
    return m


d_fs = dict(
    DA_DIR='%(DA_DIR)s',
    bd='%(DA_DIR)s/build/%(DA_CLS)s',
    rd='%(DA_DIR_REPOS)s',
    # sd='%(DA_DIR_SNAPS)s',
).items()


def already_overlayed(frm, to):
    """ Not so easy since dirs can be shadowed, the only secure way is mounts"""
    overs = [l for l in read_file('/proc/mounts').splitlines()]
    # TODO!!
    return False


class FS:
    """
    This is in use by the app starter, before app is made
    WE HAVE NO DEVAPP.APP yet! run.py does set a fake InitApp class into us
    at process start, for basic logging.
    """

    initapp = None  # set by run.py to basic logging only mock
    inode = lambda fn: os.stat(fn).st_ino
    mkdir = lambda d: sp_call('mkdir', '-p', d) if not exists(d) else 0
    d_build = lambda e: '%(DA_DIR)s/build/%(DA_CLS)s' % e

    def app(level, msg, **kw):
        # just for logging before and after we have the app - see usage below:
        # must work with the fake init app as well, thats why:
        f = getattr(app, level, None) or getattr(FS.initapp, level)
        f(msg, **kw)

    def build_from_fs_stack(mode='shared', app_env=env, fs=None):
        supported = {'shared': ['symlink', 'copy_file', 'tarpipe']}
        run = supported.get(mode)
        if run is None:
            raise Exception('Not supported currently: FS building %s' % mode)
        # meth shared: built time
        e = app_env  # at build time r['env'], else sourced os.env
        name = clean_env_key(e['DA_CLS'])
        env_have_flag = 'da_have_%s_fs_%s' % (mode, name)
        if e.get(env_have_flag):
            return
        # runtime:
        if fs is None:
            # info('Building filesystem...')
            fs = read_file(FS.d_build(e) + '/fs_stack.json')
            # $bd and such. not in anymore:
            # for k, v in fs_build_dirs().items():
            #    fs = fs.replace(k, v)
            fs = loads(fs)

        # the sorting guarantees outer dirs set before their content inside
        # e.g. /etc mounted before /etc/systemd/system copied
        for k in sorted(fs, key=len):
            src, meth = fs[k]['from'], fs[k]['meth']
            if not meth in run:
                continue
            FS.app('info', meth, to=k, frm=src)
            getattr(FS, meth)(frm=src, to=k)
        # at build write env will happen for shared meths, at proc run we just need the export
        e[env_have_flag] = name

    def overlay(frm, to):
        """Overlay assumes to be the ONLY one done, i.e. in frm we do have
        a list of all lowers
        The hard part is to find out if the overlay already exists.
        """
        # FS.indod after overlay is frm[0] == to... don't trust that to check
        # if already done. Rather this:
        app = FS.app

        lower = '' + ':'.join(frm) + ''
        upper = to + '.upper'
        if already_overlayed(frm, upper):
            FS.app('debug', 'Already overlayed', target=to)
            return
        work = to + '.work'
        name = env.get('DA_CLS')
        for k in upper, work, to:
            if not exists(k):
                os.mkdir(k)
        overlay = [
            'mount',
            '-t',
            'overlay',
            name,
            '-o',
            'lowerdir=%s,upperdir=%s,workdir=%s' % (lower, upper, work),
            to,
        ]
        return FS.sp_call(*overlay)

    def can_mount(c=[]):
        """Non root requires fusefs/bindfs"""
        if not c:
            c.append(
                FS.bindmount
                if not os.geteuid()
                else FS.bindfsmount
                if os.system('hash bindfs 2>/dev/null') == 0
                else False
            )
        return c[0]

    def mount(frm, to):
        meth = FS.can_mount()
        app = FS.app
        if not meth:
            m = 'Cannot perform mount as user w/o bindfs'
            app('die', m, frm=frm, dest=to, remedy='Install bindfs')

        if os.path.isdir(frm):
            FS.mkdir(to)
        else:
            FS.mkdir(dirname(to))
            FS.sp_call('touch', to)
        if FS.inode(frm) == FS.inode(to):
            # inode check works also with bindfs
            FS.app('debug', 'Already mounted', frm=frm)
            return
        return meth(frm, to)

    def bindmount(frm, to):
        return FS.sp_call('mount', '--bind', frm, to)

    def bindfsmount(frm, to):
        # not in use. bubblewrap better?
        return FS.sp_call('bindfs', '-o', 'nonempty', '-n', frm, to)

    def copy_file(frm, to):
        os.unlink(to) if exists(to) else 0
        return FS.sp_call('cp', frm, to)

    def tarpipe(frm, to, create=False):
        if not exists(to):
            if not create:
                raise Exception('Missing: %s' % to)
            FS.sp_call('mkdir -p "%s"' % to)
        cmd = '(cd "%s" && tar -cf - .) | (cd "%s" && tar -xpf -)'
        return FS.sp_call(cmd % (frm, to), name='tarpipe')

    def symlink(frm, to):
        if not exists(frm):
            raise Exception('Symlink source not exists %s' % frm)
        app = FS.app
        if os.path.islink(to):
            cur = os.readlink(to)
            if cur == frm:
                return
            os.unlink(to)
        if exists(to):
            raise Exception(
                'Symlink Target %s exists and is no symlink: %s' % (frm, to)
            )
        FS.mkdir(dirname(to))
        return FS.sp_call('ln', '-s', frm, to)

    def sp_call(*args, name=None):
        name, params = (name, args) if name else (args[0], args[1:])
        FS.app('debug', name, args=params)
        if len(args) == 1:
            err = os.system(args[0])
        else:
            err = sp_call(*args)
            if err:
                raise Exception('Error', err)


def full_url_and_path(env, url, mode):
    orig_url = url
    if url.startswith('http') or url.startswith('file://') or exists(url):
        if exists(url):
            url = 'file://' + abspath(url)
        return url, url[8:].split('/', 1)[1]
    if mode == 'oci':
        parts = url.split(':')
        if len(parts) == 1:
            app.die('No oci image format', url=url)
        if len(parts) == 2:
            # can't express auth and images endpoint in a single url, need
            # that indirection:
            return 'dockerio://%s' % url, url.replace(':', '')
        else:
            return url, url.split(':', 1)[1].replace(':', '')
    elif mode == 'git':
        if 'git@' in url:
            if ':' in url:
                return url, url.rsplit(':')[-1]
            return url, url.split('/', 1)[1]
        elif url.startswith('git://'):
            return url, url[8:].split('/', 1)[1]
    else:
        app.die('Not supported', mode=mode, url=url)
    if url[0] in ('/', ':'):
        url = url[1:]
    if not ':' in url:
        url = ':' + url
    pres, url = url.split(':', 1)
    if not pres:
        pre = 'DA_URL_%s' % mode.upper()
    else:
        pre = 'DA_URL_%s' % pres
    if not pre in env:
        app.die(
            'URL shortcut specified but not found in environ',
            url=orig_url,
            missing=pre,
            short=pres,
        )
    furl = env[pre] + '%s' + url
    sep = ':' if 'git@' in furl else '/'
    return furl % sep, url
