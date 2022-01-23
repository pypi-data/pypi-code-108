#!/usr/bin/env python3
# coding: utf-8

import os
from functools import wraps


def under_asset_dir(*paths):
    import joker.superuser
    from volkanic.utils import under_package_dir
    return under_package_dir(joker.superuser, 'asset', *paths)


def under_joker_superuser_dir(*paths):
    from joker.environ.provincial import under_joker_dir
    return under_joker_dir('superuser', *paths)


def make_joker_superuser_dir(*paths):
    from joker.environ.provincial import make_joker_dir
    return make_joker_dir('superuser', *paths)


def load_config(name):
    import yaml
    path = under_joker_superuser_dir(name)
    if os.path.isfile(path):
        return yaml.safe_load(open(path))


def report(data, name):
    import json
    if not name.endswith('.json'):
        name += '.json'
    make_joker_superuser_dir()
    path = under_joker_superuser_dir(name)
    with open(path, 'w') as fout:
        fout.write(json.dumps(data))


def silent_function(func):
    """Do not report any error"""

    @wraps(func)
    def sfunc(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseException:
            pass

    return sfunc


def startswith(s, *prefixes):
    for p in prefixes:
        if s.startswith(p):
            return True
    return False


def find_regular_files(dirpath, **kwargs):
    for root, dirs, files in os.walk(dirpath, **kwargs):
        for name in files:
            path = os.path.join(root, name)
            if os.path.isfile(path):
                yield path


def check_filesys_case_sensitivity(dirname='.'):
    from tempfile import TemporaryDirectory
    with TemporaryDirectory(prefix='.sus-tmp', dir=dirname) as tmp:
        return not os.path.exists(tmp.upper())
