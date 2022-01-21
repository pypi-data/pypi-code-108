import copy
import datetime
import json
import logging
import re
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

import dateutil.parser

from typing import Optional, List, Union, Dict

from stringcase import camelcase
from imecilabt_utils.urn_util import URN

from imecilabt.gpulab.model.slave_info import SlaveInfo

from imecilabt_utils.utils import datetime_now
from dataclass_dict_convert import dataclass_dict_convert, dump_rfc3339, dataclass_auto_type_check, \
    create_dict_of_dataclasses_from_convertor, create_dict_of_dataclasses_to_convertor, ignore_unknown_fields, \
    dataclass_multiline_repr


##
## Version 2 of SlaveInfo: SlaveInfo2
## This also adds ClusterInfo
## It also converts to and from the old SlaveInfo, and can detect if JSO is the old or new version
##
## Improvements:
##    - Metter naming
##    - More consist
##    - Always camelCase in JSON
##    - Added ClusterInfo and ResourceInfo
##    - Forced immutable ("frozen")
##    - Types enforced
##    - More strict: None (almost) nowhere allowed
##    - Uses python dataclasses (python 3.7+) + dataclasses_json library
##


# dataclasses_json.cfg.global_config.encoders[datetime.datetime] = dump_rfc3339
# dataclasses_json.cfg.global_config.decoders[datetime.datetime] = parse_rfc3339
# dataclasses_json.cfg.global_config.encoders[Optional[datetime.datetime]] = dump_rfc3339
# dataclasses_json.cfg.global_config.decoders[Optional[datetime.datetime]] = parse_rfc3339


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
class GpuModel:
    vendor: str
    name: str
    memory_mb: int


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass_auto_type_check
@dataclass(frozen=True)
class ResourceInfo:
    system_total: int
    acquired: int
    used: int
    available: int

    def __post_init__(self):
        assert self.acquired - self.used == self.available, \
            "acquired - used != available ({} - {} != {})".format(self.acquired, self.used, self.available)

    def add(self, other: 'ResourceInfo') -> 'ResourceInfo':
        """
        Merge resources from different slaves
        :param other:
        :return:
        """
        return ResourceInfo(
            system_total=self.system_total + other.system_total,
            acquired=self.acquired + other.acquired,
            used=self.used + other.used,
            available=self.available + other.available
        )

    def merge_instances(self, other: 'ResourceInfo') -> 'ResourceInfo':
        """
        Merge resources from different instance on the same slave
        :param other:
        :return:
        """
        assert self.system_total == other.system_total
        return ResourceInfo(
            system_total=self.system_total,
            acquired=self.acquired + other.acquired,
            used=self.used + other.used,
            available=self.available + other.available
        )


class SlaveDogAlarmCause(Enum):
    RESOURCE_DISAPPEARED = 'Resource(s) disappeared'
    JOB_REJECTED = 'Job rejected by slave'
    JOB_REQUEST_FAILED = 'Failure when slave requested job'
    SLAVE_LOOP_ERROR = 'Error in slave loop'
    PERIODIC_REPORT_ERROR = 'Error in periodic reporting'
    NET_TIMEOUT = 'Network call timeout'
    WATCHDOG_TIMEOUT_MINOR = 'Watchdog minor timeout (thread is slow)'
    WATCHDOG_TIMEOUT_MAJOR = 'Watchdog major timeout (thread is probably dead)'
    ALIVE_CHECK_FAILED = 'Watchdog alive check failed'
    ALIVE_CHECK_RECOVERED = 'Watchdog alive check recovered'
    WATCHDOG_MISMATCH = 'stop reported before start, or start after start'
    WATCHDOG_INTERNAL = 'Internal error in watchdog'


@dataclass_dict_convert(dict_letter_case=camelcase,
                        direct_fields=['alarm_counts', 'alarm_last_dates'],)
