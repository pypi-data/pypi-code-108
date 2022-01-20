#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#

import io
import json
import os
import re
import shutil
import tempfile
import time
from datetime import datetime
from os.path import exists
from typing import Dict, List, Optional, Union, Any, Iterator
from pathlib import Path
from abc import abstractmethod

import requests
from diskcache import Cache

from ..constants import (AUXILIARY_KEY, TIMESTAMP_FIELD, AssetsConstants,
                         JobConstants, AggregationsByField)
from ..custom_exceptions import (IdentityError, AssetError,
                                 InvalidAuthorization, JobError,
                                 MetadataNotFoundError)
from ..models.object_access import ObjectAccess
from ..tools import misc
from ..tools.connections import KVStoreTemplate
from ..tools.logger import get_logger
from ..tools.misc import parse_file_path, retry, tqdm
from ..tools.naming import standardize_name
from ..tools.time_utils import jsonify_metadata
from ..tools.misc import run_threaded, join

DEFAULT_SEARCH_SIZE = 50
DEFAULT_PAGINATION = 5000
PAUSE_TIME = 0.05

logger = get_logger(__name__)

VERSION_PATTERN = re.compile(r'/v\d+')
temp_dir = Path(tempfile.TemporaryDirectory().name).parent
DEFAULT_CACHE_DIR = os.getenv('CACHE_DIR', temp_dir)
DEFAULT_CACHE_SIZE = os.getenv("CACHE_MAX_SIZE", 50)
DEFAULT_CACHE_SUB_DIR = "default"
DEFAULT_ORGANIZATION_SUB_DIR = 'default'


class AssetManagerClientTemplate(object):
    """File cache for assets fetched via the AssetManagerClient.

    Using the least-frequently-used eviction policy, the cache will fill
    until the size_limit_gb is reached and will begin eviction
    """

    def __init__(
            self,
            asset_type: str,
            metadata_only: bool,
            cache_size_gb: int = None,
            disabled: bool = False,
            identity: Optional[dict] = None
    ):

        if not cache_size_gb:
            cache_size_gb = DEFAULT_CACHE_SIZE

        self.asset_type = asset_type
        self.metadata_only = metadata_only
        self.cache_disabled = disabled
        self.cache_size_gb = int(cache_size_gb)

        # Initialized in the _set_cache method
        self.cache_location = None
        self.cache = None
        self._set_cache(asset_type=asset_type, identity=identity)

    @abstractmethod
    def get_metadata(self, id: str, retry: bool = False) -> dict:
        pass

    @abstractmethod
    def get_url(self, id: str) -> str:
        pass

    @abstractmethod
    def get_bytes(self, id: str) -> bytes:
        pass

    def _get_cache_location(
            self,
            asset_type: Optional[str] = None,
            identity: Optional[dict] = None):
        # When not provided, defaults to <DEFAULT_CACHE_DIR,asset_type>.
        # If asset_type is None (for example, when initializing SceneEngineClient),
        # then defaults to a default sub directory.
        if asset_type:
            cache_location = os.path.join(DEFAULT_CACHE_DIR, asset_type)
        else:
            cache_location = os.path.join(
                DEFAULT_CACHE_DIR, DEFAULT_CACHE_SUB_DIR)

        organization = self._get_sanitized_organization_name(identity)
        cache_location = os.path.join(cache_location, organization)
        self.cache_location = cache_location
        return cache_location

    def _get_sanitized_organization_name(
            self,
            identity: Optional[dict] = None,
            replace_char: str = '_'):
        # Sanitize the organization name
        if identity:
            organization = identity.get('organization', '')
        else:
            organization = DEFAULT_ORGANIZATION_SUB_DIR
        organization = organization.lower()
        for symbol in [' ', '/', '\'', '\"', '(', ')']:
            organization = organization.replace(symbol, replace_char)
        return organization

    def _set_cache(
            self,
            asset_type: Optional[str] = None,
            identity: Optional[dict] = None) -> None:
        """Set the cache location.

        Args:
            asset_type (str): Asset type
            identity (dict): User identity dict
        """
        try:
            self.cache_location = self._get_cache_location(
                asset_type=asset_type, identity=identity)
            os.makedirs(self.cache_location, exist_ok=True)
        except Exception as e:
            logger.info(
                " cache_location ::: could not create {} because of {}, instead {} is created".format(
                    self.cache_location, e, temp_dir))
            self.cache_location = temp_dir
            os.makedirs(self.cache_location, exist_ok=True)

    def get_file_from_cache(self, key):
        if self.cache_disabled:
            return
        # Read a file as a File object
        with Cache(
                directory=self.cache_location,
                eviction_policy='least-frequently-used',
                size_limit=self.cache_size_gb * (2 ** 30)
        ) as ref:
            return ref.get(key, read=True)

    def put_file_into_cache(self, key, value):
        if self.cache_disabled:
            return
        # Put a file as a File object
        with Cache(
                directory=self.cache_location,
                eviction_policy='least-frequently-used',
                size_limit=self.cache_size_gb * (2 ** 30)
        ) as ref:
            return ref.set(key, value, read=True)

    def get_bytes_from_cache(self, key):
        if self.cache_disabled:
            return
        # Read a file as a bytes array
        with Cache(
                directory=self.cache_location,
                eviction_policy='least-frequently-used',
                size_limit=self.cache_size_gb * (2 ** 30)
        ) as ref:
            return ref.get(key, read=False)

    def put_bytes_into_cache(self, key, value):
        if self.cache_disabled:
            return
        with Cache(
                directory=self.cache_location,
                eviction_policy='least-frequently-used',
                size_limit=self.cache_size_gb * (2 ** 30)
        ) as ref:
            return ref.set(key, value, read=False)


class Asset(object):
    def __init__(self,
                 id: str,
                 asset_manager_client: AssetManagerClientTemplate
                 ):
        self.id = id
        self.asset_manager_client = asset_manager_client
        self.asset_type = asset_manager_client.asset_type
        self.metadata_only = asset_manager_client.metadata_only

    def __check_metadata_only(self):
        if self.metadata_only:
            raise AssetError("{} {} is metadata only".format(self.asset_type, self.id))

    @property
    def metadata(self) -> Dict:
        return self.asset_manager_client.get_metadata(id=self.id)

    @property
    def url(self) -> str:
        self.__check_metadata_only()
        return self.asset_manager_client.get_url(id=self.id)

    @property
    def bytes(self) -> bytes:
        self.__check_metadata_only()
        return self.asset_manager_client.get_bytes(id=self.id)

    def download_as(self, filepath):
        with open(filepath, 'wb') as file:
            file.write(self.bytes)


