#!/usr/bin/env python
"""
Building Containers


Merging filesystem layers
- either from dpull (oci compliant)
- plain dirs

using tar -> copy over
using union2 -> mount overlay(2)
"""

import json
import os
import socket
import time

from devapp.app import FLG, app, run_app
from mdvl.tools import add_metas, struct_code_block

exists = os.path.exists
abspath = os.path.abspath

root = os.geteuid() == 0


class Flags:
    autoshort = ''

    class skip_filesystem_adaptions:
        n = 'Do not run any FS changes, e.g. setting root pw. Default is True if we are not root.'
        d = False if root else True

    class write_markdown:
        n = 'Write infos into this file md formatted'

    class dirs:
        n = ('Exisiting layers or plain dirs - merged in comma sep. order given',)
        t = list
        d = ['./images']

    class target_dir:
        n = 'target filesystem directory'

    class make_tar:
        n = 'Pack together target dir into this file'

    class method:
        n = 'merge method. union requires overlay2. Supported: tar, union'
        d = 'tar'

    class rootpw:
        n = 'set root password (empty to not change)'
        d = 'devapp' if root else ''

    class allow_pts_logins:
        n = 'Allow machinectl logins for so many pts (0: skip this)'
        d = 8 if root else 0

    class allow_console_login:
        n = 'Allow console login when booted (via nspawn)'
        d = True if root else False

    class add_meta_data:
        n = 'Store meta data into target'
        d = True

    class tar_excludes:
        n = 'Add tar excludes as given'
        t = list
        d = [] if root else ['dev/*']


F = FLG


def die(msg, **kw):
    app.die(msg, **kw)


def run_cmd(cmd, msg='Running', no_fail=False):
    app.log.info(msg, cmd=cmd)
    res = os.system(cmd)
    if res:
        if no_fail:
            return res
        die('Failed - exitting')


def add_layer(ds, lay):
    app.log.info('Adding', layer=lay)
    dt = F.target_dir
    excl = FLG.tar_excludes or ''
    if excl:
        excl = ' '.join([' --exclude=%s ' % i for i in excl])

    if F.method == 'tar':
        run_cmd('tar -C  "%s/" %s --force-local -xf "%s"' % (dt, excl, ds + '/' + lay))
        return
    raise NotImplemented


def run():
    if not root:
        FLG.skip_filesystem_adaptions = True
    if not FLG.skip_filesystem_adaptions:
        run_cmd('chroot / sleep 0', 'Checking: Have chroot')
    if F.method == 'tar':
        run_cmd('tar --version | head -n1', 'Checking: Have tar')
    ds = F.dirs
    if not ds:
        die('No source dir')
    ds = F.dirs = [s[:-1] if s.endswith('/') else s for s in ds]

    if F.write_markdown and not F.add_meta_data:
        die('To write markdown we need to collect metadata')

    for d in ds:
        if not exists(d):
            die('Not found', dir=d)
        if d == F.target_dir:
            die('Source dir is target dir', dir=d)

    if F.make_tar and exists(F.make_tar):
        die('Exists', tar=F.make_tar)
    _ = F.write_markdown
    if _:
        F.write_markdown = _ = abspath(_)
        if not exists(_):
            app.log.info('Creating', file=_)
            run_cmd('mkdir -p "%s" && touch "%s"' % (_.rsplit('/', 1)[0], _))

    dt = F.target_dir
    dt = abspath(dt) if dt else ''
    dtar = abspath(F.make_tar) if F.make_tar else ''
    rm_work_dir = False
    if not dt and dtar:
        dt = abspath(ds[0]) + '.work'
        rm_work_dir = True
    else:
        if len(dt.split('/')) < 3 or dt == '/':
            die('Refusing (too short)', target_dir=dt)
    F.target_dir = dt

    for d in ds:
        do_dir(d)
    if not FLG.skip_filesystem_adaptions:
        adapt_fs()

    if F.add_meta_data:
        add_meta_data()

    if F.write_markdown:
        write_markdown()

    if dtar:
        do_tar(dtar)
    msg = 'Successfully created filesystem'
    if not FLG.skip_filesystem_adaptions:
        app.log.info(
            msg + '. Chroot uname output',
            out=os.popen('chroot "%s" uname -a' % dt).read(),
        )
    else:
        app.log.info(msg, dir=dt)

    if rm_work_dir:
        run_cmd('rm -rf "%s"' % dt, 'Removing work dir')


def do_tar(dtar):
    app.log.info('------------ BUILDING TAR ---------------')
    run_cmd('mkdir -p "%s"' % dtar.rsplit('/', 1)[0])
    run_cmd('( cd "%s/" && tar -cf "%s" . )' % (F.target_dir, dtar))


