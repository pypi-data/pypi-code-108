import os
import tarfile
from fnmatch import fnmatch
from glob import iglob

from cytoolz.curried import curry
from cytoolz import peek
from click.exceptions import Abort

from genomoncology.parse.ensures import ensure_collection
from .base import Source
from .const import TGZ_PATH_DELIMITER, CLOUD_RE_PATTERN


@curry
class CollectFilePathsSource(Source):
    def __init__(self, path, glob=None, include_tar=False):
        self.path = path
        self.glob = glob
        self.include_tar = include_tar

    def __iter__(self):
        yield from collect_files(self.path, self.glob, self.include_tar)


def is_cloud_path(path):
    return CLOUD_RE_PATTERN.match(path) is not None


def find_files(paths, glob=None, include_tar=False):
    for path in ensure_collection(paths or ["."]):

        if path.startswith("~") and os.path.exists(os.path.expanduser(path)):
            path = os.path.expanduser(path)  # pragma: no cover

        # todo: handle "buckets", currently assumes single files only.
        if is_cloud_path(path):
            yield path

        elif os.path.isfile(path):
            yield path

        else:
            glob = ensure_collection(glob) or [None]
            yield from find_normal_files(glob, path)
            if include_tar:
                yield from find_tarred_files(glob, path)


def find_tarred_files(glob, path):
    for g in ["*.tgz", "*.tar.gz", "*.tar"]:
        pattern = ["**", g] if g else ["**"]
        pattern = os.path.join(path, *pattern)

        for file_path in iglob(pattern, recursive=True):
            file_path = os.path.realpath(file_path)
            tgz = tarfile.open(file_path)
            for member_path in tgz.getnames():
                member_name = os.path.basename(member_path)
                for g in ensure_collection(glob):
                    if fnmatch(member_name, g):
                        components = ["tgz", file_path, member_path]
                        yield TGZ_PATH_DELIMITER.join(components)


def find_normal_files(glob, path):
    for g in glob:
        pattern = ["**", g] if g else ["**"]
        pattern = os.path.join(path, *pattern)

        for file_path in iglob(pattern, recursive=True):
            yield os.path.realpath(file_path)


def collect_files(paths, glob=None, include_tar=False, **_):
    """ collect files finds all of the paths and sorts them alphabetically. """
    iterator = find_files(paths, glob=glob, include_tar=include_tar)
    try:
        _, iterator = peek(iterator)
    except Exception:
        print(
            "File {} could not be found! Please check file location.".format(
                ",".join(ensure_collection(paths))
            )
        )
        Abort()

    yield from iterator
