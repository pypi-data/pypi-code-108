import abc
import json
import os
import shutil
import time
import uuid
from datetime import datetime

import appdirs  # type: ignore

from biolib.biolib_errors import BioLibError
from biolib.compute_node.job_worker.cache_types import LfsCacheStateDict, UuidStr, StoragePartition, \
    DockerImageCacheStateDict
from biolib.typing_utils import Dict, List, Optional, Generic, TypeVar


class CacheStateError(BioLibError):
    pass


class DockerCacheStateError(CacheStateError):
    pass


StateType = TypeVar('StateType')


class CacheState(abc.ABC, Generic[StateType]):
    _cache_dir: str = appdirs.user_cache_dir(appname='pybiolib', appauthor='biolib')

    @property
    @abc.abstractmethod
    def _state_path(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _state_lock_path(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_default_state(self) -> StateType:
        raise NotImplementedError

    def __init__(self):
        self._state: Optional[StateType] = None

    def __enter__(self) -> StateType:
        self._acquire_state_lock()
        if os.path.exists(self._state_path):
            with open(self._state_path, mode='r') as file:
                self._state = json.loads(file.read())
        else:
            self._state = self._get_default_state()
            with open(self._state_path, mode='w') as file:
                file.write(json.dumps(self._state))

        # Check for type checking
        if self._state is None:
            raise CacheStateError('Internal state is not defined')

        return self._state

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        with open(self._state_path, mode='w') as file:
            file.write(json.dumps(self._state))

        self._release_state_lock()

    def _acquire_state_lock(self) -> None:
        timeout_seconds = 5.0
        seconds_to_sleep = 0.5
        while os.path.exists(self._state_lock_path):
            time.sleep(seconds_to_sleep)
            timeout_seconds -= seconds_to_sleep
            if timeout_seconds < 0:
                raise CacheStateError('Cache state timed out waiting for lock file')

        os.makedirs(self._cache_dir, exist_ok=True)
        lock_file = open(self._state_lock_path, mode='x')
        lock_file.close()

    def _release_state_lock(self) -> None:
        if os.path.exists(self._state_lock_path):
            os.remove(self._state_lock_path)
        else:
            raise CacheStateError('Cache state was not locked.')

    @staticmethod
    def get_timestamp_now() -> str:
        return datetime.now().isoformat()


class LfsCacheState(CacheState):
    @property
    def _state_path(self) -> str:
        return f'{super()._cache_dir}/lfs-cache-state.json'

    @property
    def _state_lock_path(self) -> str:
        return f'{self._state_path}.lock'

    def _get_default_state(self) -> LfsCacheStateDict:
        return LfsCacheStateDict(
            large_file_systems={},
            storage_partitions=self._get_storage_partitions_from_env(),
        )

    @staticmethod
    def get_tmp_storage_paths() -> List[str]:
        lfs_tmp_storage_path_env_key = 'BIOLIB_LFS_TMP_STORAGE_PATHS'
        lfs_tmp_storage_paths = os.environ.get(lfs_tmp_storage_path_env_key)
        if lfs_tmp_storage_paths is None:
            raise CacheStateError(f'Environment variable "{lfs_tmp_storage_path_env_key}" not set')

        return lfs_tmp_storage_paths.split(',')

    @staticmethod
    def _get_storage_partitions_from_env() -> Dict[UuidStr, StoragePartition]:
        lfs_storage_path_env_key = 'BIOLIB_LFS_STORAGE_PATHS'
        lfs_storage_paths = os.environ.get(lfs_storage_path_env_key)
        if lfs_storage_paths is None:
            raise CacheStateError(f'Environment variable "{lfs_storage_path_env_key}" not set')

        storage_states: Dict[UuidStr, StoragePartition] = {}
        for lfs_storage_path in lfs_storage_paths.split(','):
            if not os.path.isdir(lfs_storage_path):
                raise CacheStateError(f'LFS storage path {lfs_storage_path} is not a directory')

            uuid_str = str(uuid.uuid4())
            disk_usage = shutil.disk_usage(lfs_storage_path)
            storage_states[uuid_str] = StoragePartition(
                allocated_size_bytes=0,
                path=lfs_storage_path,
                total_size_bytes=disk_usage.free,
                uuid=uuid_str,
            )

        return storage_states


class DockerImageCacheState(CacheState):
    @property
    def _state_path(self) -> str:
        return f'{super()._cache_dir}/docker-cache-state.json'

    @property
    def _state_lock_path(self) -> str:
        return f'{self._state_path}.lock'

    def _get_default_state(self) -> DockerImageCacheStateDict:
        return {}
