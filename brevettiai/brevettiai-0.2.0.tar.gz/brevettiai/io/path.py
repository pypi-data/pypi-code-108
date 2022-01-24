import os
import shutil
from functools import reduce


def movedir(srcdir, targetdir):
    """
    Move contents of directory on linux and windows file systems
    :param srcdir:
    :param targetdir:
    :return:
    """
    for file in os.listdir(srcdir):
        shutil.move(os.path.join(srcdir, file), os.path.join(targetdir, file))


def get_sep(path):
    sp = path.split('://', 1)
    return '/' if len(sp) == 2 else os.path.sep


def get_folders(path, bucket):
    rel_path = path.replace(bucket, '')
    pathsep = get_sep(path)
    return rel_path.strip(pathsep).split(pathsep)[:-1]


def join(*paths):
    """
    Join os paths and urls
    :param paths:
    :return:
    """
    sp = paths[0].split('://', 1)
    if len(sp) == 2:
        # Found protocol
        pathsep = '/'
        paths = list(paths)
        path_list = []
        for i, p in enumerate(paths[:-1]):
            if p != paths[i + 1][:len(p)] or "://" not in p:
                path_list.append(p)
        path_list.append(paths[-1])

        for i, p in enumerate(path_list[:-1]):
            if p[-1] == pathsep:
                path_list[i] = p[:-1]
        return pathsep.join(path_list)
    else:
        return os.path.join(*paths)


def safe_join(a0, *args):
    try:
        return join(a0, *args)
    except TypeError:
        return a0


def partition(items, func):
    """
    Partition a list based on a function
    :param items: List of items
    :param func: Function to partition after
    :return:
    """
    return reduce(lambda x, y: x[not func(y)].append(y) or x, items, ([], []))


def relpath(path, start=None):
    """
    Use os.path.relpath for local drives and adapted version for URIs
    Might be brittle when using URIs
    Return a relative version of a path
    """
    if not ("://" in path or (start is not None and "://" in start)):
        return os.path.relpath(path, start)

    sep = get_sep(path)
    if isinstance(path, bytes):
        curdir = b'.'
        pardir = b'..'
    else:
        curdir = '.'
        pardir = '..'

    if start is None:
        start = curdir

    if not path:
        raise ValueError("no path specified")

    start_abs = start
    path_abs = path
    start_drive, start_rest = start_abs.split("://", 1) if "://" in start_abs else os.path.splitdrive(start_abs)
    path_drive, path_rest = path_abs.split("://", 1) if "://" in path_abs else os.path.splitdrive(path_abs)
    if os.path.normcase(start_drive) != os.path.normcase(path_drive):
        raise ValueError("path is on mount %r, start on mount %r" % (
            path_drive, start_drive))

    start_list = [x for x in start_rest.split(sep) if x]
    path_list = [x for x in path_rest.split(sep) if x]
    # Work out how much of the filepath is shared by start and path.
    i = 0
    for e1, e2 in zip(start_list, path_list):
        if os.path.normcase(e1) != os.path.normcase(e2):
            break
        i += 1

    rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return curdir
    return sep.join(rel_list)
