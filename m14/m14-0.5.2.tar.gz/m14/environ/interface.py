#!/usr/bin/env python3
# coding: utf-8

import os

import joker.environ


class GlobalInterface(joker.environ.GlobalInterface):
    package_name = 'm14.environ'

    def under_data_dir(self, *paths, mkdirs=False):
        if 'data_dir' not in self.conf:
            names = self.package_name.split('.')
            data_dir = os.path.join('/data/local', *names)
            self.conf.setdefault('data_dir', data_dir)
        return super().under_data_dir(*paths, mkdirs=mkdirs)