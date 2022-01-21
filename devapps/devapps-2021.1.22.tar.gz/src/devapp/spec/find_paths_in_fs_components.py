import json
import os

from devapp.tools import dirname, exists, read_file, write_file

to_run_dir = lambda d, repo, phys_dir: d.replace(phys_dir, repo['run_dir'])


def find_bin_paths(comp_checkout_dir_check_dir):
    comp, cod, d = rcd = comp_checkout_dir_check_dir
    if exists(d + '/bin'):
        comp.setdefault('env_PATH', []).append(to_run_dir(d + '/bin', comp, cod))
    return rcd


def find_py_paths(comp_checkout_dir_check_dir):
    """
    Set PYTHONPATH according to package structure.

    Ok this is tricky. We want, when the comp is later mounted from
    checkout dir to run_dir, have the import statements working, allthough
    not pip installed (we might do this when we have an overlay later, but for
    now we try to be w/o unsharing whenever possible - and it IS possible,
    like in java or ruby, to find our modules just via an env enrichment -
    and that is PYTHONPATH in python.
    Problem though: python's packages declaration is not a declaration but code...
    But Since we have python we can execute that code.
    """
    # TODO: Comment that better
    # cod: checkout dir
    # d: a possible daemon dir:
    comp, cod, d = rcd = comp_checkout_dir_check_dir

    def add(dir_, comp=comp, cod=cod):
        pp = comp.setdefault('env_PYTHONPATH', [])
        pp.append(to_run_dir(dir_, comp, cod))

    if not exists(d):
        return rcd
    # first we check for daemon specific stuff:
    if any([f for f in os.listdir(d) if f.endswith('.py')]):
        add(d)
    fns = d + '/setup.py'
    if not exists(fns):
        return rcd
    # we cache the result of that setup.py import, this might take
    # long, sucks for repeated builds:
    st = os.stat(fns)
    # lets use pycache folder for that, this is gitignored for all sane python projects:
    fnc = d + '/.__pycache__/%s.%s.devapps.json' % (st.st_ino, st.st_mtime)
    if exists(fnc):
        j = read_file(fnc, '')
    else:
        # if this build toolchain would be written in go, they would hate python
        # for this. We have python, so ...piece of cak(e or a) to get the comp stuff:
        j = os.popen(
            '''cd "%s" && python -c 'if 1:
        import setuptools
        import json
        def fake_setup(**kw):
            l = [kw.get(l, "") for l in ("packages", "entry_points", "package_dir")]
            print(json.dumps(l, default=str))
        setuptools.setup = fake_setup
        import setup'
        '''
            % d
        ).read()
        os.makedirs(dirname(fnc)) if not exists(dirname(fnc)) else 0
        write_file(fnc, j)
    if not j:
        return rcd
    pkgs, eps, pkg_dirs = json.loads(j)
    # todo: create the entrypoints
    # for now only the stuff needed to run and that are the pypaths:
    pkgs = [p for p in pkgs if not '.' in p]
    # todo: currently we look only in pkgdirs:
    ds = (pkg_dirs or {'': ''}).values()
    [add(d + '/%s' % v) for v in ds]

    return rcd