@dataclass_auto_type_check
@dataclass
class WatchdogStatistic:
    alive_now: bool = False
    last_alive_date: Optional[datetime.datetime] = field(default=None)
    alarm_counts: Dict[str, int] = field(default_factory=dict)
    # alarm_last_dates stores date as RFC3339 str, because dataclass_json can't handle that conversion
    # automatically inside dict.
    # TODO But we don't use dataclass_json anymore, so we can do this the right way now!
    alarm_last_dates: Dict[str, str] = field(default_factory=dict)
    emails_sent: int = 0

    def inc_alarm(self, cause: SlaveDogAlarmCause, now=datetime_now()) -> int:
        new_count = self.alarm_counts.get(cause.name, 0) + 1
        self.alarm_counts[cause.name] = new_count
        self.alarm_last_dates[cause.name] = dump_rfc3339(now)
        return new_count

    def make_copy(self) -> 'WatchdogStatistic':
        return WatchdogStatistic.from_dict(self.to_dict())


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass_auto_type_check
@dataclass(frozen=True)
class UploadThreadStatistic:
    cur_len: int
    cur_wait_s: float
    max_ever_len: int
    max_ever_wait_s: float
    total: int
    dropped: int
    retries: int

    def __str__(self) -> str:
        return "len={} wait={}s (max ever seen: len={} wait={}s) total={} dropped={} retries={}\n".format(
            self.cur_len, self.cur_wait_s, self.max_ever_len, self.max_ever_wait_s,
            self.total, self.dropped, self.retries)


@dataclass_dict_convert(dict_letter_case=camelcase,
                        custom_from_dict_convertors={
                            'upload_threads': create_dict_of_dataclasses_from_convertor(UploadThreadStatistic, 'upload_threads')
                        },
                        custom_to_dict_convertors={
                            'upload_threads': create_dict_of_dataclasses_to_convertor('upload_threads')
                        })
@dataclass_auto_type_check
@dataclass(frozen=True)
class SlaveStatistics:
    upload_threads: Dict[str, UploadThreadStatistic]
    watchdog: WatchdogStatistic



class SlaveInstanceBase(ABC):
    # Hard to require due to baseclasses, but it should have
    # should have fields :
    #    deployment_environment: str
    #    name: str
    #    instance_id: str
    #    pid: int
    #    cluster_id: int
    #
    #    aliases: List[str] = field(default_factory=list)
    #    comment: Optional[str] = None
    #    host: Optional[str] = None

    # this doesn't work:
    # @property
    # @abstractmethod
    # def deployment_environment(self) -> str:
    #     raise NotImplementedError()
    # 
    # @property
    # @abstractmethod
    # def name(self) -> str:
    #     raise NotImplementedError()
    # 
    # @property
    # @abstractmethod
    # def instance_id(self) -> str:
    #     raise NotImplementedError()
    # 
    # @property
    # @abstractmethod
    # def pid(self) -> int:
    #     raise NotImplementedError()
    # 
    # @property
    # @abstractmethod
    # def cluster_id(self) -> int:
    #     raise NotImplementedError()
    # 
    # @property
    # @abstractmethod
    # def aliases(self) -> List[str]:
    #     raise NotImplementedError()
    # 
    # @property
    # @abstractmethod
    # def comment(self) -> Optional[str]:
    #     raise NotImplementedError()
    # 
    # @property
    # @abstractmethod
    # def host(self) -> Optional[str]:
    #     raise NotImplementedError()

    @property
    def names(self) -> List[str]:
        return [self.name] + self.aliases

    def match_name(self, any_name: Optional[str]) -> bool:
        if not any_name:
            return False
        if self.name and any_name.lower() == self.name.lower():
            return True
        if self.host and any_name.lower() == self.host.lower():
            return True  # don't compare part before the dot: we can't assume this differs between slaves. (+ hostname might be IP!)
        if self.aliases and any(m for m in self.aliases if m.lower() == any_name.lower()):
            return True


