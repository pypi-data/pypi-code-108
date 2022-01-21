#!/usr/bin/env python
"""
File is called by the shell when a test script is to be run.
Our job: Embed it into wanted environ.
sys.argv[1]: the test script
Rest in environ
"""

import os
import pdb
import sys
import time
from functools import partial

breakpoint = pdb.set_trace

env = os.environ

# print('ing build env', os.environ)
# print('args', sys.argv)
# print('env', os.environ)

d_repo = os.path.abspath(os.curdir)
d_rwdir = d_repo + '/.devapp_rw_top_layer'
d_assets = '/assets'
d_rootfs = d_assets + '/rootfs'
d_rootfss = os.listdir(d_rootfs)
dt = lambda: now() - t0
now = lambda: int(time.time() * 1000)
uc = lambda s: s.upper()
nosl = lambda s: s.replace('/', '-')
listed = (
    lambda s: list(s)
    if isinstance(s, (tuple, list))
    else [p.strip() for p in s.split(',')]
)
pretty_d = lambda d: ', '.join(['%s: %s' % (k, str(v)) for k, v in d.items()])
commit_msg = lambda: env['CI_COMMIT_MESSAGE']
d_abs_checkout = lambda: env['CI_PROJECT_DIR']
t0 = now()


class Log:
    def msg(self, msg, **kw):
        print('%6s %6s %s %s' % (dt(), uc(kw.pop('level')), msg, pretty_d(kw)))


log = Log()
[setattr(log, l, partial(log.msg, level=l)) for l in ['debug', 'info', 'warn', 'error']]
# replace this with a check for a spec:
def fs_stack():
    s = env.get('dflt_fs_stack')
    if not s:
        log.warn('No dflt_fs_stack defined in this runner - picking "centos7"')
    return s or 'centos7'


mount_tmpl = 'mount -t overlay -o lowerdir="%s",upperdir="%s",workdir="%s" '
mount_tmpl += 'overlay "%s"'


def _union(lower, upper, dir_name, d_build):
    # http://blog.programster.org/overlayfs
    D = d_stack() + '/%s' % dir_name
    os.mkdir(D)
    os.mkdir(D + '.work')
    cmd = mount_tmpl % (lower, upper, D + '.work', D)
    runproc(cmd)
    ctx['mounts'].append(D)
    return D


def abs_dir(d):
    if d.startswith('/'):
        raise Exception('Sorry no absolute dirs')
    if d in d_rootfss:
        return d_rootfs + '/' + d
    raise Exception('Not available %s' % d)


# this keeps the stack dir - in order to cleanup even at crashes:
ctx = {'mounts': []}


def main(script, *args):
    if not '.git' in os.listdir(d_repo):
        raise Exception('Not in a checkout dir')
    if not os.path.exists(d_repo + '/' + script):
        raise Exception('Not found: %s' % script)

    stack = listed(fs_stack())

    # contains all done with the fsstack during test:
    if not os.path.exists(d_rwdir):
        os.mkdir(d_rwdir)
    log.debug('Building fs stack', stack=stack)

    stack.append(d_rwdir)
    env['dev_apps_top_layer'] = d_rwdir

    # must be within the repo, it is itself mounted by gitlab:
    ctx['d_stack'] = d_abs_checkout() + '/.devapp_fs_stack'

    os.mkdir(d_stack())

    make_union = partial(_union, d_build=d_stack())
    cur = abs_dir(stack.pop(0))
    dir_name = 0
    while stack:
        n = stack.pop(0)
        dir_name += 1
        dir_name, n = ('final', n) if not stack else (dir_name, abs_dir(n))
        cur = union(cur, n, dir_name=dir_name)

    # lastely we mount the repo into it:
    dn = d_abs_checkout()
    dnf = '%s/final%s' % (ctx['d_stack'], dn)
    log.debug('Mounting repo in', into=dnf)
    bindmount(d_abs_checkout(), dnf)

    make_script(script, *args)
    run_script()


def make_script(script, *args):
    a = ['#!/usr/bin/env bash']
    a.append('set -a')
    for k, v in os.environ.items():
        a.append("%s='%s'" % (k, v))
    a.append('set +a')
    a.append('cd "$CI_PROJECT_DIR"')
    a.append('echo -e "\\033[38;5;82;1m * Running %s: \\033[0;m \\n"' % script)
    a.append('%s %s' % (script, ' '.join(args)))
    a = '\n'.join(a)
    ts = '%(d_stack)s/final/testscript' % ctx
    with open(ts, 'w') as fd:
        fd.write(a)
    runproc('chmod +x "%s"' % ts)
    log.debug('Entry script written')  # , script=a)


def run_script():
    D = ctx['d_stack'] + '/final'
    log.info('Running test container')
    runproc('systemd-nspawn -M $CI_COMMIT_SHA -D "%s" /testscript' % D)


def bindmount(frm, to):
    runproc('mkdir -p "%s"' % to)
    runproc('mount -o bind "%s" "%s"' % (frm, to))
    ctx['mounts'].append(to)
    # print(str(os.listdir(d_stack() + '/final')))
    # print(cur)


def runproc(cmd):
    cmd = cmd.replace(d_abs_checkout(), '$CI_PROJECT_DIR')
    log.debug('Running', cmd=cmd)
    r = os.system(cmd)
    if r:
        raise Exception('Cmd failed: %s' % cmd)


d_stack = lambda: ctx.get('d_stack')


def cleanup():
    """umount all overlays then remove the stackdir"""
    log.info('Cleanup', mounts=ctx['mounts'])
    while ctx['mounts']:
        m = ctx['mounts'].pop()
        runproc('umount "%s" 2>/dev/null' % m)
    runproc('/bin/rm -rf "%s"' % d_stack())


if __name__ == '__main__':
    try:
        main(sys.argv[1], *sys.argv[2:])
    except Exception as ex:
        raise ex
    finally:
        cleanup()
