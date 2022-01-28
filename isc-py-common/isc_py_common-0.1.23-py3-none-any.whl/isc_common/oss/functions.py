import os
import shutil
from pathlib import Path


def mekeDirs(name, logger, mode=0o777, exist_ok=False):
    try:
        os.makedirs(name=name, exist_ok=exist_ok, mode=mode)
        if not os.path.exists(name):
            logger.error(f'dirs: {name} not created.')
            return False
        return True
    except FileNotFoundError:
        logger.error(f'dirs: {name} not created.')
        return False


def copyTwo(src, dst, follow_symlinks=True):
    dir, _file = os.path.split(dst)
    os.chdir(dir)
    try:
        shutil.copy2(src=src, dst=_file, follow_symlinks=follow_symlinks)
        return True
    except FileNotFoundError:
        return False


def get_tmp_dir(base_dir=None):
    if base_dir is None:
        tmpdir = f'{str(Path.home())}{os.sep}tmp'
    else:
        tmpdir = f'{base_dir}{os.sep}tmp'

    if os.path.exists(tmpdir) is False:
        os.mkdir(tmpdir)

    return tmpdir
