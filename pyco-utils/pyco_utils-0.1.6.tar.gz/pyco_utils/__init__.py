import os
import sys
import string
import random
from hashlib import md5

from . import (
    _compat,
    _format,
    _json,
    colog,
    decorators,
    form_data,
    reverify,
    const,
)

__version__ = '0.1.6'


def md5sum(content):
    m = md5()
    if not isinstance(content, bytes):
        content = content.encode('utf-8').strip()
    m.update(content)
    s = m.hexdigest().lower()
    return s


def short_uuid(length):
    charset = string.ascii_letters + string.digits
    return ''.join([random.choice(charset) for i in range(length)])


def ensure_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def dirpath(path, depth=1):
    """
    usage: index to source and add to sys.path
    >>> folder = dirpath(__file__, 1)
    >>> sys.path.insert(0, folder)
    """
    path = os.path.abspath(path)
    for i in range(depth):
        path = os.path.dirname(path)
    return path


def _generate_parent_dir(fp_path, limit=1, subdir=".git"):
    fn = os.path.abspath(fp_path)
    if os.path.isdir(fn):
        p = fn
    else:
        p = os.path.dirname(fn)
    while limit:
        p2 = os.path.join(p, subdir)
        if os.path.isdir(p2):
            limit -= 1
            yield p
        p3 = os.path.dirname(p)
        if p3 == p:
            limit = 0
        else:
            p = p3


def get_parent_dir(fp_path, subdir=".git"):
    _gen = _generate_parent_dir(fp_path, limit=1, subdir=subdir)
    ps = list(_gen)
    if len(ps) > 0:
        return ps[0]