class AssetManagerClient(AssetManagerClientTemplate):
    def __init__(
            self,
            asset_type: str = AssetsConstants.SESSIONS_ASSET_ID,  # default asset is session
            asset_manager_url: Optional[str] = None,
            metadata_only: bool = False,
            auth_token: Optional[str] = None,
            cache_disabled: bool = False,
            is_non_standard_asset: bool = False,
            kv_store: Optional[KVStoreTemplate] = None
    ):
        """Asset manager client for fetching/putting assets and metadata.

        :param asset_type: (str) The type of asset
        :param asset_manager_url: (str) The URL of the asset manager
        :param metadata_only: (bool) Whether to only return metadata
        :param auth_token: (str) Authentication token of the user -- must be provided
        :param cache_disabled: (bool): Disable caching; defaults to False
        :param is_non_standard_asset (bool): Whether the asset is a non-standard asset.
               If True, ignore asset-type checks.
        :param kv_store: key-value store to cache bytes, default to None.
        """

        if is_non_standard_asset is False and asset_type not in AssetsConstants.VALID_ASSETS:
            raise ValueError('Invalid asset_type `{}`'.format(asset_type))

        # Override enabled cache with env variable
        if misc.as_bool(os.environ.get("DISABLE_CACHING", False)):
            cache_disabled = True

        self.is_non_standard_asset = is_non_standard_asset

        if asset_manager_url is None:
            raise AssetError('asset_manager_url must be provided')
        self.asset_manager_url = asset_manager_url
        self.jobs_namespace_url = join(asset_manager_url, "jobs")
        self.assets_namespace_url = join(asset_manager_url, "assets")

        self.auth_token = auth_token
        if self.auth_token:
            self.identity = self._get_identity()
        else:
            self.identity = None

        if kv_store:
            self.kv_store = kv_store
        else:
            self.kv_store = None

        super().__init__(
            asset_type=asset_type,
            metadata_only=metadata_only,
            cache_size_gb=DEFAULT_CACHE_SIZE,
            disabled=cache_disabled,
            identity=self.identity
        )

        self._set_asset_state(
            asset_type=asset_type,
            metadata_only=metadata_only)

    def _get_root_url(self):
        # Strip version from asset manager URL
        version_match = re.search(VERSION_PATTERN, self.asset_manager_url)
        if version_match:
            version = version_match.group()
            root_url = self.asset_manager_url.split(version)[0]
        else:
            root_url = self.asset_manager_url
        return root_url

    def _get_identity(
            self,
            wait_for_connection: bool = True,
            max_wait_time: int = 60):
        env_user_identity = os.getenv('SCENEBOX_USER_IDENTITY')
        if env_user_identity:
            # TODO: This is a temporary fix and should be improved
            return json.loads(env_user_identity)
        else:
            if self.auth_token is None:
                raise IdentityError(
                    'Cannot get identity when no auth has been provided')
            params = {}
            if self.auth_token:
                params['token'] = self.auth_token

            root_url = self._get_root_url()

            wait_time = 0
            sleep_time = 5
            while True:
                try:
                    resp = requests.get(
                        join(
                            root_url,
                            'auth'),
                        params=params)
                    break
                except requests.exceptions.ConnectionError as e:
                    if not wait_for_connection or wait_time > max_wait_time:
                        raise e
                    else:
                        logger.warning(
                            "could not connect to {}, retrying in {} seconds".format(
                                root_url, sleep_time))
                        time.sleep(sleep_time)
                        wait_time = wait_time + sleep_time
            if not resp.ok:
                raise IdentityError(
                    "Could not obtain the user identity {}", resp.content)
            return resp.json()

    def _set_asset_state(
            self,
            asset_type: str,
            metadata_only: bool
    ):
        if asset_type not in AssetsConstants.VALID_ASSETS:
            raise AssetError(
                "The asset type {} is invalid. Valid types are: {}".format(
                    asset_type, AssetsConstants.VALID_ASSETS))

        if not isinstance(metadata_only, bool):
            raise ValueError("metadata_only must be a boolean")

        self.asset_type = asset_type

        if asset_type in AssetsConstants.METADATA_ONLY_ASSETS:
            self.metadata_only = True
        else:
            self.metadata_only = metadata_only

        if metadata_only is False:
            self._set_cache(asset_type=asset_type, identity=self.identity)
        return self

    def add_asset_manager_params(
            self, params_dict: Optional[dict] = None) -> dict:

        if self.auth_token is None:
            raise InvalidAuthorization(
                "No authorization is provided in AssetManagerClient")

        params_dict = params_dict or {}
        params_dict['asset_type'] = self.asset_type
        params_dict['metadata_only'] = self.metadata_only
        if self.auth_token:
            params_dict['token'] = self.auth_token
        return params_dict

    def with_auth(self,
                  auth_token: Optional[str] = None,
                  ):
        if auth_token:
            self.auth_token = auth_token

        self.identity = self._get_identity()
        self._set_cache(asset_type=self.asset_type, identity=self.identity)
        return self

    def register_field(self, field_dict: dict):
        url = self.get_assets_url('register_field/')
        params = self.add_asset_manager_params({})
        resp = requests.post(
            url,
            json=field_dict,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not register the field ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def delete(
            self,
            id: str,
            wait_for_deletion: bool = True) -> dict:
        """Delete an asset.

        Parameters
        ----------
        id:
            The ID of the asset to delete.
        wait_for_deletion:
            If True, polls until the specified asset no longer exists.
            Otherwise, returns immediately (even if the asset is still in the process
            of being deleted).

        """

        id = self._check_identifier(id)
        url = self.get_assets_url(id)
        params = self.add_asset_manager_params({})
        resp = requests.delete(url, params=params)

        if not resp.ok:
            raise AssetError(
                'Could not delete the file ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))

        if wait_for_deletion:
            self._wait_for_non_existence(id)

        return resp.json()

    def put_directory(self,
                      directory_path: str,
                      metadata: dict,
                      temp_dir=temp_dir) -> str:
        """Convert a directory to a zipfile and upload."""
        if not os.path.exists(directory_path):
            raise IOError('Path does not exist')

        with tempfile.NamedTemporaryFile(dir=temp_dir) as f:
            zip_ext = 'zip'
            temp_zipfile_path = f.name
            shutil.make_archive(temp_zipfile_path, zip_ext, directory_path)

            return self.put_asset(
                file_path=temp_zipfile_path,
                metadata=metadata,
                id="{}.{}".format(temp_zipfile_path, zip_ext),
                wait_for_completion=True)

    def put_file(
            self,
            file_object: Union[io.BytesIO, bytes, str],
            id: Optional[str] = None,
            corr_asset_id: Optional[str] = None,
            corr_asset_type: Optional[str] = None,
            content_type: Optional[str] = None,
            content_size: Optional[int] = None,
            add_to_redis_cache: bool = False,
            wait_for_completion=False) -> str:
        """ Register and upload a file with the asset manager
        Args:
            file (BytesIO or bytes): bytes object
            id (str): the uid of the file. If not provided, will be set automatically
            corr_asset_id: this is only used when we are creating an additional file for an asset that already
                           exists (say creating thumbnails for an existing image/video). This is only used for
                           getting the file owner
            corr_asset_type: this is only used when we are creating an additional file for an asset that already
                           exists (say creating thumbnails for an existing image/video). This is only used for
                           getting the file owner
            wait_for_completion (bool): Whether to wait for the upload to finish before returning
        :return: id of the file
        """
        large_size_bytes = 50 * 1024 * 1024 #50 mb
        id = id or misc.get_guid()

        # process_multipart = False

        if content_size:
            file_size = content_size
        else:
            try:
                file_size = os.fstat(file_object.fileno()).st_size
            except:
                file_size = 0

        # single part upload
        if file_size < large_size_bytes:

            if isinstance(file_object, (io.BytesIO, io.IOBase)):
                file_object.seek(0)
                file = file_object.read()
            elif isinstance(file_object, str):
                file = file_object.encode("utf-8")
            else:
                file = file_object

            upload_params = self.get_temporary_upload_url(
                ids=[id],
                corr_asset_id=corr_asset_id,
                corr_asset_type=corr_asset_type,
                content_type=content_type
            )
            upload_url = upload_params[id]["url"]
            files = upload_params[id]["fields"]
            files["file"] = file

            resp = requests.post(upload_url, files=files)
            if not resp.ok:
                raise AssetError(
                    'Could not put the file ::: {} -- {} -- {}'.format(
                        self.asset_type, resp.reason, resp.content))
            if add_to_redis_cache:
                self.put_bytes_into_kv_store(id=id, data_bytes=file_object)

        # multipart upload
        else:
            if not isinstance(file_object, (io.BytesIO, io.IOBase)):
                raise NotImplementedError("type should be Bytes or IOBase")
            params = self.add_asset_manager_params()
            body_complete_multipart = {"id": id}

            if corr_asset_id:
                body_complete_multipart["corr_asset_id"] = corr_asset_id

            if corr_asset_type:
                body_complete_multipart["corr_asset_type"] = corr_asset_type

            resp = requests.post(
                self.get_assets_url('multipart_upload_id/'),
                json=body_complete_multipart,
                params=params)
            if not resp.ok:
                raise AssetError("could not get multipart upload id")
            upload_id = resp.json()["upload_id"]

            parts = []
            part_no = 1

            file_object.seek(0)
            pbar = tqdm(total=int(file_size/(1024 * 1024)), desc="uploading {} id:{} of size {:6.2f} MB".format(
                self.asset_type,
                id,
                file_size/(1024 * 1024)
            ))
            while True:
                file_data = file_object.read(large_size_bytes)
                if not file_data:
                    break

                body_complete_multipart = {"id": id, "part_no": part_no, "upload_id": upload_id}
                if corr_asset_id:
                    body_complete_multipart["corr_asset_id"] = corr_asset_id

                if corr_asset_type:
                    body_complete_multipart["corr_asset_type"] = corr_asset_type

                resp = requests.post(
                    self.get_assets_url('multipart_temporary_upload_url/'),
                    json=body_complete_multipart,
                    params=params)
                if not resp.ok:
                    raise AssetError("could not get multipart upload url")
                signed_url = resp.json()["url"]

                res = requests.put(signed_url, data=file_data)
                etag = res.headers['ETag']
                parts.append({'ETag': etag, 'PartNumber': part_no})
                part_no += 1
                pbar.update(int(large_size_bytes/(1024 * 1024)))
            pbar.close()

            body_complete_multipart = {"id": id, "parts": parts, "upload_id": upload_id}
            if corr_asset_id:
                body_complete_multipart["corr_asset_id"] = corr_asset_id

            if corr_asset_type:
                body_complete_multipart["corr_asset_type"] = corr_asset_type

            resp = requests.post(
                self.get_assets_url('multipart_complete/'),
                json=body_complete_multipart,
                params=params)
            if not resp.ok:
                raise AssetError("could not get multipart upload url")

            file_object.close()

        return id

    def get_url(self,
                id: str) -> str:
        """Get the public URL of an asset.

        Parameters
        ----------
        id:
            The ID of the asset to get the URL of.

        Returns
        -------
        str
            The URL of the specified asset.
        """
        id = self._check_identifier(id)
        url = self.get_assets_url(id)
        params = self.add_asset_manager_params({"return_url": True})
        resp = requests.get(url, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not get the file ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()['url']

    @staticmethod
    def get_key_with_prefix(prefix: str, asset_id: str):
        return "{}_{}".format(prefix, asset_id)

    def put_bytes_into_kv_store(self, id: str, data_bytes: bytes):
        if self.kv_store:
            try:
                self.kv_store.put_bytes(key=self.get_key_with_prefix(prefix=self.asset_type, asset_id=id), value=data_bytes)
            except Exception as e:
                logger.warning("{}".format(e))

    def get_bytes_from_kv_store(self, id: str) -> Optional[bytes]:
        """Get the data bytes from kv_store if available.
        Parameters
        ----------
        id:
            The ID of the asset to get the bytes of.
        """
        if self.kv_store:
            return self.kv_store.get_bytes(key=self.get_key_with_prefix(prefix=self.asset_type, asset_id=id))
        else:
            return None

    def get_bytes(self,
                  id: str) -> bytes:
        """Get the data bytes of an asset.

        Parameters
        ----------
        id:
            The ID of the asset to get the bytes of.

        Returns
        -------
        bytes
            The data bytes of the specified asset.
        """
        id = self._check_identifier(id)

        # Check if the response object exists in kv_store
        data_bytes = self.get_bytes_from_kv_store(id)

        # Check if the response object exists locally in the cache
        if not data_bytes:
            data_bytes = self.get_bytes_from_cache(id)

        if not data_bytes:
            self._check_storage()
            url = self.get_assets_url(id)
            params = self.add_asset_manager_params({"return_url": False})
            resp = requests.get(url, params=params)
            if not resp.ok:
                raise AssetError(
                    'Could not get asset {} with id {}. Reason: {}: Content: {}'.format(
                        self.asset_type, id, resp.reason, resp.content))
            data_bytes = resp.content
            self.put_bytes_into_kv_store(id, data_bytes)
            self.put_bytes_into_cache(id, data_bytes)

        return data_bytes

    def get_bytes_in_batch(self,
                           ids: List[str]) -> Dict[str, bytes]:
        """Get the data bytes for a list of assets.

        Parameters
        ----------
        ids:
            The IDs of the assets to get the data bytes of.

        Returns
        -------
        dict[str, str]:
            The URLs of the specified assets.  Keys are the inputted ``ids``.  Values are the corresponding data bytes.

        """

        data_id_bytes_map = {}

        def threaded_get_bytes_and_append(id: str):
            data_id_bytes_map[id] = self.get_bytes(id)

        run_threaded(func=threaded_get_bytes_and_append,
                     iterable=ids,
                     desc="get bytes")

        return data_id_bytes_map

    def get_url_in_batch(self,
                         ids: List[str]) -> Dict[str, str]:
        """Get the public URLs of a list of assets.

        Parameters
        ----------
        ids:
            The IDs of the assets to get the URLs of.

        Returns
        -------
        dict[str, str]:
            The URLs of the specified assets.  Keys are the inputted ``ids``.  Values are the corresponding URLs.

        """

        _ids = [self._check_identifier(_id) for _id in ids]

        assets_meta = self.search_meta_large(query={
            "filters": [
                {
                    "field": "id",
                    "values": _ids
                }
            ]
        })

        if len(assets_meta) != len(ids):
            existing_ids = [asset_meta.get("id") for asset_meta in assets_meta]
            logger.warning("{} assets do not exist with ids ::: {}".format(len(ids) - len(ids),
                                                                           set(ids).difference(set(existing_ids))))
        object_accesses = []
        ids_from_meta = []
        ids_from_meta_with_no_object_access = []

        for asset_meta in assets_meta:
            if asset_meta.get("object_access"):
                object_accesses.append(asset_meta["object_access"])
                ids_from_meta.append(asset_meta["id"])
            else:
                ids_from_meta_with_no_object_access.append(asset_meta["id"])

        if ids_from_meta_with_no_object_access:
            logger.warning("{} assets do not have object access with ids ::: {}".format(len(ids_from_meta_with_no_object_access),
                                                                           ids_from_meta_with_no_object_access))
        body = {
            "object_accesses": object_accesses,
            "ids": ids_from_meta
        }

        params = self.add_asset_manager_params()

        resp = requests.post(
            self.get_assets_url('url_from_object_access_in_batch/'),
            json=body,
            params=params
        )
        if not resp.ok:
            raise AssetError('Could not get urls for {}::: {} -- {} -- {}'.format(
                _ids, self.asset_type, resp.reason, resp.content))

        return resp.json()

    def get_file_and_write(self,
                           id: str,
                           write_filepath: Optional[str] = None) -> str:

        bytesio_data = io.BytesIO(self.get_bytes(id=id))
        if not write_filepath:
            write_filepath = tempfile.NamedTemporaryFile(delete=False).name
        with open(write_filepath, 'wb') as fout:
            fout.write(bytesio_data.read())

        return write_filepath

    def exists(self,
               id: str) -> bool:
        """Check if an asset exists.

        Parameters
        ----------
        id:
            The ID of the asset to check the existence of.

        Returns
        -------
        bool
            Returns True if the named asset exists.  Otherwise, returns False.
        """
        id = self._check_identifier(id)
        url = self.get_assets_url('exists/{}'.format(id))
        params = self.add_asset_manager_params()
        resp = requests.get(url, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not find the identifier ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return misc.as_bool(resp.json())


    def exists_multiple(self,
                        ids: List[str]) -> List[bool]:
        """Check if an asset exists.

        Parameters
        ----------
        ids:
            List of the IDs of assets to check the existence of.

        Returns
        -------
        bool
            Returns True if the named assets exist.  Otherwise, returns False.
        """

        ids = [self._check_identifier(id) for id in ids]
        metadata =  self.get_metadata_in_batch(ids=ids)
        metadata_keys = metadata.keys()

        return [id in metadata_keys for id in ids]


    def copy(self,
             id: str,
             new_id: str):
        """Copy an asset.

        Parameters
        ----------
        id:
            The ID of the asset to copy.
        new_id:
            The ID to give to the created asset copy.
        """
        id = self._check_identifier(id)
        url = self.get_assets_url('copy/{}'.format(id))
        params = self.add_asset_manager_params({"new_id": new_id})
        resp = requests.put(url, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not copy the identifier {} to {} ::: {} -- {} -- {}'.format(
                    id, new_id, self.asset_type, resp.reason, resp.content))
        return resp.json()

    def count(self, search: Optional[dict] = None) -> int:
        """Count the number of assets satisfying a query.

        Parameters
        ----------
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.

        Returns
        -------
        int
            The number of assets that fulfil ``search``.
        """
        url = self.get_assets_url('count/')
        params = self.add_asset_manager_params()
        search = search or {}
        resp = requests.post(
            url,
            json=search,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not count the files::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def _aggregate_by_field(self, aggregation: str, field_name: str, search: Optional[dict] = None) -> float:
        '''
        Args:
            aggregation: aggregation function
            field_name: the field to do aggregation over it
            search: search criteria for the assets

        Returns: aggregation result

        '''
        if aggregation not in AggregationsByField.SUPPORTED:
            raise ValueError(
                "{} aggregation is not supported".format(aggregation))

        if not field_name:
            raise ValueError(
                "field_name must be provided, {} is given".format(field_name))
        url = self.get_assets_url('{}/'.format(aggregation))
        params = self.add_asset_manager_params()
        search = search or {}
        aggregation_request = {
            'search': search,
            'field_name': field_name
        }
        resp = requests.post(
            url,
            json=aggregation_request,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not obtain {} aggregation for field {} ::: {} -- {} -- {}'.format(
                    aggregation, field_name, self.asset_type, resp.reason, resp.content))
        return resp.json()

    def sum(self, field_name: str, search: Optional[dict] = None) -> float:
        """Sum a specified field over assets that satisfy a query.

        Find the aggregate sum of ``field_name`` over all the assets specified by ``search``.

        Parameters
        ----------
        field_name:
            The field name in the filtered assets' metadata of which to sum over.
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.

        Returns
        -------
        float
            The aggregate sum of the specified field name over the filtered assets.
       """
        return self._aggregate_by_field(aggregation=AggregationsByField.SUM, field_name=field_name, search=search)

    def average(self, field_name: str, search: Optional[dict] = None) -> float:
        """Average a specified field over assets that satisfy a query.

        Find the aggregate average of ``field_name`` over all the assets specified by ``search``.

        Parameters
        ----------
        field_name:
            The field name in the filtered assets' metadata of which to average over.
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.

        Returns
        -------
        float
            The aggregate average of the specified field name over the filtered assets.
       """
        '''
        Args:
            field_name: the field to do average over it
            search: search criteria for the assets

        Returns: average

        '''
        return self._aggregate_by_field(aggregation=AggregationsByField.AVERAGE, field_name=field_name, search=search)

    def cardinality(self, field_name: str, string_field: bool=True, search: Optional[dict] = None) -> float:
        '''
        Args:
            field_name: the field to do average over it
            search: search criteria for the assets

        Returns: Count of distinct values

        '''
        if string_field:
            field_name += ".keyword"
        return self._aggregate_by_field(aggregation=AggregationsByField.CARDINALITY, field_name=field_name, search=search)

    @retry(Exception, logger=logger)
    def get_metadata(self, id: str, retry: bool = False) -> dict:
        """Fetch an asset's metadata.

        Parameters
        ----------
        id:
            The ID of the asset to receive the metadata of.
        retry:
            If True, retries the call for total_tries set in retry decorator

        Returns
        -------
        dict
            The metadata of the specified asset.
        """
        id = self._check_identifier(id)
        url = self.get_assets_url('meta/{}'.format(id))
        params = self.add_asset_manager_params()
        resp = requests.get(url, params=params)
        if not resp.ok:
            raise MetadataNotFoundError(
                'Could not get the metadata from the identifier ::: {} -- {} -- {} -- {}'.format(
                    id, self.asset_type, resp.reason, resp.content))
        return resp.json()

    @retry(Exception, logger=logger)
    def get_metadata_in_batch(self,
                              ids: List[str]) -> Dict[str, Optional[dict]]:
        """Fetch an asset's metadata.

        Parameters
        ----------
        ids:
            The IDs of the asset to receive the metadata of.

        Returns
        -------
        Dict: str->dict or None
            The metadata of the specified asset-set to None if not found.
        """

        _ids = [self._check_identifier(_id) for _id in ids]

        assets_meta = self.search_meta_large(query={
            "filters": [
                {
                    "field": "id",
                    "values": _ids
                }
            ]
        })

        assets_meta_dict = {}
        existing_ids = set()
        for asset_meta in assets_meta:
            existing_id = asset_meta.get("id")
            assets_meta_dict[existing_id] = asset_meta
            existing_ids.add(existing_id)

        if len(existing_ids) != len(_ids):
            extra_ids = set(_ids).difference(existing_ids)
            logger.warning("{} assets do not exist with ids ::: {}".format(len(extra_ids), extra_ids))
            for extra_id in extra_ids:
                assets_meta_dict[extra_id] = None

        return assets_meta_dict


    @retry(Exception, logger=logger)
    def put_asset(self,
                  metadata: dict,
                  file_path: Optional[str] = None,
                  filename: Optional[str] = None,
                  file_object: Optional[Union[io.BytesIO, bytes, str]] = None,
                  url: Optional[str] = None,
                  id: Optional[str] = None,
                  uri: Optional[str] = None,
                  geo_field: Optional[str] = None,
                  shape_group_field: Optional[str] = None,
                  buffered_write: bool = False,
                  wait_for_completion: bool = True,
                  content_type: Optional[str] = None,
                  add_to_redis_cache: bool = False,
                  retry: bool = False) -> str:

        # metadata should be always provided
        # either of the following should be provided if the asset is not metadata only
        # url
        # file_path
        # file_object and filename

        id = id or metadata.get("id") or misc.get_guid()
        metadata["id"] = id

        if not metadata.get(TIMESTAMP_FIELD):
            metadata[TIMESTAMP_FIELD] = datetime.utcnow()

        if self.asset_type in AssetsConstants.METADATA_ONLY_ASSETS:
            if any([filename, file_path, url, file_path, uri]):
                raise AssetError(
                    "asset {} does not accept file, filename, file_path, uri or, url".format(
                        self.asset_type))
        else:
            if not any([file_object, url, file_path, uri]) and self.asset_type != AssetsConstants.ANNOTATIONS_ASSET_ID:
                raise AssetError(
                    "file_object, url, file_path is required for asset {}".format(
                        self.asset_type))
            object_access = None
            if url:
                object_access = ObjectAccess(url=url,
                                             id=id,
                                             filename=filename)
                if uri:
                    raise AssetError(
                        "url {} cannot support uri".format(url))
            elif uri:
                object_access = ObjectAccess(uri=uri,
                                             id=id,
                                             filename=filename)
                if url:
                    raise AssetError(
                        "uri {} cannot support url".format(uri))
            elif file_path or file_object:
                if file_path:
                    if not exists(file_path):
                        raise AssetError(
                            "file_path {} does not exist".format(file_path))
                    filename, _, _, _ = parse_file_path(file_path)
                    file_object = open(file_path, 'rb')
                else:
                    filename = filename or id

                self.put_file(file_object=file_object,
                              id=id,
                              content_type=content_type,
                              content_size=metadata.get("num_bytes", 0),
                              add_to_redis_cache=add_to_redis_cache
                              )

                object_access = ObjectAccess(id=id, filename=filename)
            if object_access:
                metadata["object_access"] = object_access.to_dic()

        metadata_json = jsonify_metadata(metadata)

        params = {
            "replace": True,
            "geo_field": geo_field,
            "shape_group_field": shape_group_field,
            "buffered_write": buffered_write,
            "replace_sets": False}
        params = self.add_asset_manager_params(params)
        resp = requests.put(
            url=self.get_assets_url("meta/{}".format(id)),
            json=metadata_json,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not put the metadata for the identifier ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))

        if wait_for_completion:
            self._wait_for_existence(id)
        return id

    @retry(Exception, logger=logger, initial_wait=1.5, total_tries=10)
    def put_assets_batch(self,
                  metadata: List[dict],
                  file_paths: Optional[List[str]] = None,
                  filenames: Optional[List[str]] = None,
                  file_objects: Optional[List[Union[io.BytesIO, bytes, str]]] = None,
                  urls: Optional[List[str]] = None,
                  ids: Optional[List[str]] = None,
                  uris: Optional[List[str]] = None,
                  geo_field: Optional[str] = None,
                  shape_group_field: Optional[str] = None,
                  wait_for_completion: bool = True,
                  content_type: Optional[str] = None,
                  threading: bool = True,
                  disable_tqdm: bool = True,
                  add_to_redis_cache: bool = False,
                  retry: bool = False) -> List[str]:

        # metadata should be always provided
        # either of the following should be provided if the asset is not metadata only
        # url
        # file_path
        # file_object and filename

        key_json_meta_map = {}
        key_id_map = {}
        def threaded_file_writer(iterable):
            key, id, metadatum, filename, file_path, file_object, url, uri = iterable

            id = id or metadatum.get("id") or misc.get_guid()
            metadatum["id"] = id

            if not metadatum.get(TIMESTAMP_FIELD):
                metadatum[TIMESTAMP_FIELD] = datetime.utcnow()

            if self.asset_type in AssetsConstants.METADATA_ONLY_ASSETS:
                if any([filename, file_path, url, file_object, uri]):
                    raise AssetError(
                        "asset {} does not accept file, filename, file_path, uri or, url".format(
                            self.asset_type))
            else:
                if not any([file_object, url, file_path, uri]) and self.asset_type != AssetsConstants.ANNOTATIONS_ASSET_ID:
                    raise AssetError(
                        "file_object, url, file_path is required for asset {}".format(
                            self.asset_type))
                object_access = None
                if url:
                    object_access = ObjectAccess(url=url,
                                                 id=id,
                                                 filename=filename)
                    if uri:
                        raise AssetError(
                            "url {} cannot support uri".format(url))
                elif uri:
                    object_access = ObjectAccess(uri=uri,
                                                 id=id,
                                                 filename=filename)
                    if url:
                        raise AssetError(
                            "uri {} cannot support url".format(uri))
                elif file_path or file_object:
                    if file_path:
                        if not exists(file_path):
                            raise AssetError(
                                "file_path {} does not exist".format(file_path))
                        filename, _, _, _ = parse_file_path(file_path)
                        file_object = open(file_path, 'rb')
                    else:
                        filename = filename or id

                    self.put_file(file_object=file_object,
                                  id=id,
                                  content_type=content_type,
                                  content_size=metadatum.get("num_bytes", 0),
                                  add_to_redis_cache=add_to_redis_cache)

                    object_access = ObjectAccess(id=id, filename=filename)
                if object_access:
                    metadatum["object_access"] = object_access.to_dic()

            metadatum_json = jsonify_metadata(metadatum)
            key_json_meta_map[key] = metadatum_json
            key_id_map[key] = id

        # Formatting inputs to a list to run threaded
        if ids is None:
            ids = [None] * len(metadata)
        if filenames is None:
            filenames = [None] * len(metadata)
        if file_paths is None:
            file_paths = [None] * len(metadata)
        if file_objects is None:
            file_objects = [None] * len(metadata)
        if urls is None:
            urls = [None] * len(metadata)
        if uris is None:
            uris = [None] * len(metadata)

        keys = list(range(len(metadata)))
        # logger.debug("Writing {} files to disk.".format(len(metadata)))
        run_threaded(func=threaded_file_writer,
                     iterable=zip(keys, ids, metadata, filenames, file_paths,
                                  file_objects, urls, uris),
                     desc="adding annotations",
                     disable_threading=not threading,
                     disable_tqdm=disable_tqdm)

        json_metadata_list = []
        ids_list = []
        for key in keys:
            json_metadata_list.append(key_json_meta_map[key])
            ids_list.append(key_id_map[key])

        # Rename to avoid confusion
        ids = ids_list
        body = {"ids": ids, "metadata": json_metadata_list}

        params = {
            "replace": True,
            "geo_field": geo_field,
            "shape_group_field": shape_group_field,
            "replace_sets": False}

        params = self.add_asset_manager_params(params)

        # logger.debug("Putting {} metadata in one batch.".format(len(json_metadata_list)))
        resp = requests.post(
            self.get_assets_url('meta_batch/'),
            json=body,
            params=params)

        if not resp.ok:
            raise AssetError(
                'Could not put the metadata for the identifier ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))

        if wait_for_completion:
            self._wait_for_existence(ids=ids)

        return ids


    @retry(Exception, logger=logger)
    def update_metadata(
            self,
            id: str,
            metadata: dict,
            buffered_write: bool = False,
            replace_sets: bool = False,
            geo_field: Optional[str] = None,
            shape_group_field: Optional[str] = None,
            retry: bool = False) -> dict:
        """Update an asset's metadata.

        Parameters
        ----------
        id:
            The ID of the asset to update the metadata of.
        metadata:
            The metadata to update the existing metadata with.
        buffered_write:
            If True, ingests the metadata in a buffered fashion.
        replace_sets:
            If True, replaces existing metadata with ``metadata``.  Otherwise, attempts to append ``metadata`` to the
            existing metadata.
        geo_field:
            Geolocation field
        shape_group_field:
            Shape group field (example: UMAP)
        retry:
            If True, retries the call for total_tries set in retry decorator
        """

        id = self._check_identifier(id)
        url = self.get_assets_url('meta/{}'.format(id))
        params = {"replace": False,
                  "replace_sets": replace_sets,
                  "buffered_write": buffered_write,
                  "geo_field": geo_field,
                  "shape_group_field": shape_group_field
                  }
        params = self.add_asset_manager_params(params)
        metadata_json = jsonify_metadata(metadata)

        resp = requests.put(
            url,
            json=metadata_json,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not update the metadata for the identifier ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()


    @retry(Exception, logger=logger, initial_wait=1.5, total_tries=10)
    def update_metadata_batch(
            self,
            ids: List[str],
            metadata: List[dict],
            buffered_write: bool = False,
            replace_sets: bool = False,
            geo_field: Optional[str] = None,
            shape_group_field: Optional[str] = None) -> dict:
        """Update an asset's metadata.

        Parameters
        ----------
        id:
            The ID of the asset to update the metadata of.
        metadata:
            The metadata to update the existing metadata with.
        buffered_write:
            If True, ingests the metadata in a buffered fashion.
        replace_sets:
            If True, replaces existing metadata with ``metadata``.  Otherwise, attempts to append ``metadata`` to the
            existing metadata.
        geo_field:
            Geolocation field
        shape_group_field:
            Shape group field (example: UMAP)
        retry:
            If True, retries the call for total_tries set in retry decorator
        """

        ids = [self._check_identifier(id) for id in ids]
        url = self.get_assets_url('meta_batch')
        params = {
                  "replace": False,
                  "replace_sets": replace_sets,
                  "buffered_write": buffered_write,
                  "geo_field": geo_field,
                  "shape_group_field": shape_group_field
                  }
        params = self.add_asset_manager_params(params)
        metadata_json = [jsonify_metadata(meta) for meta in metadata]

        body = {"ids": ids, "metadata": metadata_json}

        resp = requests.post(
            url,
            json=body,
            params=params)

        if not resp.ok:
            raise AssetError(
                'Could not update the metadata for the identifier ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()


    def upsert_metadata(
            self,
            id: str,
            metadata: dict,
            geo_field: Optional[str] = None,
            shape_group_field: Optional[str] = None,
            buffered_write: bool = False) -> dict:
        """Upsert an asset's metadata.

        Inserts new fields of ``metadata`` if they do not already exist.  Otherwise, updates the existing field if it
        does exist.

        Parameters
        ----------
        id:
            The ID of the asset to upsert the metadata of.
        metadata:
            The metadata to upsert the existing metadata with.
        geo_field:
            Geolocation field
        shape_group_field:
            Shape group field (example: UMAP)
        buffered_write:
            If True, ingests metadata in a buffered fashion.
        """
        id = self._check_identifier(id)
        url = self.get_assets_url('meta/{}'.format(id))
        params = {"replace": True,
                  "replace_sets": True,
                  "buffered_write": buffered_write,
                  "geo_field": geo_field,
                  "shape_group_field": shape_group_field
                  }
        params = self.add_asset_manager_params(params)
        metadata_json = jsonify_metadata(metadata)

        resp = requests.put(
            url,
            json=metadata_json,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not upsert the metadata for the identifier ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def assets_iterator(
            self,
            query: Optional[dict] = None,
            filters: Optional[dict] = None,
            sort_field: str = "id",
            sort_order: str = "asc") -> Iterator[Asset]:

        """Retrieve an iterator for Assets with a search query.

                Parameters
                ----------
                query:
                    Query to locate the data subset of interest.  Filters through existing
                    assets according to the dictionary passed.
                filters:
                    Filter names and values to append to ``query``.  Dict keys represent the existing filter names,
                    and dict values are the filter values.
                sort_field:
                    Filters for the specified name.
                sort_order:
                    Specifies the string sorting order. [asc. desc]

                Returns
                -------
                Iterator[Asset]
                    Iterator for assets

                """

        class AssetIterator(Iterator):
            # Constructor
            def __init__(self,
                         asset_manager_client: AssetManagerClient,
                         query_: dict,
                         ):
                self.query = query_
                self.asset_manager_client = asset_manager_client
                self.params = {
                    "size": DEFAULT_PAGINATION,
                    "offset": 0,
                    "scan": False,
                    "sort_field": sort_field,
                    "sort_order": sort_order
                }
                self.index = 0
                self.results = []
                self.len = 0
                self.search_after = None

            def __next__(self):
                if self.index >= self.len:
                    params = {"size": DEFAULT_PAGINATION,
                              "offset": 0,
                              "scan": False,
                              "sort_field": sort_field,
                              "sort_order": sort_order
                              }
                    if self.search_after is not None:
                        params["search_after"] = self.search_after
                    url = self.asset_manager_client.get_assets_url('')
                    params = self.asset_manager_client.add_asset_manager_params(params)
                    resp = requests.post(url, json=query, params=params)
                    if not resp.ok:
                        raise AssetError(
                            'Could not search the files ::: {} -- {} -- {}'.format(
                                self.asset_manager_client.asset_type, resp.reason, resp.content))
                    self.results = resp.json().get("results")
                    self.len = len(self.results)
                    if self.results:
                        self.search_after = self.results[-1]
                    else:
                        raise StopIteration
                    self.index = 0

                asset = Asset(id=self.results[self.index],
                              asset_manager_client=self.asset_manager_client)
                self.index += 1
                return asset

        query = self._construct_query(query, filters)

        return AssetIterator(
            asset_manager_client=self,
            query_=query
        )

    def search_assets(
            self,
            query: Optional[dict] = None,
            filters: Optional[dict] = None,
            size: int = DEFAULT_SEARCH_SIZE,
            offset: int = 0,
            sort_field: Optional[str] = None,
            sort_order: Optional[str] = None,
            scan: bool = False) -> List[str]:
        """Retrieve asset IDs with a search query.

        Returns the top ``size`` matching hits.  If a return of more than 10000 hits is desired, please use
        AssetManagerClient.search_assets_large().

        Parameters
        ----------
        query:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        filters:
            Filter names and values to append to ``query``.  Dict keys represent the existing filter names,
            and dict values are the filter values.
        size:
            Specifies the Elasticsearch search size.  The maximum number of hits to return.
            Has no effect if ``scan`` is False.
        offset:
            Specifies the Elasticsearch search offset.  The number of hits to skip.
            Has no effect if ``scan`` is False.
        sort_field:
            Filters for the specified name.
        sort_order:
            Specifies the Elasticsearch string sorting order.
        scan:
            If True, uses the Elasticsearch scan capability.
            Otherwise, uses the Elasticsearch search API.

        Returns
        -------
        List[str]
            A list of the IDs of the assets fulfilling the search query.

        """
        query = self._construct_query(query, filters)
        params = {'size': size, 'offset': offset, 'scan': scan}
        if sort_field:
            params['sort_field'] = sort_field
        if sort_order:
            params['sort_order'] = sort_order
        url = self.get_assets_url('')
        params = self.add_asset_manager_params(params)
        resp = requests.post(url, json=query, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not search the files ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()['results']

    def search_assets_large(
            self,
            query: Optional[dict] = None,
            filters: Optional[dict] = None
    ) -> List[str]:
        """Retrieve all asset IDs matching a search query.

        Return all hits matching a search query.  If a return of less than 10000 hits is desired, please use
        AssetManagerClient.search_assets() or SceneEngineClient.search_assets().

        Parameters
        ----------
        query:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        filters:
            Filter names and values to append to ``query``.  Dict keys represent the existing filter names,
            and dict values are the filter values.

        Returns
        -------
        List[str]
            A list of the IDs of the assets fulfilling the search query.
        """
        query = self._construct_query(query, filters)
        params = {"size": DEFAULT_PAGINATION,
                  "offset": 0,
                  "scan": False,
                  "sort_field": "id",
                  "sort_order": "asc"
                  }
        url = self.get_assets_url('')
        params = self.add_asset_manager_params(params)
        resp = requests.post(url, json=query, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not search the files ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        results = resp.json().get('results')
        if results:
            search_after = resp.json()['results'][-1]
        else:
            return results
        while search_after is not None:
            params = {"size": DEFAULT_PAGINATION,
                      "offset": 0,
                      "scan": False,
                      "sort_field": "id",
                      "sort_order": "asc",
                      "search_after": search_after
                      }
            url = self.get_assets_url('')
            params = self.add_asset_manager_params(params)
            resp = requests.post(url, json=query, params=params)
            if not resp.ok:
                raise AssetError(
                    'Could not search the files ::: {} -- {} -- {}'.format(
                        self.asset_type, resp.reason, resp.content))
            if resp.json().get('results'):
                res = resp.json()['results']
                results += res
                search_after = res[-1]
            else:
                break
        return results

    def delete_with_query(self,
                          query: Optional[dict] = None,
                          filters: Optional[dict] = None,
                          wait_for_completion: bool = False) -> str:
        """Delete assets specified with a search query.

        Parameters
        ----------
        query:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        filters:
            Filter names and values to append to ``query``.  Dict keys represent the existing filter names,
            and dict values are the filter values.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.

        Returns
        -------
        str
            The id of the Job that carries out the asset deletion.

        """
        query = self._construct_query(query, filters)
        params = self.add_asset_manager_params()
        url = self.get_assets_url('remove_with_query/')
        resp = requests.post(url, json=query, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not remove the assets ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        job_id = resp.json()['job_id']
        if wait_for_completion:
            self._wait_for_job_completion(job_id)

        return job_id

    def delete_with_list(self,
                         assets_list: Optional[list] = None,
                         wait_for_completion: bool = False) -> str:
        """Delete assets specified with a list of asset IDs.

        Parameters
        ----------
        assets_list:
            Asset IDs of the assets to delete.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.

        Returns
        -------
        str
            The id of the Job that carries out the asset deletion.
        """
        assets_list = assets_list or []
        params = self.add_asset_manager_params()
        url = self.get_assets_url('remove_with_list/')
        resp = requests.post(
            url,
            json={
                "assets_list": assets_list},
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not remove the assets ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))

        job_id = resp.json()['job_id']
        if wait_for_completion:
            self._wait_for_job_completion(job_id)

        return job_id

    def search_meta(
            self,
            query=None,
            size=DEFAULT_SEARCH_SIZE,
            filters: Optional[dict] = None,
            offset=0,
            sort_field=None,
            sort_order=None,
            scan=False) -> List[dict]:

        """Retrieve asset metadata with a search query.

        Returns the top ``size`` matching hits.  If a return of more than 10000 hits is desired, please use
        AssetManagerClient.search_meta_large().

        Parameters
        ----------
        query:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        filters:
            Filter names and values to append to ``query``.  Dict keys represent the existing filter names,
            and dict values are the filter values.
        size:
            Specifies the Elasticsearch search size.  The maximum number of hits to return.
            Has no effect if ``scan`` is False.
        offset:
            Specifies the Elasticsearch search offset.  The number of hits to skip.
            Has no effect if ``scan`` is False.
        sort_field:
            Filters for the specified name.
        sort_order:
            Specifies the Elasticsearch string sorting order.
        scan:
            If True, uses the Elasticsearch scan capability.
            Otherwise, uses the Elasticsearch search API.

        Returns
        -------
        List[dict]
            A list of the metadata dicts of each asset that fulfills the search query.
        """
        query = self._construct_query(query, filters)
        params = {'size': size, 'offset': offset, 'scan': scan}
        if sort_field:
            params['sort_field'] = sort_field
        if sort_order:
            params['sort_order'] = sort_order
        url = self.get_assets_url('meta')
        params = self.add_asset_manager_params(params)
        resp = requests.post(url, json=query, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not search the metadata ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def search_meta_large(
            self,
            query: Optional[dict] = None,
            filters: Optional[dict] = None) -> List[dict]:
        """Retrieve all asset metadata matching a search query.

        Return all hits matching a search query.  If a return of less than 10000 hits is desired, please use
        AssetManagerClient.search_meta() or SceneEngineClient.search_meta().

        Parameters
        ----------
        query:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        filters:
            Filter names and values to append to ``query``.  Dict keys represent the existing filter names,
            and dict values are the filter values.

        Returns
        -------
        List[dict]
            A list of the metadata dicts of each asset that fulfills the search query.

        """
        query = self._construct_query(query, filters)
        params = {"size": DEFAULT_PAGINATION,
                  "offset": 0,
                  "scan": False,
                  "sort_field": "id",
                  "sort_order": "asc"
                  }
        url = self.get_assets_url('meta')
        params = self.add_asset_manager_params(params)
        resp = requests.post(url, json=query, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not search the files ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        results = resp.json()
        if results:
            search_after = resp.json()[-1]['id']
        else:
            return results
        while search_after:
            params = {"size": DEFAULT_PAGINATION,
                      "offset": 0,
                      "scan": False,
                      "sort_field": "id",
                      "sort_order": "asc",
                      "search_after": search_after
                      }
            url = self.get_assets_url('meta')
            params = self.add_asset_manager_params(params)
            resp = requests.post(url, json=query, params=params)
            if not resp.ok:
                raise AssetError(
                    'Could not search the files ::: {} -- {} -- {}'.format(
                        self.asset_type, resp.reason, resp.content))
            if resp.json():
                res = resp.json()
                results += res
                search_after = res[-1]['id']
            else:
                break
        return results

    def summary_meta(self, summary_request: dict) -> dict:
        """Get a metadata summary.

        Parameters
        ----------
        summary_request:
            Dict of summary settings of the following form:
            {
                "search" (dict): <Query to locate the data subset of interest>,
                "dimensions" (Optional[List[str]): <Dimensions of summary (term aggregations)>,
                "custom_buckets_numeric" Optional[List[dict]]: <Buckets for range aggregation>
                "custom_buckets_time" Optional[List[dict]]: <Buckets for date_range aggregation>
                "aggregate_field" Optional[str]: <Field for metric aggregations>
                "aggregation_type" Optional[str]: <Type of metric aggregation (e.g. avg, sum)>
            }

        Returns
        -------
        dict
            Metadata summary according to ``summary_request``.

        """
        url = self.get_assets_url('meta/summary/')
        params = self.add_asset_manager_params()
        resp = requests.post(
            url,
            json=summary_request,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not retrieve the metadata summary ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def summary_2d(self, summary_2d_request):
        url = self.get_assets_url('summary_2d/')
        params = self.add_asset_manager_params()
        resp = requests.post(
            url,
            json=summary_2d_request,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not get the confusion matrix for ::: {} -- {} -- {}'.format(
                    summary_2d_request, resp.reason, resp.content))
        return resp.json()

    def api_status(self):
        url = self.get_assets_url('status/')
        params = self.add_asset_manager_params()
        resp = requests.get(url, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not check the status of the API ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))

    def get_assets_url(self, route=""):
        url = join(self.assets_namespace_url, route)
        return url

    def get_statistics(self, field_dicts: List[dict]):
        statistics_endpoint = self.get_assets_url("field_statistics/")
        params = self.add_asset_manager_params()
        resp = requests.post(
            statistics_endpoint,
            params=params,
            json={
                'field_dicts': field_dicts})
        if not resp.ok:
            raise AssetError(
                'Could not get field statistics ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def _get_job_status(self, job_id):
        """Get the status of the async job.

        Assumes that the job_id is the same as the celery task_id

        :param job_id: Celery task ID
        :return:
        """
        status_endpoint = join(
            self.jobs_namespace_url, "status", job_id)
        params = {}
        if self.auth_token:
            params['token'] = self.auth_token
        resp = requests.get(status_endpoint, params=params)
        status = resp.json().get('status')
        return status

    def _wait_for_job_completion(self, job_id):
        while True:
            status = self._get_job_status(job_id)
            if status == JobConstants.STATUS_FINISHED:
                break
            elif status in {JobConstants.STATUS_ABORTED}:
                job_metadata = self.with_asset_state(
                    'jobs', True).get_metadata(job_id)
                job_notes = job_metadata['notes']
                raise JobError(
                    'Job {} encountered error with status {} with notes::: {}'.format(
                        job_id, status, job_notes))
            else:
                time.sleep(1)

    def _wait_for_existence(self, id = None,
                            ids: List[str] = None,
                            increments_sec: int = 5,
                            max_wait_sec: int = 120):
        elapsed_time = 0
        if ids is not None:
            # Wait on multiple assets
            exists_status = [False] * len(ids)
            while sum(exists_status) < len(ids):
                if elapsed_time >= max_wait_sec:
                    raise TimeoutError("Timeout waiting for {} ids to exist".format(len(ids)))

                exists_status = self.exists_multiple(ids)
                elapsed_time += increments_sec
                time.sleep(increments_sec)
        else:
            # Wait on single asset
            id = self._check_identifier(id)
            while not self.exists(id):
                time.sleep(PAUSE_TIME)

    def _wait_for_non_existence(self, id):
        id = self._check_identifier(id)
        while self.exists(id):
            time.sleep(PAUSE_TIME)

    def _check_storage(self):
        if self.metadata_only:
            raise AssetError('Asset client is metadata only')

    def update_asset_state(self, asset_type: str, metadata_only: bool = False):

        if self.is_non_standard_asset is False and asset_type not in AssetsConstants.VALID_ASSETS:
            raise AssetError(
                "The asset type {} is invalid. Valid types are: {}".format(
                    asset_type, AssetsConstants.VALID_ASSETS))

        if not isinstance(metadata_only, bool):
            raise ValueError("metadata_only must be a boolean")

        self.asset_type = asset_type
        if asset_type in AssetsConstants.METADATA_ONLY_ASSETS:
            self.metadata_only = True
        else:
            self.metadata_only = metadata_only

    def with_asset_state(self, asset_type: str, metadata_only: bool = False):
        """Set the asset state, for use in chaining.

        Eg. client.with_asset_state("images", True).search_files({})
        """

        self.update_asset_state(
            asset_type=asset_type,
            metadata_only=metadata_only)
        return self

    def _construct_query(self,
                         query: Optional[Dict],
                         filters: Optional[Dict]):
        if query is None:
            query = {}
        elif not isinstance(query, dict):
            raise ValueError('Query parameter must be a dictionary')

        if filters:
            query_filters = query.get("filters", [])
            for key, value in filters.items():
                if isinstance(value, list):
                    query_filters.append({"field": key, "values": value})
                else:
                    query_filters.append({"field": key, "values": [value]})
            query["filters"] = query_filters
        return query

    def _check_identifier(self, id: str) -> str:
        # Perform any preprocessing on the identifier
        if self.asset_type == AssetsConstants.SESSIONS_ASSET_ID:
            id = standardize_name(id)
        return id

    def download_data_with_query(self,
                                 destination_dir: str,
                                 query: Optional[dict] = None,
                                 download_metadata=True) -> dict:
        """Download asset files using a search query.

        Parameters
        ----------
        destination_dir:
            The existing local directory to download the files to.
        query:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        download_metadata:
            If True, downloads asset metadata.  Otherwise, does not download asset metadata.

        Returns
        -------
        dict
            Maps asset IDs obtained with ``query`` to local filepath and metadata.
            Highest level keys represent asset IDs. Lower level keys "filepath" and "metadata" map to local filepath and
            metadata for a specific ID.
        """

        if not os.path.isdir(destination_dir):
            raise NotADirectoryError(
                "{} does not exist".format(destination_dir))

        ids = self.search_assets(
            query=query, scan=True)

        local_dataset = {}

        def threaded_download_asset_and_metadata(id: str):
            logger.info(
                "downloading binary and metadata for {}".format(id))
            local_access = {}
            if not self.metadata_only:
                filepath = os.path.join(destination_dir, id)
                self.get_file_and_write(id=id, write_filepath=filepath)
                local_access["filepath"] = filepath
            if download_metadata:
                metadata = self.get_metadata(id=id)
                local_access["metadata"] = metadata
                json_filepath = os.path.join(
                    destination_dir, '{}.json'.format(id))
                with open(json_filepath, 'w') as file:
                    file.write(json.dumps(metadata))

            local_dataset[id] = local_access

        run_threaded(func=threaded_download_asset_and_metadata,
                     iterable=ids,
                     desc="download data with query")

        return local_dataset

    def get_temporary_upload_url(self,
                                 ids: List[str],
                                 corr_asset_id: Optional[str] = None,
                                 corr_asset_type: Optional[str] = None,
                                 content_type: Optional[str] = None,
                                 ) -> Dict:
        params = self.add_asset_manager_params()
        body = {"ids": ids}

        if corr_asset_id:
            body["corr_asset_id"] = corr_asset_id

        if corr_asset_type:
            body["corr_asset_type"] = corr_asset_type

        if content_type:
            body["content_type"] = content_type

        resp = requests.post(
            self.get_assets_url('temporary_upload_url/'),
            json=body,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not get temporary upload url::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def get_storage_url(self,
                        ids: List[str],
                        corr_asset_id: Optional[str] = None,
                        corr_asset_type: Optional[str] = None,
                        ) -> Dict:
        params = self.add_asset_manager_params()
        body = {"ids": ids}

        if corr_asset_id:
            body["corr_asset_id"] = corr_asset_id

        if corr_asset_type:
            body["corr_asset_type"] = corr_asset_type

        resp = requests.post(
            self.get_assets_url('storage_url/'),
            json=body,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not get storage url::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def get_auxiliary_search_fields(self) -> List[dict]:
        all_search_fields = self.get_all_search_fields()
        return [
            d for d in all_search_fields if d['field'].startswith(
                AUXILIARY_KEY + ".")]

    def get_all_search_fields(self) -> List[dict]:
        resp = requests.get(
            self.get_assets_url("meta/search_fields/"),
            params=self.add_asset_manager_params()
        )
        if not resp.ok:
            raise AssetError(
                'Could not get search fields::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def get_url_from_object_access(self,
                                   object_access: ObjectAccess,
                                   corr_id: Optional[str] = None) -> str:

        if object_access.url:
            return object_access.url

        params = self.add_asset_manager_params()
        body = object_access.to_dic()
        if corr_id:
            body["corr_id"] = corr_id
        resp = requests.post(
            self.get_assets_url('url_from_object_access/'),
            json=body,
            params=params
        )
        if not resp.ok:
            raise AssetError('Could not get url for {}::: {} -- {} -- {}'.format(
                object_access.to_dic(), self.asset_type, resp.reason, resp.content))

        return resp.json()["url"]

    def get_bytes_from_object_access(self,
                                     object_access: ObjectAccess,
                                     corr_id: Optional[str] = None) -> bytes:

        url = self.get_url_from_object_access(
            object_access=object_access, corr_id=corr_id)

        resp = requests.get(url)
        if not resp.ok:
            raise AssetError(
                'Could not get url ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.content

    def add_auxiliary_metadata(
            self,
            id: Optional[str] = None,
            ids: Optional[List[str]] = None,
            search: Optional[dict] = None,
            filters: Optional[dict] = None,
            **kwargs: Dict[str, Any]
    ):
        """Add auxiliary metadata to an asset.

        Parameters
        ----------
        id:
            An asset IDs to add the auxiliary metadata to.
        ids:
            A list of asset IDs to add the auxiliary metadata to.
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        filters:
            Filter names and values to append to ``search``.  Dict keys represent the existing filter names,
            and dict values are the filter values.
        **kwargs:
            Maps custom metadata labels to any value.  Keys represent the auxiliary metadata labels.
            Values represent the auxiliary metadata values.
        """

        _ids = []
        if id:
            _ids.append(id)

        if ids:
            _ids.extend(ids)

        if search is not None or filters:
            _ids.extend(self.search_assets(query=search, filters=filters, scan=True))
        metadata = {AUXILIARY_KEY: kwargs}

        def _update_metadata_threaded(id_):
            self.update_metadata(id=id_,
                                 metadata=metadata,
                                 replace_sets=False)

        disable_threading = len(_ids) < 2
        run_threaded(func=_update_metadata_threaded,
                     iterable=_ids,
                     disable_threading=disable_threading,
                     disable_tqdm=disable_threading)

    def clear_cache(self, all_organizations: bool = False, partitions: Optional[List[str]]=None):
        '''
        Clears asset manager's Redis cache by organization
        Args:
            all_organizations: if True, Redis cache for all organization is cleared. Requires Admin privilege
            partitions: list of partitions (like images, sets, annotations) to clear their cache, if not set, all is cleared

        Returns:
            ACK_OK_RESPONSE on success
        '''

        url = join(self._get_root_url(),'clear_cache')
        params = {"all_organizations": all_organizations}
        if self.auth_token:
            params['token'] = self.auth_token

        payload = {"partitions": partitions} if partitions else {}
        return requests.post(url, params=params,json=payload).json()