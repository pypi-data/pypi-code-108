#!/usr/bin/env python3
# coding: utf-8
import os
from functools import cached_property

import volkanic.environ

packages = [
    'joker.aligner',
    'joker.broker',
    'joker.cast',
    'joker.environ',
    'joker.flasky',
    'joker.geometry',
    'joker.masquerade',
    'joker.minions',
    'joker.pyoneliner',
    'joker.relational',
    'joker.scraper',
    'joker.stream',
    'joker.studio',
    'joker.textmanip',
    'joker.xopen'
]

projects = [
    'joker-aligner',
    'joker-broker',
    'joker-cast',
    'joker',
    'joker-flasky',
    'joker-geometry',
    'joker-masquerade',
    'joker-minions',
    'joker-pyoneliner',
    'joker-relational',
    'joker-scraper',
    'joker-stream',
    'joker-studio',
    'joker-textmanip',
    'joker-xopen'
]


# this is deprecated
class GlobalInterface(volkanic.environ.GlobalInterfaceTrial):
    package_name = 'joker.environ'
    default_config = {}
    _meta = {}

    def under_temp_dir(self, ext=''):
        name = os.urandom(17).hex() + ext
        return self.under_data_dir('tmp', name, mkdirs=True)

    _get_conf_search_paths = None

    @cached_property
    def jinja2_env(self):
        # noinspection PyPackageRequirements
        from jinja2 import Environment, PackageLoader, select_autoescape
        return Environment(
            loader=PackageLoader(self.package_name, 'templates'),
            autoescape=select_autoescape(['html', 'xml']),
        )


class JokerInterface(GlobalInterface):
    package_name = 'joker.environ'

    # this method will be moved to JokerInterface at ver 0.3.0
    @classmethod
    def under_joker_dir(cls, *paths):
        path = os.environ.get('JOKER_HOME', cls.under_home_dir('.joker'))
        if not cls._meta.get('joker_dir_made'):
            os.makedirs(path, int('700', 8), exist_ok=True)
            cls._meta['joker_dir_made'] = True
        return os.path.join(path, *paths)

    @classmethod
    def _get_conf_path_names(cls):
        return [cls.project_name, cls._get_option('confpath_filename')]

    _options = {
        'confpath_dirname_sep': '/',
    }


ji = JokerInterface()


def _get_joker_packages():
    import pkg_resources
    _packages = []
    for pkg in pkg_resources.working_set:
        pn = pkg.project_name
        if pn.startswith('joker-') or pn == 'joker':
            _packages.append(pkg)
    return _packages


def _get_joker_packages_with_pkgutil():
    import pkgutil
    import joker
    # https://stackoverflow.com/a/57873844/2925169
    return list(pkgutil.iter_modules(
        joker.__path__,
        joker.__name__ + "."
    ))


def get_joker_packages(use_pkgutil=False):
    if use_pkgutil:
        return _get_joker_packages_with_pkgutil()
    else:
        return _get_joker_packages()


def under_joker_dir(*paths):
    return ji.under_joker_dir(*paths)
