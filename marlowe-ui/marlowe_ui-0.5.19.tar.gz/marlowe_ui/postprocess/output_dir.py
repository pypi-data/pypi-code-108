"""control output directory
"""

from pathlib import Path
from . import skel


class Error(Exception):
    pass


def prepare(path):
    """create output directory and copy contetns under skelton

    path is a pathlib.Path or string object for output directory
      if path does not exists try to be created.
    """

    # translate output directory to Path object
    if not isinstance(path, Path):
        path = Path(path)

    create(path)

    # copy contents from skelton
    skel.copy_contents(path)


def create(path):
    """test or create a directory as path

    path is a pahtlib.Path object or string to be created"""

    # output directory
    if not isinstance(path, Path):
        path = Path(path)

    # generate
    if path.exists():
        if not path.is_dir():
            raise Error('{} exists but is not directory'.format(path))
        else:
            # path already exists and is recognized as a directory
            pass
    else:
        # dig directory
        path.mkdir()
