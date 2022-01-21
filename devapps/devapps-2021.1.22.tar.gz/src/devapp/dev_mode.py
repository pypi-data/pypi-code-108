import os
from fnmatch import fnmatch

from devapp import FLG, app, flag, run_app

is_dir = os.path.isdir
exists = os.path.exists


flag.str('pkg', '', 'package to download and install in dev mode')


def get_package_source(pkg):
    pass


def get_meta_yaml(match, download_if_not_local=False):
    ad = app.pkgs_dir
    if not exists(app.pkgs_dir):
        raise app.die(
            'No pkgs dir.',
            dir=app.pkgs_dir,
            hint=' Maybe keep_pkgs was set to false when creating this in constructor',
        )
    ap = os.listdir(app.pkgs_dir)
    app.log.debug('Packages', count=len(ap))
    p = [p for p in ap if fnmatch(p, match) and is_dir(ad + '/%s' % p)]


def dev_on_package(match):
    ad = app.pkgs_dir
    if not exists(app.pkgs_dir):
        raise app.die(
            'No pkgs dir.',
            dir=app.pkgs_dir,
            hint=' Maybe keep_pkgs was set to false when creating this in constructor',
        )
    ap = os.listdir(app.pkgs_dir)
    app.log.debug('Packages', count=len(ap))
    p = [p for p in ap if fnmatch(p, match) and is_dir(ad + '/%s' % p)]
    for pkg in p:
        get_package_source(pkg)
        # dev_install(pkg)
    return p


def main():
    """Called from max d package"""
    return dev_on_package('*%s*' % FLG.pkg)


install_dev_pkg = lambda: run_app(main)
