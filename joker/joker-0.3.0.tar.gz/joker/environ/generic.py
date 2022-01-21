#!/usr/bin/env python3
# coding: utf-8

import os

import volkanic.environ
from volkanic.compat import cached_property

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
