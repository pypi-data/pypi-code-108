#!/usr/bin/env python
# coding: utf-8

import os

exists = os.path.exists
abspatch = os.path.abspath
dirname = os.path.dirname


'''
Old, from devapp/arch/axc2, will need a few tools later:
"""
# OS Tools

Supporting various operations on the shell, like mkdir, chroot...

"""
import os, sys, stat, time, errno, re, inspect, platform
from os.path import exists
import json, socket, stat
import subprocess as sp
from . import sh
from axc_app.cli import say, die, dbg, quiet, warn, add_indent, pop_indent
from axc_app.app import app_dir, call, base_pid
from time import sleep, time
from .os_tools import j, exists, env, ls
import tempfile, uuid
import shutil
from fnmatch import fnmatch
from functools import partial
from axc_app.tools import cast_list, is_str, str8

join, isdir, islink = os.path.join, os.path.isdir, os.path.islink

piped_popen = partial(
    sp.Popen, shell=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE
)

XC = '/xc'


def term_width():
    width = 0
    try:
        import struct, fcntl, termios

        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(1, termios.TIOCGWINSZ, s)
        width = struct.unpack('HHHH', x)[1]
    except IOError:
        pass
    return width


def do_logo():
    """ show the AXC logo"""
    c = lambda c, m='38': '\\033[%s;5;%sm' % (m, c)
    with open(j(app_dir, 'logo')) as f:
        lg = f.read() + '\n'
    try:
        cols = term_width()
    except:
        print('welcome to axc2')
        return
    if not cols:
        return
    # lg = '\n'.join([l.ljust(cols) for l in lg.splitlines()])
    os.system("echo -e '\\e[48;5;233m'")
    for L in ('B', '1', '4', '5', '6', '7'):
        lg = lg.replace(L, L + L + L)

    for k, v in list(
        {
            '\n': '\n' + c(232),
            'BBB': c(233),
            '111': c(236),
            '444': c(82),
            '555': c(236),
            '666': c(235),
            '777': c(234),
            '=': '■',
        }.items()
    ):
        lg = lg.replace(k, v)
    sys.stderr.write(lg + '\\033[0m\n')


def do_rmdir(dir):
    if '..' in dir:
        die('security')
    if not len(dir.split('/')) > 2:
        die('security')
    if not exists(dir):
        return
    say('removing directory', dir)
    shutil.rmtree(dir)


def do_clear_dir(dir, keep=['.hg*']):
    """clear a workdir
    """
    keep = cast_list(keep)
    # mode 1: all but .hg*
    if '..' in dir:
        die('security')
    dir = os.path.abspath(dir)
    if not os.path.exists(dir):
        dbg('not present', dir)
        return
    if not len(dir.split('/')) > 2:
        die('security')
    for f in os.listdir(dir):
        fn = join(dir, f)
        skip = 0
        for k in keep:
            if fnmatch(f, k):
                skip = 1
                break
        if skip:
            dbg('skipping', f)
            continue
        shutil.rmtree(fn) if isdir(fn) and not islink(fn) else os.unlink(fn)


def do_distri():
    """Linux Distribution Info"""
    res = os.popen('distribution').read()
    if res:
        o, k, arch, distro, version = res.split('|')[:5]
    version = version.split(' ')[0].strip()
    return {
        'os': o,
        'kernel': k,
        'arch': arch,
        'distro': distro,
        'ver': version,
    }


def chmodx(fn):
    st = os.stat(fn)
    os.chmod(fn, st.st_mode | stat.S_IEXEC)


class masked_dir:
    """overlays a directory with an empty temp dir
    useful for e.g. prefix build where we can not rm -rf before, e.g. /opt/nginx
    """

    def __init__(self, d_tgt, d_src=None, exit_remove=True, **kw):
        self.kw = kw
        self.d_tgt = d_tgt
        self.d_src = d_src
        self.exit_remove = exit_remove

    def __enter__(self):
        if not self.d_src:
            self.d_src = tempfile.mkdtemp()
        add_indent('Masking', self.d_tgt, 'with', self.d_src)
        mount(self.d_src, self.d_tgt)
        return self

    def __exit__(self, *a):
        pop_indent('')
        run('umount "%s"' % self.d_tgt)
        if self.exit_remove:
            shutil.rmtree(self.d_src)


def mount(s, t):
    'bind mount. creates mountpoint.'
    s, t = os.path.abspath(s), os.path.abspath(t)
    if not exists(s):
        die('mount fails, source dir not found', s)
    if not exists(t):
        run('mkdir -p "%s"' % t)
    if os.stat(s).st_ino == os.stat(t).st_ino:
        dbg('source already mounted to target', s, '->', t)
        return
    run('mount -o bind "%s" "%s"' % (s, t))


def do_swapon(gigs=2, no_fail=None):
    """creates a /swapfile and activates it.
    If you set gigs to 0 we switch swapping off and delete the file.
    https://www.digitalocean.com/community/tutorials/how-to-add-swap-on-ubuntu-14-04
    """
    fn_s = '/swapfile'
    if not gigs:
        run('swapoff -a; rm -f ' + fn_s)
        return
    if gigs > 4:
        die('max 4 gig. not', gigs)
    if os.path.exists(fn_s):
        run('swapon -s')
        if no_fail:
            return
        die('have already', fn_s)
    # and proceeding with chmod, mkswap & swapon commands. Bingo ! It worked.
    # alternative (fallocate sometimes fail):
    # sudo dd if=/dev/zero of=/myswap count=4096 bs=1MiB
    run(
        [
            'fallocate -l %sG %s' % (gigs, fn_s),
            'chmod 600 ' + fn_s,
            'mkswap ' + fn_s,
            'swapon ' + fn_s,
            'swapon -s',
        ]
    )
    os.system('free -h | grep -v Mem:')
    return True


# ----------------------------------------------------------------------- Tools
def do_deep_copy(src, dest):
    """
    Copy a directory via a tarpipe, i.e. including all perms
    """
    s, d = src, dest
    if not exists(s):
        die('not exists:', s)
    do_mkdir(d)
    run('(cd "%s" && tar -cf - .) | (cd "%s" && tar -xpf -)' % (s, d))


def do_mkdir(directory):
    """ make a directory tree, assuring root directory is present
    """
    d = directory
    if d.startswith('/'):
        # plausi:
        root = '/' + d.split('/')[1]
        if not os.path.exists(root):
            die('Security:', 'Top level dir must exist, does not:', root)
    if not os.path.exists(d):
        run('mkdir -p "%s"' % d)
    return d


# -------------------------------------------- file change monitor
_stats_by_dir = {}


class ChangeDetected(Exception):
    pass


def do_run_on_change(
    monitored_dir,
    depth=1,
    monitored_types='.py',
    check_every=1,
    cmd='echo "change!"',
):
    """
    runs the given command if sth changes in the watched monitored_dir.
    Example: Regenerate help on change.
    ```
    axc os.run_on_change "/xc/bin/axc_app" depth=2 '/xc/bin/axc gen_help'
    ```
    """
    monitored_types = monitored_types.split(',')
    d = os.path.abspath(monitored_dir)
    if not exists(monitored_dir):
        die('not exists', d)
    kw = dict(locals())
    kw['init'] = 1
    check_dir(**kw)
    kw.pop('init')
    do_run = 1
    while 1:
        if do_run:
            if isinstance(cmd, str):
                run(cmd)
            else:
                call(cmd)
        do_run = 0
        sleep(check_every)
        try:
            check_dir(**kw)
        except ChangeDetected as ex:
            say('Change in', ex)
            do_run = 1


def check_files(d, monitored_types, init):
    for f in ls(d):
        if not os.path.isfile(j(d, f)):
            continue
        do = 0
        for t in monitored_types:
            if f.endswith(t):
                do = 1
                break
        if not do:
            continue
        f = j(d, f)
        print(('checking', f))
        old = _stats_by_dir.get(f)
        new = _stats_by_dir[f] = os.stat(f)[8]
        if old != new and not init:
            raise ChangeDetected(f)


def check_dir(monitored_dir, monitored_types, depth, init=0, hir=0, **kw):
    if hir >= depth:
        return
    d = monitored_dir
    old = _stats_by_dir.get(d)
    now = _stats_by_dir[d] = os.stat(d)[8]
    if old != now:
        check_files(d, monitored_types, init)
    for ds in os.listdir(d):
        ds = j(d, ds)
        if not os.path.isdir(ds):
            continue
        check_dir(ds, monitored_types, depth, init, hir + 1)


# ---------------------------------------------------------- OS system commands
def run(
    cmd,
    d='',
    unshared=0,
    no_fail=0,
    fail_msg='',
    dimm=True,
    if_exists=0,
    chrooted=0,
    mounts=0,
    umounts=0,
    quiet=0,
    read=0,
    cd=None,
):
    """ mounts: we mount before the command, permanently.
    Within the command does not work over chroot when rprivate!
    umounts: independent list of clean up umounts after the command
    cd: set cwd parameter to this
    no_fail can be a number then we continue of exit code matches

    """
    if not cmd:
        dbg('no command to run')
        return
    oumounts = umounts

    if chrooted:
        om = mounts
        if mounts in (1, 2):
            # shortcut, one could list those explictly as well::
            mounts = (chrooted, XC, '/proc', '/sys', '/dev', ('/', '/host'))
            if om == 2:
                umounts = mounts
    if if_exists and not exists(os.path.join(d, cmd)):
        dbg('ignoring (not found)', cmd)
        return

    if isinstance(cmd, list):
        cmd = ' && '.join(cmd)
    if d:
        d = 'cd "%s" && ' % d
        cmd = d + cmd

    if chrooted:
        # /bin/bash in debian, in rh seems to be /usr/bin/bash, with still a
        # symlink to /bin though:
        cmd = 'chroot "%s" /bin/bash -c "%s"' % (chrooted, cmd)
    if mounts:
        ums = list(mounts)
        # the chroot as seen from outside:
        mount_prefix = ums.pop(0) or ''
        for um in ums:
            if isinstance(um, str):
                do_mount(um, mount_prefix + um)
            else:
                do_mount(um[0], mount_prefix + um[1])
    if unshared:
        cmd = "unshare -m bash -c '%s'" % cmd
    if read and quiet is 0:  # quiet is default, i.e. not set
        quiet = True
    if quiet < 1:
        dbg('dir:', cd or os.getcwd(), 'cmd:', cmd)
    # cmd = '/usr/bin/env %s' % cmd $ but builtins like export wont work then
    res = 1
    try:

        if read:
            return do_popen(cmd, timeout=read, cd=cd)
        elif quiet:
            res = sp.call(cmd, shell=True, cwd=cd)
        else:
            # colorized run
            fg = 236 if dimm else 249
            # FIXME: we really must do piped command chains,
            # not just && them together (sh # injection)
            ccmd = (
                'res=0;echo -n "\\033[1;38;5;%sm" && ' % fg
                + cmd
                + ' || res=$?; echo -n "\\033[0m"; exit $res'
            )
            # ccmd = 'export term=xterm-256 && ' + cmd
            res = sp.call(ccmd, shell=True, cwd=cd)

    except KeyboardInterrupt as ex:
        die('Keyboard Interrupt. Bye.', no_tb_msg=True)
    finally:
        if umounts:
            ums = list(umounts)
            mount_prefix = ums.pop(0) or ''
            for um in ums:
                if not isinstance(um, str):
                    um = um[1]
                run('umount "%s%s"' % (mount_prefix, um))
    if res == 0:
        return 'ok'
    if res:
        nf = str(no_fail)
        if (nf.isdigit() and res == no_fail) or nf == 'True':
            dbg('exit code', str(res), '- continuing.')
            return
        if fail_msg:
            fail_msg = '[%s]' % fail_msg
        die('failed (exit code %s):' % res, cmd, fail_msg)


def do_popen(cmd, timeout=120, cd=None):
    t1 = time()
    r = {'cmd': cmd}
    r['out'], r['err'] = piped_popen(cmd, cwd=cd).communicate()
    for k in 'out', 'err':
        r[k] = str8(r[k]).strip()
    return r


def rm(rmd, d=None, recreate=0):
    if isinstance(rmd, str):
        rmd = (rmd,)
    for r in rmd:
        if recreate:
            run('find . -mindepth 1 -delete', d=r)
        else:
            run('/bin/rm -rf "%s"' % r, d=d)


def do_kill(match='xxx', sigkill=None):
    """kill process matching 'match'
    if sigkill is set we kill with -9
    if not we check for max 5 seconds if all is gone otherwise we kill
    with sigkill.
    """

    def pids(quiet=0):
        procs = sh.grep(sh.ps('wwwax'), '-i', match)
        if not quiet:
            dbg(procs)
        res = [int(li.strip().split(' ', 1)[0]) for li in procs]
        res = [i for i in res if not i in (base_pid, os.getpid())]
        if quiet:
            dbg(res)
        return res

    sig = -15
    if sigkill:
        sig = -9
    for p in pids():
        try:
            sh.kill(sig, p)
        except Exception as ex:
            warn(p, str(ex))
    t1 = time()
    while time() - t1 < 5:
        if not pids(quiet=1):
            return
        sleep(0.5)
    ps = pids(quiet=1)
    warn('sending SIGKILL', ps)
    for p in ps:
        sh.kill(-9, p)
    if pids():
        die('could not kill', pids())


mount_log = []


def do_mount(src, tgt):
    """
    bind mount a dir to a target
    - creates the target if not exists.
    - checks of already mounted
    """
    s, t = src, tgt
    s, t = os.path.abspath(s), os.path.abspath(t)
    if not exists(s):
        die('mount fails, source dir not found', s)
    if not exists(t):
        if os.path.isdir(src):
            run('mkdir -p "%s"' % t)
        else:
            run('mkdir -p "%s"' % dirname(t))
            run('touch "%s"' % t)
    assert os.path.isdir(s) == os.path.isdir(
        t
    ), 'src and target must be same type, %s %s' % (src, tgt)
    if os.stat(s).st_ino == os.stat(t).st_ino:
        dbg('source already mounted to target', s, '->', t)
        return
    run('mount -o bind "%s" "%s"' % (s, t))
    mount_log.append([s, t])


class mounted(object):
    def __init__(self, src, tgt, indent=True):
        self.src, self.tgt, self.indent = src, tgt, indent

    def __enter__(self):
        if self.indent:
            add_indent('Mounting', self.src, '->', self.tgt)
        return do_mount(src=self.src, tgt=self.tgt)

    def __exit__(self, type, value, traceback):
        run('umount "%s"' % self.tgt)
        if self.indent:
            pop_indent()


def do_unp(
    files,
    output='$PWD',
    dump_command=False,
    forced_unpacker=None,
    list_unpackers=False,
):
    """
    Universal unarchiver (bash alias: 'unp').

    Shamelessly stolen from Armin's unp, stripped of click dep which we find
    overkill for non windows
    """

    class Click:
        class UsageError(Exception):
            pass

        class BadParameter(Exception):
            pass

        def format_filename(self, fn):
            return fn

        def echo(self, s, fg='green', err=False):
            fg = 'red' if err == False else fg
            from axc_app.cli import I, M, R, L

            f = {'green': M, 'red': R, 'yellow': I}.get(fg, L)
            say(f(s))

        secho = echo

    class Ctx(dict):
        def exit(self):
            sys.exit()

    from axc_app.tools import unp, cast_list
    from axc_app.cli import ctx as axc_ctx

    silent = axc_ctx.get('cli_q')
    files = cast_list(files)
    unp.click = click = Click()
    ctx = Ctx()

    if list_unpackers:
        unp.list_unpackers(ctx, 1, 1)

    from axc_app.tools.unp import get_unpacker_class

    unpackers = []

    for filename in files:
        filename = os.path.realpath(filename)
        if not os.path.isfile(filename):
            die('Could not find file "%s".' % click.format_filename(filename))
        if forced_unpacker is not None:
            unpacker_cls = forced_unpacker
        else:
            unpacker_cls = get_unpacker_class(filename)
        unpackers.append(unpacker_cls(filename, silent=silent))

    for unpacker in unpackers:
        if dump_command:
            unpacker.dump_command(output)
        else:
            unpacker.unpack(output)
'''
