import datetime
import re

import dateutil.parser

from typing import Optional, List, Union

from imecilabt_utils.utils import any_to_bool


class SlaveInfo:
    def __init__(self,
                 version: str,  # called deployment_environment in version 2
                 slave_hostname: str,
                 slave_instance_id: Optional[str],  # Optional for backward compatibility
                 cluster_id: Union[int, str],

                 gpu_models: List[str],
                 cpu_models: List[str],

                 worker_count: int,
                 system_memory_mb: int,
                 gpu_count: int,
                 cpu_count: int,

                 worker_inuse: int,
                 system_memory_inuse_mb: int,
                 gpu_inuse: int,
                 cpu_inuse: int,

                 cuda_version_major: int,
                 cuda_version_full: str,

                 last_update: Optional[datetime.datetime] = None,
                 comment: Optional[str] = None,
                 shutting_down: bool = False):
        self.version = version  # called deployment_environment in version 2
        self.slave_hostname = slave_hostname
        self.slave_instance_id = str(slave_instance_id) if slave_instance_id is not None else None
        self.cluster_id = int(cluster_id)

        self.gpu_models = gpu_models
        self.cpu_models = cpu_models

        # These names should have been better, but... backwards compatibility... and hassle to change everywhere...
        self.worker_count = worker_count  # This should have been named worker_total.
        self.system_memory_mb = system_memory_mb  # This should have been called memory_acquired_mb
        self.gpu_count = gpu_count  # This should have been called gpu_acquired
        self.cpu_count = cpu_count  # This should have been called cpu_acquired

        self.worker_inuse = worker_inuse
        self.system_memory_inuse_mb = system_memory_inuse_mb  # This should have been called memory_inuse_mb
        self.gpu_inuse = gpu_inuse
        self.cpu_inuse = cpu_inuse

        self.cuda_version_major = cuda_version_major if cuda_version_major else SlaveInfo.extract_major_cuda_version(
            cuda_version_full)
        self.cuda_version_full = cuda_version_full
        assert self.cuda_version_full is None \
               or self.cuda_version_major == SlaveInfo.extract_major_cuda_version(self.cuda_version_full), \
            "cuda_version_full={} cuda_version_major={} extr={}".format(
                self.cuda_version_full, self.cuda_version_major,
                SlaveInfo.extract_major_cuda_version(self.cuda_version_full))

        self.last_update = last_update
        self.comment = comment

        self.shutting_down = shutting_down

        # No naive datetimes
        assert self.last_update is None or self.last_update.tzinfo is not None

    @classmethod
    def extract_major_cuda_version(cls, full_version: Optional[str]) -> Optional[int]:
        if not full_version:
            return None
        version_pattern = re.compile(r'^([0-9]+)\.[0-9.]+$')
        match_version = version_pattern.match(full_version)
        if match_version:
            return int(match_version.group(1))
        else:
            return None

    # forward compatible with new name for version
    @property
    def deployment_environment(self):
        return self.version

    def to_dict(self, add_available=False) -> dict:
        res = dict()
        res['version'] = self.version
        res['slave_hostname'] = self.slave_hostname
        res['slave_instance_id'] = self.slave_instance_id
        res['cluster_id'] = self.cluster_id
        res['gpu_models'] = self.gpu_models
        res['cpu_models'] = self.cpu_models
        res['worker_count'] = self.worker_count
        res['system_memory_mb'] = self.system_memory_mb
        res['gpu_count'] = self.gpu_count
        res['cpu_count'] = self.cpu_count
        res['worker_inuse'] = self.worker_inuse
        res['system_memory_inuse_mb'] = self.system_memory_inuse_mb
        res['gpu_inuse'] = self.gpu_inuse
        res['cpu_inuse'] = self.cpu_inuse
        res['cuda_version_major'] = self.cuda_version_major
        res['cuda_version_full'] = self.cuda_version_full
        if self.last_update:
            assert self.last_update is None or self.last_update.tzinfo is not None
            res['last_update'] = self.last_update.isoformat()
        if self.comment:
            res['comment'] = self.comment
        res['shutting_down'] = self.shutting_down

        if add_available:
            try:
                res['worker_available'] = self.worker_count - self.worker_inuse
                res['system_memory_available_mb'] = self.system_memory_mb - self.system_memory_inuse_mb
                res['cpu_available'] = self.cpu_count - self.cpu_inuse
                res['gpu_available'] = self.gpu_count - self.gpu_inuse
            except Exception:
                pass  # ignore any exception here, it's not important...

        return res

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            d['version'],
            d['slave_hostname'],
            d.get('slave_instance_id'),
            d['cluster_id'],
            d['gpu_models'],
            d.get('cpu_models', []),
            d['worker_count'],
            d['system_memory_mb'],
            d['gpu_count'],
            d['cpu_count'],
            d['worker_inuse'],
            d['system_memory_inuse_mb'],
            d['gpu_inuse'],
            d['cpu_inuse'],
            d.get('cuda_version_major'),
            d.get('cuda_version_full', 'unknown'),
            dateutil.parser.parse(d['last_update']) if 'last_update' in d and d['last_update'] else None,
            d.get('comment'),
            any_to_bool(d['shutting_down']) if 'shutting_down' in d else False
        )

    def make_copy(self) -> 'SlaveInfo':
        return SlaveInfo.from_dict(self.to_dict())
