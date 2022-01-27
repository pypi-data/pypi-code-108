# -*- mode: python; coding: utf-8 -*-
# Copyright 2020 the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""
Azure Blob Storage I/O backend for the pipeline framework.

This module requires that the ``azure.storage.blob`` Python module be available.
If it is not, this module will still be importable, but it won't work. Check the
``ENABLED`` boolean variable or call :func:`assert_enabled` to raise an
exception offering guidance if the needed support is missing.

"""

__all__ = '''
AzureBlobPipelineIo
ENABLED
assert_enabled
'''.split()

import shutil

from . import PipelineIo

try:
    from azure.storage.blob import BlobServiceClient
    ENABLED = True
except ImportError:
    ENABLED = False


def assert_enabled():
    if not ENABLED:
        raise Exception('Azure pipeline I/O backend is needed but unavailable -'
            ' install the `azure-storage-blob` package')


class AzureBlobPipelineIo(PipelineIo):
    """I/O for pipeline processing that uses Microsoft Azure Blob Storage.

    Parameters
    ----------
    connection_string : str
      The Azure "connection string" to use
    container_name : str
      The name of the blob container within the storage account
    path_prefix : str or iterable of str
      A list folder names within the blob container that will be
      prepended to all paths accessed through this object.

    """
    _connection_string = None
    _svc_client = None
    _cnt_client = None
    _container_name = None
    _path_prefix = None

    def __init__(self, connection_string, container_name, path_prefix):
        assert_enabled()

        if isinstance(path_prefix, str):
            path_prefix = (path_prefix, )
        else:
            try:
                path_prefix = tuple(path_prefix)
                for item in path_prefix:
                    assert isinstance(item, str)
            except Exception:
                raise ValueError('path_prefix should be a string or iterable of strings; '
                                 'got %r' % (path_prefix, ))

        self._connection_string = connection_string
        self._container_name = container_name
        self._svc_client = BlobServiceClient.from_connection_string(connection_string)
        self._cnt_client = self._svc_client.get_container_client(container_name)
        self._path_prefix = path_prefix

    def _export_config(self):
        return {
            '_type': 'azure-blob',
            'connection_secret': self._connection_string,
            'container_name': self._container_name,
            'path_prefix': self._path_prefix,
        }

    @classmethod
    def _new_from_config(cls, config):
        return cls(
            config['connection_secret'],
            config['container_name'],
            config['path_prefix'],
        )

    def _make_blob_name(self, path_array):
        """TODO: is this actually correct? Escaping?"""
        return '/'.join(self._path_prefix + tuple(path_array))

    def check_exists(self, *path):
        from azure.core.exceptions import ResourceNotFoundError

        blob_client = self._cnt_client.get_blob_client(self._make_blob_name(path))

        try:
            blob_client.get_blob_properties()
        except ResourceNotFoundError:
            return False
        return True

    def get_item(self, *path, dest=None):
        blob_client = self._cnt_client.get_blob_client(self._make_blob_name(path))
        blob_client.download_blob().readinto(dest)

    def put_item(self, *path, source=None):
        blob_client = self._cnt_client.get_blob_client(self._make_blob_name(path))
        blob_client.upload_blob(source)

    def list_items(self, *path):
        from azure.storage.blob.models import BlobPrefix
        prefix = self._make_blob_name(path) + '/'

        for item in self._cnt_client.list_blobs(
                prefix = prefix,
                delimiter = '/'
        ):
            assert item.name.startswith(prefix)
            stem = item.name[len(prefix):]
            is_folder = isinstance(item, BlobPrefix)

            if is_folder:
                # Returned names end with a '/' too
                assert stem[-1] == '/'
                stem = stem[:-1]

            yield stem, is_folder
