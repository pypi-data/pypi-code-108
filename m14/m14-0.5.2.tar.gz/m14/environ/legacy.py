#!/usr/bin/env python3
# coding: utf-8

import os.path
import sys

# noinspection PyPackageRequirements
import yaml
from volkanic.utils import under_home_dir

_conf = None


def _load_conf():
    paths = [under_home_dir('.m14-default.yml'), '/etc/m14-default.yml']
    for path in paths:
        if os.path.isfile(path):
            return yaml.safe_load(open(path))


def _get_default_prefix():
    if sys.platform.startswith('win'):
        return r'c:\data'
    return '/data'


def _get_conf():
    global _conf
    if _conf is None:
        _conf = _load_conf() or {}
    if 'default' not in _conf:
        _conf['default'] = _get_default_prefix()
    return _conf


def under_default_dir(package, *paths):
    conf = _get_conf()
    name = getattr(package, '__name__', str(package)).split('.')[-1]
    try:
        dir_ = conf[name]
    except LookupError:
        dir_ = os.path.join(conf.get('default'), name)
    return os.path.join(dir_, *paths)