def adapt_fs():
    app.log.info('------------ ADAPT FILESYSTEM -----------')
    rp, dt = F.rootpw, F.target_dir
    if rp:
        r = run_cmd(
            "echo 'root:%s' | chroot '%s' chpasswd" % (rp, dt),
            'Changing root password',
            no_fail=True,
        )
        if r:
            app.log.error('Could not set password. chpasswd utility missing')
    nrc = F.allow_pts_logins
    with open(dt + '/etc/securetty') as fd:
        s = fd.read().splitlines()
    lines = [l for l in s if not 'pts' in l and not 'console' in l]
    for i in range(0, nrc):
        lines.insert(0, 'pts/%s' % i)
        app.log.info('Adding pts', nr=i)
    if F.allow_console_login:
        lines.insert(0, 'console')
        app.log.info('Adding console login')
    with open(dt + '/etc/securetty', 'w') as fd:
        fd.write('\n'.join(lines))


def find_files(d, match):
    return (
        os.popen('cd "%s" && find . -print |grep "%s"' % (d, match)).read().splitlines()
    )


def read(fn):
    with open(fn) as fd:
        s = fd.read()
        try:
            return json.loads(s)
        except:
            return s


def document(d, md):
    app.log.info('Documenting', d=d)
    for mani in find_files(d, 'manifestJson'):
        fmani = d + '/' + mani
        mani = read(fmani)
        for l in mani:
            md.append('RepoTags: %s' % ', '.join(l['RepoTags']))
            cfg = read(fmani.replace('manifestJson', l['Config']))
            md.append(struct_code_block(cfg, title='Config'))

            md.append('### Layers:')
            for L in l['Layers']:
                L = L.replace('/layer.tar', '')
                j = read(fmani.replace('manifestJson', L + '/json'))
                md.append(struct_code_block(j, title=str(j['config']['Cmd'])))


def write_markdown():
    app.log.info('------------ WRITE MARKDOWN -------------')
    dl = F.target_dir + '/.da_layers'
    md = ['# Build Documentation']
    md.append('')
    md.append(struct_code_block(dict(os.environ), 'Environment'))
    md.append('')

    for d in os.listdir(dl):
        md.append('## %s' % ' '.join(d.split('_')))
        md.append('')
        document(dl + '/' + d, md)
    s = read(F.write_markdown)
    sep = '<!-- DevApps Autodoc -->'
    if sep in s:
        pre, _, post = s.split(sep, 3)
    else:
        pre, post = '', ''
    md = sep.join((pre, '\n'.join(md), post))
    m = {
        'DA_T_Merged': time.ctime(),
        'DA_ROOT_PW': F.rootpw,
        'DA_BUILD_HOST': socket.gethostname(),
    }
    md = add_metas(md, m)
    with open(F.write_markdown, 'w') as fd:
        fd.write(md)


def add_meta_data():
    app.log.info('------------ ADD METADATA ---------------')
    # breakpoint()
    dl = F.target_dir + '/.da_layers'
    run_cmd('mkdir -p "%s"' % dl)
    i = 1
    for ds in F.dirs:
        dt = dl + ('/%s__' % i) + ds.rsplit('/', 1)[-1]
        run_cmd('mkdir -p "%s"' % dt)
        if exists(ds + '/.da_layers'):
            d1, d2 = (ds + '/.da_layers', dt)
        else:
            d1, d2 = (ds, dt)
        # tar --force-local -cf google.com:files.tar *
        dta = abspath(ds + '.%s.tar' % os.getpid())
        run_cmd('cd "%s" && tar --force-local -cf "%s" .' % (d1, dta))
        run_cmd('cd "%s" && tar --force-local -xf "%s" ' % (d2, dta))
        os.unlink(dta)
        i += 1
    size = os.popen('du "%s"  -d 0' % dl).read()
    app.log.info('Added metadata', count=i, size=size)


def do_dir(ds):
    s = ds.rsplit('/', 1)[-1]
    app.log.info('------------ DO DIR ---------------------%s' % s)
    dt = F.target_dir
    mani = ds + '/manifestJson'
    if exists(mani):
        with open(mani) as fd:
            mani = json.loads(fd.read())[0]
        layers = mani['Layers']
        run_cmd('mkdir -p "%s"' % F.target_dir)
        for l in layers:
            add_layer(ds, l)
    else:
        app.log.info('Merging as plain', dir=ds)
        add_plain_dir(ds)


def add_plain_dir(ds):
    if F.method == 'tar':
        dirs = (ds, F.target_dir)
        run_cmd('(cd "%s" && tar cf - | cd "%s" && tar xf - )' % dirs)
        return
    raise NotImplemented


main = lambda: run_app(run, flags=Flags)

if __name__ == '__main__':
    main()
