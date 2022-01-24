# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Factory class that automatically selects the appropriate cache store."""
from typing import Optional
import logging
import os

from azureml.automl.core.shared._diagnostics.contract import Contract

from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.automl.runtime.shared.memory_cache_store import MemoryCacheStore
from azureml.data.azure_storage_datastore import AzureBlobDatastore
from azureml.automl.runtime.shared import lazy_file_cache_store as lfcs
from azureml.automl.runtime.shared.lazy_azure_blob_cache_store import LazyAzureBlobCacheStore
from azureml.automl.runtime.shared import file_dataset_cache

logger = logging.getLogger(__name__)


class CacheStoreFactory:

    @staticmethod
    def get_cache_store(
        temp_location: str,
        run_target: str,
        run_id: Optional[str],
        data_store: Optional[AzureBlobDatastore] = None,
        task_timeout: int = lfcs._CacheConstants.DEFAULT_TASK_TIMEOUT_SECONDS,
        use_fd_cache: bool = False
    ) -> CacheStore:
        """Get the cache store based on run type."""
        try:
            if run_id is None:
                return MemoryCacheStore()

            if data_store is not None and run_target != "local":
                Contract.assert_type(data_store, name='data_store', expected_types=AzureBlobDatastore)

                # Only used FileDataset cache if the env var is set.
                if use_fd_cache:
                    return file_dataset_cache.FileDatasetCache(
                        data_store=data_store, blob_path=run_id, task_timeout=task_timeout
                    )
                else:
                    return LazyAzureBlobCacheStore(
                        data_store=data_store, blob_path=run_id, task_timeout=task_timeout, temp_dir_path=temp_location
                    )

            return lfcs.LazyFileCacheStore(path=temp_location)
        except Exception as e:
            logger.warning("Cannot proceed with the Run {} without a valid storage for intermediate files. "
                           "Encountered an exception of type: {}".format(run_id, type(e)))
            raise
