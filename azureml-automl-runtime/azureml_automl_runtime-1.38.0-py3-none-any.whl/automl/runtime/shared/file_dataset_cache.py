# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module containing the implementation for a FileDataset based cache used for saving automl data between runs."""
from typing import Any, Dict, Iterable, List, Optional
import logging
import os
import shutil
import tempfile

from azureml._common._error_definition import AzureMLError
from azureml.core import Datastore, Run

from azureml.data import dataset_error_handling
from azureml.data.azure_storage_datastore import AzureBlobDatastore
from azureml.data.dataset_factory import FileDatasetFactory

from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    DataPathInaccessible
)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import CacheException, UserException

from azureml.automl.runtime.shared import lazy_file_cache_store as lfcs

logger = logging.getLogger()
_USE_FD_CACHE = "USE_FD_CACHE"


class FileDatasetCache(lfcs.LazyFileCacheStore):
    """File cache store backed by azure blob using FileDataset APIs."""
    def __init__(
        self,
        data_store: AzureBlobDatastore,
        blob_path: str,
        task_timeout: int = lfcs._CacheConstants.DEFAULT_TASK_TIMEOUT_SECONDS
    ):
        super().__init__(tempfile.mkdtemp())

        self._data_store = data_store
        self._blob_path = blob_path + "/cache"
        self._task_timeout = task_timeout
        self._validate_data_store()

    def _validate_data_store(self) -> None:
        """
        Validate datastore object.
        """
        Contract.assert_value(value=self._data_store, name='data_store', log_safe=True)

    def _download_cache(self) -> None:
        """
        Download files from _blob_path to the _root directory and return the list of files downloaded.

        :return: List of files from the _blob_path downloaded to the _root dir.
        """
        try:
            FileDatasetFactory.from_files((self._data_store, self._blob_path), validate=False)\
                .download(self._root, overwrite=True)
        except Exception as ex:
            logging_utilities.log_traceback(ex, logger, is_critical=False)
            msg = f"Failed to download files from the data store. Error type: {ex.__class__.__name__}"
            raise CacheException.from_exception(ex, msg=msg).with_generic_msg(msg)

    def load(self) -> None:
        """
        Read the contents of the blob at the path and store keys, data references to them
        in memory. This will hydrate `cached_items` field of this.
        """
        self._download_cache()
        super(FileDatasetCache, self).load()

    def add(self, keys: Iterable[str], values: Iterable[Any]) -> None:
        """
        Serialize the values and add them to cache and upload to the azure blob container.

        :param keys: List of keys.
        :param values: Corresponding values to be cached.
        """
        Contract.assert_value(value=keys, name='keys', log_safe=True)
        super(FileDatasetCache, self).add(keys, values)

        # upload the files to the datastore
        cached_values = [self.cache_items[k] for k in keys]
        self._upload_multiple(cached_values)

    def remove(self, key: str) -> None:
        """
        Remove key from store.

        :param key: store key
        """
        raise NotImplementedError()

    def remove_all(self):
        """Remove all the cache from store."""
        raise NotImplementedError()

    def upload_folder(self, src: str, dest: str) -> None:
        """
        Upload a file directly to AzureML Datastore specifing target_path via dest.

        :param src: The path to the folder with desired files to be uploaded.
            NOTE - src can be based of grain key/value combinations and should not be logged!
        :type src: str
        :param dest: The target_path to be written to within the Datastore (backed by Azure Blob).
        :type dest: str
        """
        with self.log_activity():
            try:
                FileDatasetFactory.upload_directory(src, (self._data_store, dest), overwrite=True)
            except MemoryError:
                raise
            except dataset_error_handling.DatasetValidationError as e:
                # Dataset client fails to capture auth errors so we must catch the subsequent
                # validation error. 1542254
                msg = "Encountered exception while uploading files to azure storage. This can happen "\
                    "when there are insufficient permissions for accessing the storage account."
                raise UserException._with_error(azureml_error=AzureMLError.create(
                    DataPathInaccessible, target="File_Cache_Store",
                    dprep_error=str(msg)), inner_exception=e) from None
            except Exception as e:
                logging_utilities.log_traceback(e, logger, is_critical=False)
                msg = "Failed to upload file to the cache. Exception type: {}".format(
                    e.__class__.__name__
                )
                raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

    def _upload_multiple(
            self,
            cached_values: List[lfcs.CachedValue]) -> List[lfcs.CachedValue]:
        """
        Upload multiple files represented by cached_values to the blob store.

        :param cached_values: The items to be uploaded.
            NOTE cached_value file paths may not be log safe!
        :returns: Updated CachedValue list with the path pointing to the location of files on blob.
        """
        with self.log_activity():
            files = [c.path for c in cached_values]
            file_names = [self._blob_path + "/" + os.path.split(file_path)[1] for file_path in files]
            try:
                FileDatasetFactory.upload_directory(self._root, (self._data_store, self._blob_path), overwrite=True)
            except MemoryError:
                raise
            except dataset_error_handling.DatasetValidationError as e:
                # Dataset client fails to capture auth errors so we must catch the subsequent
                # validation error. 1542254
                msg = "Encountered exception while uploading files to azure storage. This can happen "\
                    "when there are insufficient permissions for accessing the storage account."
                raise UserException._with_error(azureml_error=AzureMLError.create(
                    DataPathInaccessible, target="File_Cache_Store",
                    dprep_error=str(msg)), inner_exception=e) from None
            except Exception as e:
                logging_utilities.log_traceback(e, logger, is_critical=False)
                msg = "Failed to upload files to the cache. Exception type: {}".format(
                    e.__class__.__name__
                )
                raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

            return [lfcs.CachedValue(
                file_name,
                c.func
            ) for file_name, c in zip(file_names, cached_values)]

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
            'ds_name': self._data_store.name
        }

    def __setstate__(self, state):
        """
        Deserialize this cache store's state.

        :param state: Tuple of dictionaries containing object state.
        """
        super_state, my_state = state

        run = Run.get_context()

        ws = run.experiment.workspace
        self._data_store = Datastore.get(ws, my_state['ds_name'])
        self._blob_path = my_state['blob_path']
        self._task_timeout = my_state['task_timeout']
        self.max_retries = my_state['max_retries']

        super().__setstate__(super_state)
