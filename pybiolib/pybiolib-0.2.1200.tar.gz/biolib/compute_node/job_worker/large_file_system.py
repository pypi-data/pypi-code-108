import os
import shutil
import subprocess
import time
import zipfile

import docker.types  # type: ignore

from biolib.biolib_errors import BioLibError
from biolib.compute_node.job_worker.cache_state import LfsCacheState
from biolib.compute_node.job_worker.cache_types import LargeFileSystemCache, StoragePartition
from biolib.typing_utils import TypedDict, Optional, Callable

from biolib.biolib_api_client import LargeFileSystemMapping


class StatusUpdate(TypedDict):
    progress: int
    log_message: str


class LargeFileSystemAttachResponse(TypedDict):
    aws_ebs_volume_id: str
    device_name: str


class DeviceInfo(TypedDict):
    attached_device_name: str
    aws_ebs_volume_id: str
    nvme_device_name: str


class LargeFileSystemError(BioLibError):
    pass


class LargeFileSystem:

    def __init__(
            self,
            job_id: str,
            lfs_mapping: LargeFileSystemMapping,
            send_status_update: Callable[[StatusUpdate], None],
    ):
        self._job_id: str = job_id
        self._lfs_mapping: LargeFileSystemMapping = lfs_mapping
        self._path_on_disk: Optional[str] = None
        self._send_status_update: Callable[[StatusUpdate], None] = send_status_update

    @property
    def _is_initialized(self) -> bool:
        return self._path_on_disk is not None

    @property
    def uuid(self) -> str:
        return self._lfs_mapping['uuid']

    @property
    def docker_mount(self) -> docker.types.Mount:
        if not self._is_initialized:
            raise LargeFileSystemError('LargeFileSystem not initialized')

        return docker.types.Mount(
            read_only=True,
            source=self._path_on_disk,
            target=self._lfs_mapping['to_path'],
            type='bind',
        )

    def initialize(self) -> None:
        if self._is_initialized:
            return

        lfs_size_bytes = self._lfs_mapping['size_bytes']

        lfs_is_already_downloading = False

        with LfsCacheState() as cache_state:
            lfs_cache = cache_state['large_file_systems'].get(self.uuid)

            if lfs_cache is None:

                storage_partition_to_use: Optional[StoragePartition] = None
                for storage_partition in cache_state['storage_partitions'].values():
                    free_space_bytes = storage_partition['total_size_bytes'] - storage_partition['allocated_size_bytes']
                    if lfs_size_bytes < free_space_bytes:
                        storage_partition_to_use = storage_partition
                        break

                if storage_partition_to_use is None:
                    raise LargeFileSystemError('No storage partition with space available')
                else:
                    storage_partition_to_use['allocated_size_bytes'] += lfs_size_bytes

                cache_state['large_file_systems'][self.uuid] = LargeFileSystemCache(
                    active_jobs=[self._job_id],
                    last_used_at=LfsCacheState.get_timestamp_now(),
                    size_bytes=lfs_size_bytes,
                    state='downloading',
                    storage_partition_uuid=storage_partition_to_use['uuid'],
                    uuid=self.uuid,
                )

                self._path_on_disk = f"{storage_partition_to_use['path']}/lfs/{self.uuid}/data"

            else:
                lfs_cache['active_jobs'].append(self._job_id)
                storage_partition = cache_state['storage_partitions'][lfs_cache['storage_partition_uuid']]
                self._path_on_disk = f"{storage_partition['path']}/lfs/{self.uuid}/data"

                if lfs_cache['state'] == 'ready':
                    return
                else:
                    lfs_is_already_downloading = True

        # TODO: Come up with better status reporting such that the progress values below make sense
        if lfs_is_already_downloading:
            self._send_status_update(StatusUpdate(
                progress=30,
                log_message=f'Waiting for Large File System "{self.uuid}" to be ready...',
            ))
            self._wait_for_lfs_to_be_ready()
            self._send_status_update(StatusUpdate(progress=33, log_message=f'Large File System "{self.uuid}" ready.'))
        else:
            self._send_status_update(StatusUpdate(
                progress=30,
                log_message=f'Downloading Large File System "{self.uuid}"...',
            ))
            self._download_and_unzip()
            self._send_status_update(StatusUpdate(
                progress=33,
                log_message=f'Large File System "{self.uuid}" downloaded.',
            ))
            with LfsCacheState() as cache_state:
                cache_state['large_file_systems'][self.uuid]['state'] = 'ready'

    def detach(self) -> None:
        if not self._is_initialized:
            return

        with LfsCacheState() as cache_state:
            lfs_cache = cache_state['large_file_systems'][self.uuid]
            lfs_cache['last_used_at'] = LfsCacheState.get_timestamp_now()
            lfs_cache['active_jobs'] = [job_id for job_id in lfs_cache['active_jobs'] if job_id != self._job_id]

        self._path_on_disk = None

    def _wait_for_lfs_to_be_ready(self) -> None:
        # Timeout after 15 min
        for _ in range(180):
            time.sleep(5)
            with LfsCacheState() as cache_state:
                if cache_state['large_file_systems'][self.uuid]['state'] == 'ready':
                    return

        raise LargeFileSystemError(f'Waiting for Large File System "{self.uuid}" downloading timed out')

    def _download_and_unzip(self) -> None:
        s3_lfs_bucket_name = os.environ.get('BIOLIB_S3_LFS_BUCKET_NAME')

        lfs_size_bytes = self._lfs_mapping['size_bytes']

        tmp_storage_dir: Optional[str] = None
        for path in LfsCacheState.get_tmp_storage_paths():
            disk_usage = shutil.disk_usage(path)
            if lfs_size_bytes < disk_usage.free:
                tmp_storage_dir = path

        if tmp_storage_dir is None:
            raise LargeFileSystemError('No temporary storage available for downloading Large File System')

        s3_data_zip_uri = f's3://{s3_lfs_bucket_name}/lfs/versions/{self.uuid}/data.zip'
        tmp_data_zip_path = f'{tmp_storage_dir}/lfs-{self.uuid}-data.zip'

        download_result = subprocess.run(
            ['s5cmd', 'cp', s3_data_zip_uri, tmp_data_zip_path],
            check=False,
            capture_output=True,
        )

        if download_result.returncode != 0:
            raise LargeFileSystemError(
                f'Failed to download Large File System data.zip: {download_result.stderr.decode()}'
            )

        with zipfile.ZipFile(tmp_data_zip_path, 'r') as zip_ref:
            zip_ref.extractall(self._path_on_disk)

        os.remove(tmp_data_zip_path)
