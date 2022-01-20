import logging
import threading
from typing import Callable, Union

import requests
from fs import errors
from fs.errors import ResourceNotFound, DirectoryExists
from fs.onedrivefs import OneDriveFS
from fs.base import FS
from fs.path import dirname, basename
from fs.subfs import SubFS
from msgraphy import GraphApi
from msgraphy.auth.graph_auth import BasicAuth
from msgraphy.client.graph_client import GraphClient, RequestsGraphClient
from msgraphy.data.file import DriveItem

_log = logging.getLogger(__name__)


def _get_default_client(writeable: bool = False) -> GraphClient:
    return RequestsGraphClient(BasicAuth(scopes='Files.ReadWrite.All' if writeable else 'Files.Read.All'),
                               timeout=1, timeout_retry=3)


class MSGraphyClientSession:
    def __init__(self, client: GraphClient, drive_root: str):
        self._client = client
        self._drive_root = drive_root

    def path_url(self, path, extra):
        # the path must start with '/'
        if path in {'/', ''}:  # special handling for the root directory
            return f'{self._drive_root}/root{extra}'
        if extra != '':
            extra = ':' + extra
        return f'{self._drive_root}/root:{path}{extra}'

    def item_url(self, itemId, extra):
        return f'{self._drive_root}/items/{itemId}{extra}'

    def get_path(self, path, extra='', **kwargs):
        return self.get(self.path_url(path, extra), **kwargs)

    def post_path(self, path, extra='', **kwargs):
        return self.post(self.path_url(path, extra), **kwargs)

    def delete_path(self, path, extra='', **kwargs):
        return self.delete(self.path_url(path, extra), **kwargs)

    def get_item(self, path, extra='', **kwargs):
        return self.get(self.item_url(path, extra), **kwargs)

    def patch_item(self, path, extra='', **kwargs):
        return self.patch(self.item_url(path, extra), **kwargs)

    def post_item(self, path, extra='', **kwargs):
        return self.post(self.item_url(path, extra), **kwargs)

    def put_item(self, path, extra='', **kwargs):
        return self.put(self.item_url(path, extra), **kwargs)

    def delete_item(self, path, extra='', **kwargs):
        return self.delete(self.item_url(path, extra), **kwargs)

    def get(self, url, **kwargs):
        return self._client.make_request(url, method="GET", **kwargs).response

    def post(self, url, **kwargs):
        return self._client.make_request(url, method="POST", **kwargs).response

    def put(self, url, **kwargs):
        return self._client.make_request(url, method="PUT", **kwargs).response

    def patch(self, url, **kwargs):
        return self._client.make_request(url, method="PATCH", **kwargs).response

    def delete(self, url, **kwargs):
        return self._client.make_request(url, method="DELETE", **kwargs).response


class MSGraphyOneDriveFS(OneDriveFS):
    _client_factory = _get_default_client

    def __init__(self, root: Union[str, DriveItem], writeable=False, client=None):
        self._lock = threading.RLock()
        super(FS, self).__init__()
        if client is None:
            self.__client = self.get_client(writeable)
        else:
            self.__client = client

        api = GraphApi(self.__client)

        try:
            if isinstance(root, DriveItem):
                drive_item = root
            else:
                drive_item, filename = api.files.parse_file_path(root)
                assert filename == "/"
                drive_item = drive_item.value
        except Exception as e:
            raise errors.CreateFailed(f"Could not open {root}: {e}") from e

        self._drive_root = self._resource_root = drive_item.get_api_reference()
        self.session = MSGraphyClientSession(self.__client, self._resource_root)

        self._meta = {
            'case_insensitive': True,
            'invalid_path_chars': ':\0\\',
            'max_path_length': None,  # don't know what the limit is
            'max_sys_path_length': None,  # there's no syspath
            'network': True,
            'read_only': False,
            'supports_rename': False  # since we don't have a syspath...
        }

    @classmethod
    def set_client_factory(cls, factory: Callable[[bool], GraphClient]) -> None:
        cls._client_factory = factory

    @classmethod
    def get_client(cls, writeable: bool = False) -> GraphClient:
        return cls._client_factory(writeable)

    def makedir(self, path, permissions=None, recreate=False):
        _log.info(f'makedir({path}, {permissions}, {recreate})')
        path = self.validatepath(path)
        with self._lock:
            parentDir = dirname(path)
            # parentDir here is expected to have a leading slash
            assert parentDir[0] == '/'
            response = self.session.get_path(parentDir)
            if response.status_code == 404:
                raise ResourceNotFound(parentDir)
            response.raise_for_status()

            if recreate is False:
                response = self.session.get_path(path)
                if response.status_code != 404:
                    raise DirectoryExists(path)

            response = self.session.post_path(parentDir, '/children',
                                              json={'name': basename(path), 'folder': {},
                                                    '@microsoft.graph.conflictBehavior': 'replace'
                                                    })
            # TODO - will need to deal with these errors locally but don't know what they are yet
            response.raise_for_status()
            # don't need to close this filesystem so we return the non-closing version
            return SubFS(self, path)

    def copy(self, src_path, dst_path, overwrite=False, preserve_time=False):
        _log.info(f'copy({src_path}, {dst_path}, {overwrite}, {preserve_time})')
        src_path = self.validatepath(src_path)
        dst_path = self.validatepath(dst_path)
        with self._lock:
            if not overwrite and self.exists(dst_path):
                raise errors.DestinationExists(dst_path)

            driveItemResponse = self.session.get_path(src_path)
            if driveItemResponse.status_code == 404:
                raise ResourceNotFound(src_path)
            driveItemResponse.raise_for_status()
            driveItem = driveItemResponse.json()

            if 'folder' in driveItem:
                raise errors.FileExpected(src_path)

            newParentDir = dirname(dst_path)
            newFilename = basename(dst_path)

            parentDirResponse = self.session.get_path(newParentDir)
            if parentDirResponse.status_code == 404:
                raise ResourceNotFound(src_path)
            parentDirResponse.raise_for_status()
            parentDirItem = parentDirResponse.json()

            # This just asynchronously starts the copy
            response = self.session.post_item(driveItem['id'], '/copy?@microsoft.graph.conflictBehavior=replace', json={
                'parentReference': {'driveId': parentDirItem['parentReference']['driveId'], 'id': parentDirItem['id']},
                'name': newFilename,
            })
            response.raise_for_status()
            assert response.status_code == 202, 'Response code should be 202 (Accepted)'
            monitorUri = response.headers['Location']
            while True:
                # monitor uris don't require authentication
                # (https://docs.microsoft.com/en-us/onedrive/developer/rest-api/concepts/long-running-actions)
                jobStatusResponse = requests.get(monitorUri)
                jobStatusResponse.raise_for_status()
                jobStatus = jobStatusResponse.json()
                if 'operation' in jobStatus and jobStatus['operation'] != 'itemCopy':
                    _log.warning(f'Unexpected operation: {jobStatus["operation"]}')

                if jobStatus['status'] not in ['inProgress', 'completed', 'notStarted']:
                    _log.warning(f'Unexpected status: {jobStatus}')

                if jobStatus['status'] == 'completed':
                    break
