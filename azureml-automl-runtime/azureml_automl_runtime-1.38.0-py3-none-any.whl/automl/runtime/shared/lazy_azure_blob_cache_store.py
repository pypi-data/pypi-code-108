# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module containing the implementation for an azure based cache to be used for saving automl data between runs."""
import logging
import os
import pathlib
import shutil
import tempfile
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional

from azure.common import AzureHttpError
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (CredentiallessDatastoreNotSupported,
                                                                              InaccessibleDataStore,
                                                                              OtherDataStoreException)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import CacheException, ValidationException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared import lazy_file_cache_store as lfcs
from azureml.automl.runtime.shared._cache_constants import Keys
from azureml.data.azure_storage_datastore import AzureBlobDatastore

logger = logging.getLogger(__name__)


class LazyAzureBlobCacheStore(lfcs.LazyFileCacheStore):
    """
    File cache store backed by Azure Blob Storage.

    This class inherits all of the default behavior from the super class. In addition to that, all the objects
    added to this cache store is also uploaded to an Azure Blob Store, under the blob_path specified in the
    during the initialization of this class.
    """

    def __init__(
            self,
            data_store: AzureBlobDatastore,
            blob_path: str,
            task_timeout: int = lfcs._CacheConstants.DEFAULT_TASK_TIMEOUT_SECONDS,
            temp_dir_path: Optional[str] = None,
    ):
        temp_dir_path = temp_dir_path or tempfile.mkdtemp()
        super().__init__(os.path.join(temp_dir_path, blob_path))

        self._data_store = data_store
        self._blob_path = blob_path
        self._task_timeout = task_timeout
        self._validate_data_store()

    def _validate_data_store(self) -> None:
        """
        Validate datastore object and it's various attributes.
        """
        Contract.assert_value(value=self._data_store, name='data_store', log_safe=True)
        Contract.assert_value(value=self._data_store.blob_service, name='data_store.blob_service', log_safe=True)
        Contract.assert_value(value=self._data_store.container_name, name='data_store.container_name', log_safe=True)

        # Check the datastore is not credentialless (currently unsupported by AutoML 1521429).
        if self._data_store.sas_token is None and self._data_store.account_key is None:
            logger.error("Identified datastore as credentialless.")
            raise ValidationException._with_error(
                AzureMLError.create(
                    CredentiallessDatastoreNotSupported,
                    data_store=self._data_store.name,
                    reference_code=ReferenceCodes._CREDENTIALLESS_DATASTORE_FAILURE
                )
            )

        # Check that datastore has valid credentials by attempting to retrieve metadata from datastore.
        try:
            self._data_store.blob_service.get_container_metadata(self._data_store.container_name)
        except AzureHttpError as e:
            if "AuthenticationError" in str(e):
                raise ValidationException._with_error(
                    AzureMLError.create(
                        InaccessibleDataStore,
                        data_store_name=self._data_store.name,
                        reference_code=ReferenceCodes._CACHE_AUTH_ERROR,
                    )) from e
            else:
                raise ValidationException._with_error(
                    AzureMLError.create(
                        OtherDataStoreException,
                        data_store_name=self._data_store.name,
                        exception=e,
                        reference_code=ReferenceCodes._CACHE_AZUREHTTP_ERROR,
                    )) from e
        except Exception as e:
            raise ValidationException._with_error(
                AzureMLError.create(
                    OtherDataStoreException,
                    data_store_name=self._data_store.name,
                    exception=e,
                    reference_code=ReferenceCodes._CACHE_OTHER_ERROR,
                )) from e

    def _download_cache(self) -> None:
        """
        Download files from _blob_path to the _root directory and return the list of files downloaded.

        :return: List of files from the _blob_path downloaded to the _root dir.
        """
        try:
            local_path = str(pathlib.Path(self._root).parent)
            self._data_store.download(
                target_path=local_path, prefix=self._blob_path, overwrite=True, show_progress=False
            )
        except Exception as ex:
            logging_utilities.log_traceback(ex, logger, is_critical=False)
            msg = f"Failed to download files from the data store. Error type: {ex.__class__.__name__}"
            raise CacheException.from_exception(ex, msg=msg).with_generic_msg(msg)

    def load(self) -> None:
        """
        Read the contents of the blob at the path and store keys, data references to them
        in memory. This will hydrate `cached_items` field of this.
        """
        # download the files in the blob locally
        self._download_cache()
        # load the files as items available on the cache
        super(LazyAzureBlobCacheStore, self).load()

    def set(self, key: str, value: Any) -> None:
        """
        Set key and value in the cache.

        :param key: Key to store.
        :param value: Value to store.
        """
        Contract.assert_value(value=key, name='key', log_safe=True)
        # TODO When sample_weight is None, we are still calling this and uploading a
        # pickle that has `None`. Need to fix this.
        self.add([key], [value])

    def add(self, keys: Iterable[str], values: Iterable[Any]) -> None:
        """
        Serialize the values and add them to cache and upload to the azure blob container.

        :param keys: List of keys.
        :param values: Corresponding values to be cached.
        """
        Contract.assert_value(value=keys, name='keys', log_safe=True)
        super(LazyAzureBlobCacheStore, self).add(keys, values)

        # upload the files to the datastore
        keys_written = {k: self.cache_items[k] for k in keys}
        self._upload_multiple(keys_written)

    def remove(self, key: str) -> None:
        """
        Remove key from store.

        :param key: store key
        """
        try:
            to_remove = self.cache_items[key]
            self._data_store.blob_service.delete_blob(
                self._data_store.container_name,
                to_remove.path,
                timeout=self._task_timeout
            )
            del self.cache_items[key]
        except KeyError as ke:
            logging_utilities.log_traceback(ke, logger, is_critical=False)
            msg = "Failed to find key '{}' in cache.".format(key)
            raise CacheException.from_exception(ke, msg=msg).with_generic_msg(msg)
        except Exception as e:
            logging_utilities.log_traceback(e, logger, is_critical=False)
            msg = "Failed to delete key '{}' from cache. Exception type: {}".format(
                key, e.__class__.__name__)
            raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

    def remove_all(self):
        """Remove all the cache from store."""
        keys = list(self.cache_items.keys())
        for key in keys:
            self.remove(key)

    def upload_file(self, src: str, dest: str) -> None:
        """
        Upload a file directly to AzureML Datastore specifing target_path via dest.

        :param src: The full path to the desired file to upload.
            NOTE - src can be based of grain key/value combinations and should not be logged!
        :type src: str
        :param dest: The target_path to be written to within the Datastore (backed by Azure Blob).
        :type dest: str
        """
        with self.log_activity():
            try:
                self._data_store.upload_files(
                    files=[src],
                    target_path=dest,
                    show_progress=False,
                    overwrite=True
                )
            except MemoryError:
                raise
            except Exception as e:
                logging_utilities.log_traceback(e, logger, is_critical=False)
                msg = "Failed to upload file to the cache. Exception type: {}".format(
                    e.__class__.__name__
                )
                raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

    def _upload_multiple(self, keys_with_local_paths: Dict[str, lfcs.CachedValue]) -> List[lfcs.CachedValue]:
        """
        The key in `keys_with_local_paths` represents the fully qualified name of the key, and the value
        contains the file path on the local disk where the key was serialized.

        :param keys_with_local_paths: The items to be uploaded
            NOTE cached_value file paths may not be log safe!
        :returns: Updated CachedValue list with the path pointing to the location of files on blob.
        """
        with self.log_activity():
            namespace_to_files_map = defaultdict(list)  # type: Dict[str, List[lfcs.CachedValue]]
            for k, v in keys_with_local_paths.items():
                namespace = pathlib.Path(k).parent.as_posix()
                if namespace.strip() in [".", "/", ""]:
                    # If this is the root namespace, be explicit about it
                    namespace = Keys.DEFAULT_NAMESPACE
                namespace_to_files_map[namespace].append(v)

            updated_cached_values = []  # type: List[lfcs.CachedValue]
            for namespace, cached_values in namespace_to_files_map.items():
                upload_path = (pathlib.Path(self._blob_path) / namespace)
                files = [c.path for c in cached_values]
                # batch upload all files within a folder together
                try:
                    self._data_store.upload_files(
                        files=files,
                        target_path=upload_path.as_posix(),
                        show_progress=False,
                        overwrite=True
                    )
                except MemoryError:
                    raise
                except Exception as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    msg = "Failed to upload files to the cache. Exception type: {}".format(
                        e.__class__.__name__
                    )
                    raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

                for cv in cached_values:
                    f_name = upload_path / pathlib.Path(cv.path).name
                    updated_cached_values.append(
                        lfcs.CachedValue(f_name.as_posix(), cv.func)
                    )

            return updated_cached_values

    def __repr__(self):
        path = self._blob_path[:self._blob_path.rfind("/cache")]
        return "{c}(data_store=\"{ds}\", blob_path=\"{path}\", task_timeout={to})".format(
            c=self.__class__.__name__, ds=self._data_store, path=path, to=self._task_timeout)

    def __del__(self):
        shutil.rmtree(self._root)

    def __getstate__(self):
        """
        Get this cache store's state.

        :return: A tuple of dictionaries containing object's state.
        """
        return super().__getstate__(), {
            'blob_path': self._blob_path,
            'max_retries': self.max_retries,
            'task_timeout': self._task_timeout,
            'ds_name': self._data_store.name,
            'ds_container_name': self._data_store.container_name,
            'ds_account_name': self._data_store.account_name,
            'ds_sas_token': self._data_store.sas_token,
            'ds_account_key': self._data_store.account_key,
            'ds_protocol': self._data_store.protocol,
            'ds_endpoint': self._data_store.endpoint,
            'ds_workspace_msi_has_access': self._data_store.workspace_msi_has_access,
            'ds_subscription_id': self._data_store.subscription_id,
            'ds_resource_group': self._data_store.resource_group,
            'ds_service_data_access_auth_identity': self._data_store.service_data_access_auth_identity
        }

    def __setstate__(self, state):
        """
        Deserialize this cache store's state.

        :param state: Tuple of dictionaries containing object state.
        """
        super_state, my_state = state
        ds_name = my_state['ds_name']
        ds_container_name = my_state['ds_container_name']
        ds_account_name = my_state['ds_account_name']
        ds_sas_token = my_state['ds_sas_token']
        ds_account_key = my_state['ds_account_key']
        ds_protocol = my_state['ds_protocol']
        ds_endpoint = my_state['ds_endpoint']
        ds_workspace_msi_has_access = my_state['ds_workspace_msi_has_access']
        ds_subscription_id = my_state['ds_subscription_id']
        ds_resource_group = my_state['ds_resource_group']
        ds_service_data_access_auth_identity = my_state['ds_service_data_access_auth_identity']

        self._data_store = AzureBlobDatastore(
            workspace=None,
            name=ds_name,
            container_name=ds_container_name,
            account_name=ds_account_name,
            sas_token=ds_sas_token,
            account_key=ds_account_key,
            protocol=ds_protocol,
            endpoint=ds_endpoint,
            workspace_msi_has_access=ds_workspace_msi_has_access,
            subscription_id=ds_subscription_id,
            resource_group=ds_resource_group,
            service_data_access_auth_identity=ds_service_data_access_auth_identity
        )

        self._blob_path = my_state['blob_path']
        self._task_timeout = my_state['task_timeout']
        self.max_retries = my_state['max_retries']

        # Double check datastore access
        self._validate_data_store()
        super().__setstate__(super_state)
