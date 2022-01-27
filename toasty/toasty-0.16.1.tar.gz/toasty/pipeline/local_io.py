# -*- mode: python; coding: utf-8 -*-
# Copyright 2020 the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""
Pipeline I/O using the local filesystem as a storage backend.

Note that pipeline processing *always* uses the local filesystem for
intermediate steps. This module is for scenarios where the final long-term
storage of processed data should also involve the local filesystem.

"""

__all__ = '''
LocalPipelineIo
'''.split()

import os.path
import shutil

from . import PipelineIo


class LocalPipelineIo(PipelineIo):
    """
    I/O for pipeline processing using the local disk.

    Parameters
    ----------
    path_prefix : str
        A path prefix that will be used for all I/O options.

    """
    _path_prefix = None

    def __init__(self, path_prefix):
        self._path_prefix = path_prefix

    def _export_config(self):
        return {
            '_type': 'local',
            'path': self._path_prefix,
        }

    @classmethod
    def _new_from_config(cls, config):
        return cls(config['path'])

    def _make_item_name(self, path_array):
        return os.path.join(self._path_prefix, *path_array)

    def check_exists(self, *path):
        return os.path.exists(self._make_item_name(path))

    def get_item(self, *path, dest=None):
        with open(self._make_item_name(path), 'rb') as f:
            shutil.copyfileobj(f, dest)

    def put_item(self, *path, source=None):
        fpath = self._make_item_name(path)

        cdir = os.path.split(fpath)[0]
        os.makedirs(cdir, exist_ok=True)

        with open(fpath, 'wb') as f:
            shutil.copyfileobj(source, f)

    def list_items(self, *path):
        dpath = self._make_item_name(path)

        for stem in os.listdir(dpath):
            yield stem, os.path.isdir(os.path.join(dpath, stem))