STORAGE_PATH_LIMITED_CLUSTER_PROJECTS = 'PRIVATE_CLUSTER_PROJECTS'


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass_auto_type_check
@dataclass(frozen=True)
@dataclass_multiline_repr
class SlaveInfo2(SlaveInstanceBase):
    deployment_environment: str
    name: str
    instance_id: str
    pid: int
    cluster_id: int
    gpu_model: List[GpuModel]
    cpu_model: List[str]
    worker: ResourceInfo  # system_total is to be ignored here. It will be set the same as acquired.
    cpu_memory_mb: ResourceInfo
    # much more scheduling info will be needed for scheduler to use partial GPUs and their memory.
    # this will need to be added alter
    #   gpu_memory_mb_by_id: List[ResourceInfo]
    gpu: ResourceInfo
    cpu: ResourceInfo
    last_update: datetime.datetime
    shutting_down: bool
    cuda_version_full: str
    aliases: List[str] = field(default_factory=list)
    comment: Optional[str] = None
    host: Optional[str] = None
    cuda_version_major: int = None
    docker_disk_used_percent: float = -1.0
    accepting_jobs: bool = True
    statistics: Optional[SlaveStatistics] = None

    # A list of storage paths that are available on the cluster. (optional, where None means "unknown")
    storage_paths_available: Optional[List[str]] = None
    # A dict of storage aliases available on the cluster. (optional, where None means "unknown")
    storage_aliases_available: Optional[Dict] = None

    # A list of storage paths that are available on the cluster, but only for certain projects.
    # Projects are identified by URN. The special value "PRIVATE_CLUSTER_PROJECTS" is allowed instead of a URN.
    # It means: all projects that have access to the private cluster.
    # Each storage paths may only appear once. Either here as a key, or in storage_paths_available.
    storage_paths_available_project_limited: Optional[Dict[str, List[str]]] = None

    # For all the ResourceInfo (cpu_memory_mb, gpu and cpu),
    # the scheduler needs to know which jobs they include, and which not.
    #   empty list -> no jobs (so all resources should be free)
    #   None -> not reported
    active_job_uuids: Optional[List[str]] = None

    def __post_init__(self):
        # cuda_version_major uses a bit of a hack: SlaveInfo2 is frozen, so we need to bypass that

        assert self.cuda_version_full is None \
               or self.cuda_version_major is None \
               or self.cuda_version_major == SlaveInfo2.extract_major_cuda_version(self.cuda_version_full), \
            "cuda_version_full={} cuda_version_major={} extr={}".format(
                self.cuda_version_full, self.cuda_version_major,
                SlaveInfo2.extract_major_cuda_version(self.cuda_version_full))

        if self.cuda_version_full and not self.cuda_version_major:
            super().__setattr__('cuda_version_major', SlaveInfo2.extract_major_cuda_version(self.cuda_version_full))

    def matches_name(self, name: str) -> bool:
        """
        Check if the given name matches this SlaveInfo2's name or aliases.
        This also ignores all non-alphanum chars!
        :param name:
        :return:
        """
        norm_name = re.sub(r'[^a-z0-9]', '', name.lower())
        norm_self_name = re.sub(r'[^a-z0-9]', '', self.name.lower())
        if norm_name == norm_self_name:
            return True
        for alias in self.aliases:
            norm_alias = re.sub(r'[^a-z0-9]', '', alias.lower())
            if norm_name == norm_alias:
                return True
        return False


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

    def has_storage(self, storage_path: str):
        """
        This checks both storage_paths_available and storage_aliases_available.
        This does not work correctly with tmpfs or .ssh!
        :param storage_path:
        :return: whether the storage path is available on this slave.
        """
        def add_end_slash_ifneeded(dir: str):
            return dir + '/' if not dir.endswith('/') else dir

        storage_path = add_end_slash_ifneeded(storage_path)

        ## The code below is no longer used: we now assume that if a slave doesn't list storage, it doesn't have any.
        # if not self.storage_paths_available or self.storage_aliases_available is None:
        #     # We assume that if a slave reports its storage:
        #     #   - storage_paths_available should never be empty, all cluster should have a storage
        #     #   - storage_aliases_available should not be None. But it can be empty.
        #
        #     # Assumption doesn't hold: We don't know about storage, so we fall back to True
        #     # (Should never happen)
        #     logging.warning(f'No info is available about storage for {self.name} {self.instance_id}: \n{self}')
        #     return True

        for available in self.storage_paths_available:
            if storage_path.startswith(add_end_slash_ifneeded(available)):
                return True

        for available in self.storage_aliases_available.keys():
            if storage_path.startswith(add_end_slash_ifneeded(available)):
                return True

        return False

    def allows_storage(self, storage_path: str, project_urn: str):
        """
        This checks both storage_paths_available and storage_aliases_available.
        This does not work correctly with tmpfs or .ssh!
        :param storage_path:
        :param project_urn: the projects that wants to access the storage
        :return: whether the storage path is available on this slave, for the specified project.
        """
        def add_end_slash_ifneeded(dir: str):
            return dir + '/' if not dir.endswith('/') else dir

        storage_path = add_end_slash_ifneeded(storage_path)

        to_check = []
        for available in self.storage_paths_available:
            if storage_path.startswith(add_end_slash_ifneeded(available)):
                to_check.append(available)

        for available in self.storage_aliases_available.keys():
            if storage_path.startswith(add_end_slash_ifneeded(available)):
                to_check.append(available)
                to_check.append(self.storage_aliases_available[available])

        if not to_check:
            return False

        if self.storage_paths_available_project_limited:
            for s in to_check:
                s = add_end_slash_ifneeded(s)
                for available, projects in self.storage_paths_available_project_limited.items():
                    if s.startswith(add_end_slash_ifneeded(available)):
                        return URN(project_urn) in [URN(p) for p in projects]
        return True


    def make_copy(self) -> 'SlaveInfo2':
        return SlaveInfo2.from_dict(self.to_dict())

    def make_copy_with_added_usage(self, cpu_memory_mb: int, gpu: int, cpu: int,
                                   job_uuids: Optional[List[str]] = None, remove=False) -> 'SlaveInfo2':
        """
        Make a copy of the job, but modify the gpu, cpu and memory usage by adding to it

        :param cpu_memory_mb:
        :param gpu:
        :param cpu:
        :param job_uuids:
        :param remove: remove the usage instead of adding it
        :return:
        """
        if remove:
            cpu_memory_mb = -cpu_memory_mb
            cpu = -cpu
            gpu = -gpu
        if self.active_job_uuids is None:
            active_job_uuids = None
        else:
            if remove:
                active_job_uuids = list(set(self.active_job_uuids) - set(job_uuids if job_uuids else []))
            else:
                # add
                active_job_uuids = list(set(self.active_job_uuids + (job_uuids if job_uuids else [])))
        return SlaveInfo2(
            deployment_environment=self.deployment_environment,
            name=self.name,
            aliases=self.aliases,
            host=self.host,
            instance_id=self.instance_id,
            pid=self.pid,
            cluster_id=self.cluster_id,
            gpu_model=self.gpu_model,
            cpu_model=self.cpu_model,
            worker=ResourceInfo(
                system_total=self.worker.system_total,
                acquired=self.worker.acquired,
                used=self.worker.used,
                available=self.worker.available
            ),
            cpu_memory_mb=ResourceInfo(
                system_total=self.cpu_memory_mb.system_total,
                acquired=self.cpu_memory_mb.acquired,
                used=self.cpu_memory_mb.used + cpu_memory_mb,
                available=self.cpu_memory_mb.available - cpu_memory_mb
            ),
            gpu=ResourceInfo(
                system_total=self.gpu.system_total,
                acquired=self.gpu.acquired,
                used=self.gpu.used + gpu,
                available=self.gpu.available - gpu
            ),
            cpu=ResourceInfo(
                system_total=self.cpu.system_total,
                acquired=self.cpu.acquired,
                used=self.cpu.used + cpu,
                available=self.cpu.available - cpu
            ),
            cuda_version_full=self.cuda_version_full,
            cuda_version_major=self.cuda_version_major,
            last_update=self.last_update,
            comment=self.comment,
            shutting_down=self.shutting_down,
            docker_disk_used_percent=self.docker_disk_used_percent,
            accepting_jobs=self.accepting_jobs,
            statistics=self.statistics,
            storage_paths_available=self.storage_paths_available,
            storage_aliases_available=self.storage_aliases_available,
            storage_paths_available_project_limited=self.storage_paths_available_project_limited,
            active_job_uuids=active_job_uuids,
        )

    def make_copy_with_alt_last_update(self, new_last_update: datetime) -> 'SlaveInfo2':
        """
        Make a copy of the job, but modify last_update

        :param new_last_update
        :return:
        """
        assert new_last_update.tzinfo is not None
        return SlaveInfo2(
            deployment_environment=self.deployment_environment,
            name=self.name,
            aliases=self.aliases,
            host=self.host,
            instance_id=self.instance_id,
            pid=self.pid,
            cluster_id=self.cluster_id,
            gpu_model=self.gpu_model,
            cpu_model=self.cpu_model,
            worker=self.worker,
            cpu_memory_mb=self.cpu_memory_mb,
            gpu=self.gpu,
            cpu=self.cpu,
            cuda_version_full=self.cuda_version_full,
            cuda_version_major=self.cuda_version_major,
            last_update=new_last_update,
            comment=self.comment,
            shutting_down=self.shutting_down,
            docker_disk_used_percent=self.docker_disk_used_percent,
            accepting_jobs=self.accepting_jobs,
            statistics=self.statistics,
            storage_paths_available=self.storage_paths_available,
            storage_aliases_available=self.storage_aliases_available,
            storage_paths_available_project_limited=self.storage_paths_available_project_limited,
            active_job_uuids=self.active_job_uuids,
        )

    def merge_instances(self, other: 'SlaveInfo2') -> 'SlaveInfo2':
        """
        Make new SlaveInfo2 that is a merger of both SlaveInfo's.

        This should only be used to merge info from multiple instances of the same slave

        This is probably only useful if you want to have the resource totals
        """
        assert other.deployment_environment == self.deployment_environment
        assert other.cluster_id == self.cluster_id
        assert other.name == self.name

        preferred = self if self.accepting_jobs and not self.shutting_down else other

        return SlaveInfo2(
            deployment_environment=self.deployment_environment,
            name=self.name,
            aliases=preferred.aliases,
            host=preferred.host,
            instance_id=preferred.instance_id,
            pid=preferred.pid,
            cluster_id=self.cluster_id,
            gpu_model=preferred.gpu_model,
            cpu_model=preferred.cpu_model,
            worker=self.worker.merge_instances(other.worker),
            cpu_memory_mb=self.cpu_memory_mb.merge_instances(other.cpu_memory_mb),
            gpu=self.gpu.merge_instances(other.gpu),
            cpu=self.cpu.merge_instances(other.cpu),
            cuda_version_full=preferred.cuda_version_full,
            cuda_version_major=preferred.cuda_version_major,
            last_update=max(self.last_update, other.last_update),
            comment=preferred.comment,
            shutting_down=preferred.shutting_down,
            docker_disk_used_percent=preferred.docker_disk_used_percent,
            accepting_jobs=preferred.accepting_jobs,
            statistics=preferred.statistics,
            storage_paths_available=preferred.storage_paths_available,
            storage_aliases_available=preferred.storage_aliases_available,
            storage_paths_available_project_limited=self.storage_paths_available_project_limited,
            active_job_uuids=list(set(self.active_job_uuids + other.active_job_uuids)),
        )

    @classmethod
    def from_any_json(cls, json_str: str) -> 'SlaveInfo2':
        return cls.from_any_dict(json.loads(json_str))

    @classmethod
    def from_any_dict(cls, d: dict) -> 'SlaveInfo2':
        """
        :param d: a dict containing either SlaveInfo or SlaveInfo2
        :return: a SlaveInfo2
        """
        if 'gpu_models' in d.keys() and 'system_memory_inuse_mb' in d.keys():
            return cls.from_slave_info_1(SlaveInfo.from_dict(d))
        if 'gpuModel' in d.keys() and 'instanceId' in d.keys():
            # SlaveInfo2 had a few changes along the way, which we will automatically convert for now (to be removed later!)
            if 'memoryMb' in d.keys() and 'cpuMemoryMb' not in d.keys():
                d = copy.deepcopy(d)  # copy
                d['cpuMemoryMb'] = d['memoryMb']
                del d['memoryMb']
            if 'hostname' in d.keys() and 'name' not in d.keys():
                d = copy.deepcopy(d)  # copy
                d['name'] = d['hostname']
                d['host'] = d['hostname']
                del d['hostname']
            if 'gpuModel' in d.keys() and len(d['gpuModel']) > 0 and isinstance(d['gpuModel'][0], str):
                d = copy.deepcopy(d)  # copy
                newModels = []
                for modelName in d['gpuModel']:
                    newModels.append({"vendor": "nvidia", "name": modelName, "memoryMb": -1})
                d['gpuModel'] = newModels
            if not 'aliases' in d:
                d['aliases'] = []
            return cls.from_dict(d, on_unknown_field_override=ignore_unknown_fields)
        raise ValueError('Neither SlaveInfo or SlaveInfo2 format in {}'.format(d))

    @classmethod
    def from_slave_info_1(cls, slave_info_1: SlaveInfo) -> 'SlaveInfo2':
        assert slave_info_1.last_update is None or slave_info_1.last_update.tzinfo is not None
        return cls(
            deployment_environment=slave_info_1.version,
            name=slave_info_1.slave_hostname,
            aliases=[],
            host=slave_info_1.slave_hostname,
            instance_id=slave_info_1.slave_instance_id,
            pid=-1,
            cluster_id=slave_info_1.cluster_id,
            gpu_model=[GpuModel(vendor='nvidia', name=m, memory_mb=0) for m in slave_info_1.gpu_models],
            cpu_model=slave_info_1.cpu_models,
            worker=ResourceInfo(
                system_total=slave_info_1.worker_count,
                acquired=slave_info_1.worker_count,
                used=slave_info_1.worker_inuse,
                available=slave_info_1.worker_count - slave_info_1.worker_inuse
            ),
            cpu_memory_mb=ResourceInfo(
                system_total=slave_info_1.system_memory_mb,
                acquired=slave_info_1.system_memory_mb,
                used=slave_info_1.system_memory_inuse_mb,
                available=slave_info_1.system_memory_mb - slave_info_1.system_memory_inuse_mb
            ),
            gpu=ResourceInfo(
                system_total=slave_info_1.gpu_count,
                acquired=slave_info_1.gpu_count,
                used=slave_info_1.gpu_inuse,
                available=slave_info_1.gpu_count - slave_info_1.gpu_inuse
            ),
            cpu=ResourceInfo(
                system_total=slave_info_1.cpu_count,
                acquired=slave_info_1.cpu_count,
                used=slave_info_1.cpu_inuse,
                available=slave_info_1.cpu_count - slave_info_1.cpu_inuse
            ),
            cuda_version_full=slave_info_1.cuda_version_full,
            last_update=slave_info_1.last_update if slave_info_1.last_update else datetime.datetime.fromtimestamp(0).astimezone(datetime.timezone.utc),  # 1 jan 1970 instead of None
            comment=slave_info_1.comment,
            shutting_down=slave_info_1.shutting_down,
            docker_disk_used_percent=-1.0,
            accepting_jobs=True,
            statistics=None,
        )

    def to_slave_info_1(self) -> 'SlaveInfo':
        return SlaveInfo(
            version=self.deployment_environment,
            slave_hostname=self.name,
            slave_instance_id=self.instance_id,
            cluster_id=self.cluster_id,
            gpu_models=[m.name for m in self.gpu_model],
            cpu_models=self.cpu_model,
            worker_count=self.worker.acquired,
            system_memory_mb=self.cpu_memory_mb.acquired,
            gpu_count=self.gpu.acquired,
            cpu_count=self.cpu.acquired,
            worker_inuse=self.worker.used,
            system_memory_inuse_mb=self.cpu_memory_mb.used,
            gpu_inuse=self.gpu.used,
            cpu_inuse=self.cpu.used,
            cuda_version_major=self.cuda_version_major,
            cuda_version_full=self.cuda_version_full,
            comment=self.comment,
            shutting_down=self.shutting_down,
            last_update=self.last_update
        )

    @staticmethod
    def from_dict_list(s_dict_lst: List[Dict], on_unknown_field_override=None) -> List['SlaveInfo2']:
        # Note: normally, you can do this with Job.schema().load(s_dict_lst, many=True)
        #       that seems to ignore global decoders however
        #       (which is not a problem here, but we also avoid it here for consistency)
        return [SlaveInfo2.from_dict(d, on_unknown_field_override=on_unknown_field_override) for d in s_dict_lst]


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass_auto_type_check
@dataclass(frozen=True)
class ClusterInfo:
    deployment_environment: str
    cluster_id: int
    comment: str
    is_private: bool
    slave_count: int = 0
    gpu_model: List[GpuModel] = field(default_factory=list)
    worker: ResourceInfo = ResourceInfo(0, 0, 0, 0)
    cpu_memory_mb: ResourceInfo = ResourceInfo(0, 0, 0, 0)
    gpu: ResourceInfo = ResourceInfo(0, 0, 0, 0)
    cpu: ResourceInfo = ResourceInfo(0, 0, 0, 0)

    # Does the user requesting the info have access? (optional, None when not relevant)
    have_access: Optional[bool] = None

    # A list of projects that have access (optional, None means public access)
    allowed_projects: Optional[List[str]] = None

    # A list of storage paths that are available on the cluster. (optional, where None means "unknown")
    storage_paths_available: Optional[List[str]] = None
    # A dict of storage aliases available on the cluster. (optional, where None means "unknown")
    storage_aliases_available: Optional[Dict] = None

    def make_copy(self) -> 'ClusterInfo':
        return ClusterInfo.from_dict(self.to_dict())

    @staticmethod
    def _merge_storage_paths(
            storage_paths_available_1: Optional[List[str]],
            storage_paths_available_2: Optional[List[str]]) -> Optional[List[str]]:
        if storage_paths_available_1 is None and storage_paths_available_2 is None:
            return None
        if storage_paths_available_1 is None or storage_paths_available_2 is None:
            return storage_paths_available_1 if storage_paths_available_1 is not None else storage_paths_available_2
        assert storage_paths_available_1 is not None
        assert storage_paths_available_2 is not None
        return list(set(storage_paths_available_1).union(set(storage_paths_available_2)))

    @staticmethod
    def _merge_storage_aliases(
            storage_aliases_available_1: Optional[Dict[str, str]],
            storage_aliases_available_2: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if storage_aliases_available_1 is None and storage_aliases_available_2 is None:
            return None
        if storage_aliases_available_1 is None or storage_aliases_available_2 is None:
            return storage_aliases_available_1 if storage_aliases_available_1 is not None else storage_aliases_available_2
        assert storage_aliases_available_1 is not None
        assert storage_aliases_available_2 is not None
        res = dict(storage_aliases_available_1)
        res.update(storage_aliases_available_2)
        return res

    def add(self, slave_info: SlaveInfo2) -> 'ClusterInfo':
        gpu_model = set(self.gpu_model)
        gpu_model.update(slave_info.gpu_model)
        return ClusterInfo(
            deployment_environment=self.deployment_environment,
            cluster_id=self.cluster_id,
            comment=self.comment,
            is_private=self.is_private,
            slave_count=self.slave_count+1,
            gpu_model=list(gpu_model),
            worker=self.worker.add(slave_info.worker),
            cpu_memory_mb=self.cpu_memory_mb.add(slave_info.cpu_memory_mb),
            gpu=self.gpu.add(slave_info.gpu),
            cpu=self.cpu.add(slave_info.cpu),
            have_access=self.have_access,
            allowed_projects=self.allowed_projects,
            storage_paths_available=ClusterInfo._merge_storage_paths(
                self.storage_paths_available,
                slave_info.storage_paths_available
            ),
            storage_aliases_available=ClusterInfo._merge_storage_aliases(
                self.storage_aliases_available,
                slave_info.storage_aliases_available
            ),
        )

    @staticmethod
    def from_dict_list(c_dict_lst: List[Dict]) -> List['ClusterInfo']:
        # Note: normally, you can do this with Job.schema().load(c_dict_lst, many=True)
        #       that seems to ignore global decoders however
        #       (which is not a problem here, but we also avoid it here for consistency)
        return [ClusterInfo.from_dict(d) for d in c_dict_lst]
