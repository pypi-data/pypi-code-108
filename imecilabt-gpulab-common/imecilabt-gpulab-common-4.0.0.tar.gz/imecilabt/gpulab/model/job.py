import datetime
import json
import re
from enum import Enum
from typing import Dict, Optional, Any, List, Union, Callable

import dateutil.parser

from imecilabt_utils.urn_util import URN, always_optional_urn
from imecilabt_utils.validation_utils import is_valid_uuid4, is_valid_uuid
from imecilabt.gpulab.util.convert_utils import urn_to_user_mini_id, urn_to_name, urn_to_auth

NVDATA_JOBDEFINITION = "jobDefinition"

DOCKER_IMAGE_USERPASS_PATTERN = re.compile('([a-zA-Z0-9_+-]*):([^@]*)@([^@]*)')

# Name components may contain lowercase letters, digits and separators.
# A separator is defined as a period, one or two underscores, or one or more dashes.
# A name component may not start or end with a separator.
# A tag name must be valid ASCII and may contain lowercase and uppercase letters,
# digits, underscores, periods and dashes. A tag name may not start with a period
# or a dash and may contain a maximum of 128 characters.
DOCKER_IMAGE_AND_TAG_PATTERN = re.compile('(.*):([a-zA-Z0-9_][a-zA-Z0-9_.-]*)')


class JobState(Enum):
    ONHOLD = 'On Hold'             # On hold, not planned to run at this time (not in queue)
    QUEUED = 'Queued'              # Available to run, waiting in queue
    ASSIGNED = 'Assigned'          # Assigned to a specific node by the scheduler, but not yet "picked up" by that node.
    TRANSFER = 'Transferring'      # (deprecated) Being sent to worker (replaced by ASSIGNED)
    STARTING = 'Starting'          # Received by worker, setup in progress, not yet running
    RUNNING = 'Running'            # Running on worker
    CANCELLED = 'Cancelled'        # Cancelled during run (due to user request)
    FINISHED = 'Finished'          # Run completed
    DELETED = 'Deleted'            # Marked as deleted. This causes it to be ignored in "queue" view
    FAILED = 'Failed'              # Failure due to job definition problem, system problems, or other.


def _parse_opt_date(opt_date_str: Optional[str]) -> Optional[datetime.datetime]:
    return dateutil.parser.parse(opt_date_str) if opt_date_str else None


def _ensure_opt_date(opt_date_any: Optional[Union[str, datetime.datetime]]) -> Optional[datetime.datetime]:
    if opt_date_any is None:
        return None
    if isinstance(opt_date_any, datetime.datetime):
        return opt_date_any
    return dateutil.parser.parse(opt_date_any)


def _opt_date_str(opt_date: Optional[datetime.datetime]) -> Optional[str]:
    return opt_date.isoformat() if opt_date else None


def _int_or_none(val: Optional[Any]) -> Optional[int]:
    return int(val) if val is not None else None


class JobPortMapping:
    def __init__(self,
                 container_port: Optional[int] = None,
                 host_port: Optional[int] = None,
                 host_ip: Optional[str] = None,
                 ):
        try:
            self.container_port = int(container_port) if container_port else None
        except ValueError:
            # might be str like "8888/tcp" instead of int, when used in run_details.
            self.container_port = str(container_port)
        self.host_port = int(host_port) if host_port else None
        self.host_ip = str(host_ip) if host_ip else None

    def to_dict(self, strip=True, snake_case=True) -> dict:
        res = dict()
        if snake_case:
            res['container_port'] = self.container_port
            res['host_port'] = self.host_port
            res['host_ip'] = self.host_ip
        else:
            res['containerPort'] = self.container_port
            res['hostPort'] = self.host_port
            res['hostIp'] = self.host_ip

        if strip:
            empty = []
            for key, value in res.items():
                if value is None:
                    empty.append(key)
            for key in empty:
                del res[key]

        return res

    @classmethod
    def from_dict(cls, d: dict) -> 'JobPortMapping':
        return cls(
            container_port=d.get('containerPort', d.get('container_port')),
            host_port=d.get('hostPort', d.get('host_port')),
            host_ip=d.get('hostIp', d.get('host_ip')),
        )

    def __str__(self) -> str:
        return json.dumps(self.to_dict())

    def __repr__(self) -> str:
        return 'JobPortMapping(container_port={}, host_port={}, host_ip={})' \
            .format(self.container_port, self.host_port, self.host_ip)

    def make_copy(self) -> 'JobPortMapping':
        return JobPortMapping.from_dict(self.to_dict())



class JobRunDetails:
    def __init__(self,
                 slave_hostname: Optional[str] = None,
                 slave_dns_name: Optional[str] = None,
                 slave_instance_id: Optional[str] = None,
                 slave_instance_pid: Optional[int] = None,
                 gpu_ids: Optional[List[int]] = None,
                 cpu_ids: Optional[List[int]] = None,
                 memory: Optional[str] = None,
                 worker_id: Optional[int] = None,
                 cluster_id: Optional[int] = None,
                 port_mappings: Optional[Union[List[Dict], List[JobPortMapping]]] = None,
                 start_date: Optional[datetime.datetime] = None,
                 end_date: Optional[datetime.datetime] = None,
                 deadline_date: Optional[datetime.datetime] = None,
                 notify_date: Optional[datetime.datetime] = None,
                 ssh_username: Optional[str] = None,
                 ssh_proxy_username: Optional[str] = None,
                 ssh_proxy_host: Optional[str] = None,
                 ssh_proxy_port: Optional[int] = None,
                 summary_statistics: dict = None,
                 gpu_fixed_info: dict = None,
                 ):
        self.slave_hostname = slave_hostname
        self.slave_dns_name = slave_dns_name
        self.slave_instance_id = str(slave_instance_id) if slave_instance_id else None
        self.slave_instance_pid = int(slave_instance_pid) if slave_instance_pid else None
        self.gpu_ids = [int(i) for i in gpu_ids] if gpu_ids else None
        self.cpu_ids = [int(i) for i in cpu_ids] if cpu_ids else None
        self.memory = str(memory) if memory else None
        self.worker_id = int(worker_id) if worker_id else None
        self.cluster_id = int(cluster_id) if cluster_id else None
        self.start_date = _ensure_opt_date(start_date)
        self.end_date = _ensure_opt_date(end_date)
        self.deadline_date = _ensure_opt_date(deadline_date)
        self.notify_date = _ensure_opt_date(notify_date)
        self.ssh_username = ssh_username
        self.ssh_proxy_username = ssh_proxy_username
        self.ssh_proxy_host = ssh_proxy_host
        self.ssh_proxy_port = int(ssh_proxy_port) if ssh_proxy_port else None
        self.summary_statistics = summary_statistics if summary_statistics is not None else {}
        self.gpu_fixed_info = gpu_fixed_info if gpu_fixed_info is not None else {}

        if not port_mappings:  # None or empty list
            self.port_mappings = []
        elif isinstance(port_mappings[0], JobPortMapping):
            self.port_mappings = list(port_mappings)
        else:  # assume it's a dict like
            self.port_mappings = [JobPortMapping.from_dict(d) for d in port_mappings]

    # These class attributes define the fields that can be changed with api.update_job_run_details_field
    # No other fields should ever be changed after init.
    # TODO is there a cleaner way? (Enum looks too boiler plate for this case)
    FIELDNAME_PORT_MAPPINGS = 'portMappings'
    FIELDNAME_GPU_INFO = 'gpuFixedInfo'
    FIELDNAME_END_DATE = 'endDate'
    FIELDNAME_SUMMARY_STATISTICS = 'summaryStatistics'
    UPDATABLE_FIELDS = \
        (FIELDNAME_PORT_MAPPINGS, FIELDNAME_GPU_INFO, FIELDNAME_END_DATE, FIELDNAME_SUMMARY_STATISTICS)

    @classmethod
    def is_update_field(cls, json_field_name: str):
        return json_field_name in cls.UPDATABLE_FIELDS

    @property
    def memory_byte(self) -> int:
        # Note: python3 has no size limit for int

        # from docker docs:
        # a positive integer, followed by a suffix of b, k, m, g, to indicate bytes, kilobytes, megabytes, or gigabytes.
        #
        # -> examples show this is in multiples of 1000, not 1024
        if not self.memory:
            return 0
        match = re.match(r'^([0-9.]+)g$', self.memory)
        if match:
            return int(match.group(1)) * 1000 * 1000 * 1000
        match = re.match(r'^([0-9.]+)m$', self.memory)
        if match:
            return int(match.group(1)) * 1000 * 1000
        match = re.match(r'^([0-9.]+)k$', self.memory)
        if match:
            return int(match.group(1)) * 1000
        match = re.match(r'^([0-9.]+)b$', self.memory)
        if match:
            return int(match.group(1))
        # if not suffix, it seems we assumed "m" before
        assert re.match(r'^([0-9.]+)$', self.memory), 'Unhandled memory field value: "{}"'.format(self.memory)
        return int(self.memory) * 1000 * 1000

    @property
    def memory_mb(self) -> int:
        # while MB is sometimes 1000^2 instead of 1024^2 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return self.memory_byte // (1024 * 1024)

    @property
    def memory_gb(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return self.memory_byte // (1024 * 1024 * 1024)

    def get_duration(self) -> Optional[datetime.timedelta]:
        start = self.start_date
        end = self.end_date
        if start is None:
            return None
        if end is None:
            end = datetime.datetime.now(datetime.timezone.utc)
        assert end.tzinfo is not None, 'end is naive "{}"'.format(end)
        assert start.tzinfo is not None, 'start is naive "{}"'.format(start)
        return end - start

    def sanitized_copy(self, logged_in=True) -> 'JobRunDetails':
        return JobRunDetails(
            slave_hostname=self.slave_hostname if logged_in else None,
            slave_dns_name=self.slave_dns_name if logged_in else None,
            slave_instance_id=self.slave_instance_id if logged_in else None,
            slave_instance_pid=self.slave_instance_pid if logged_in else None,
            gpu_ids=None,
            cpu_ids=None,
            memory=None,
            worker_id=None,
            cluster_id=self.cluster_id,
            port_mappings=None,
            start_date=self.start_date,
            end_date=self.end_date,
            deadline_date=self.deadline_date,
            notify_date=self.notify_date if logged_in else None,
            ssh_username=None,
            ssh_proxy_username=None,
            ssh_proxy_host=None,
            ssh_proxy_port=None,
            summary_statistics=self.summary_statistics if logged_in else None,
            gpu_fixed_info=None,
        )

    def to_dict(self, strip=True) -> dict:
        res = dict()
        res['slaveHostname'] = self.slave_hostname
        res['slaveDnsName'] = self.slave_dns_name
        res['slaveInstanceId'] = self.slave_instance_id
        res['slaveInstancePID'] = self.slave_instance_pid
        res['gpuIds'] = self.gpu_ids
        res['cpuIds'] = self.cpu_ids
        res['memory'] = self.memory
        res['workerId'] = self.worker_id
        res['clusterId'] = self.cluster_id
        res['portMappings'] = [pm.to_dict(strip=strip, snake_case=True) for pm in self.port_mappings] if self.port_mappings else None
        res['startDate'] = _opt_date_str(self.start_date)
        res['endDate'] = _opt_date_str(self.end_date)
        res['deadlineDate'] = _opt_date_str(self.deadline_date)
        res['notifyDate'] = _opt_date_str(self.notify_date)
        res['sshUsername'] = self.ssh_username
        res['sshProxyUsername'] = self.ssh_proxy_username
        res['sshProxyHost'] = self.ssh_proxy_host
        res['sshProxyPort'] = self.ssh_proxy_port
        res['summaryStatistics'] = self.summary_statistics
        res['gpuFixedInfo'] = self.gpu_fixed_info

        if strip:
            empty = []
            for key,value in res.items():
                if not value:
                    empty.append(key)
            for key in empty:
                del res[key]

        return res

    @classmethod
    def from_dict(cls, d: dict) -> 'JobRunDetails':
        return cls(
            slave_hostname=d.get('slaveHostname'),
            slave_dns_name=d.get('slaveDnsName'),
            slave_instance_id=d.get('slaveInstanceId'),
            slave_instance_pid=d.get('slaveInstancePID'),
            gpu_ids=d.get('gpuIds'),
            cpu_ids=d.get('cpuIds'),
            memory=d.get('memory'),
            worker_id=d.get('workerId'),
            cluster_id=d.get('clusterId'),
            port_mappings=d.get('portMappings'),
            start_date=_parse_opt_date(d.get('startDate')),
            end_date=_parse_opt_date(d.get('endDate')),
            deadline_date=_parse_opt_date(d.get('deadlineDate')),
            notify_date=_parse_opt_date(d.get('notifyDate')),
            ssh_username=d.get('sshUsername'),
            ssh_proxy_username=d.get('sshProxyUsername'),
            ssh_proxy_host=d.get('sshProxyHost'),
            ssh_proxy_port=d.get('sshProxyPort'),
            summary_statistics=d.get('summaryStatistics'),
            gpu_fixed_info=d.get('gpuFixedInfo'),
        )

    def make_copy(self) -> 'JobRunDetails':
        return JobRunDetails.from_dict(self.to_dict())

    def is_empty(self) -> bool:
        return len(self.to_dict(strip=True)) == 0

    def is_default(self) -> bool:
        return len(self.to_dict(strip=True)) == 0


class JobSchedulerInfo:
    def __init__(self,
                 within_max_simultaneous_jobs: Optional[bool] = None,
                 assigned_slave_hostname: Optional[str] = None,
                 assigned_instance_id: Optional[str] = None,
                 assigned_cluster_id: Optional[int] = None,
                 queued_explanations: Optional[List[str]] = None,
                 assigned_time: Optional[datetime.datetime] = None
                 ):
        self.within_max_simultaneous_jobs = within_max_simultaneous_jobs  # False if running this Job would result in to many simultaneous jobs
        self.queued_explanations = list(queued_explanations) if queued_explanations else []  # why is this job not running yet?
        self.assigned_slave_hostname = assigned_slave_hostname
        self.assigned_instance_id = assigned_instance_id
        self.assigned_cluster_id = int(assigned_cluster_id) if assigned_cluster_id else None
        self.assigned_time = assigned_time
        assert assigned_time is None or assigned_time.tzinfo is not None

    def sanitized_copy(self, logged_in=True) -> 'JobSchedulerInfo':
        return JobSchedulerInfo(
            within_max_simultaneous_jobs=self.within_max_simultaneous_jobs,
            queued_explanations=self.queued_explanations,
            assigned_slave_hostname=self.assigned_slave_hostname,
            assigned_instance_id=self.assigned_instance_id,
            assigned_cluster_id=self.assigned_cluster_id,
            assigned_time=self.assigned_time,
        )

    def to_dict(self, strip=True) -> dict:
        res = dict()
        res['within_max_simultaneous_jobs'] = bool(self.within_max_simultaneous_jobs) if self.within_max_simultaneous_jobs is not None else None
        res['queued_explanations'] = self.queued_explanations if self.queued_explanations else []
        res['assigned_slave_hostname'] = self.assigned_slave_hostname
        res['assigned_instance_id'] = self.assigned_instance_id
        res['assigned_cluster_id'] = self.assigned_cluster_id
        res['assigned_time'] = _opt_date_str(self.assigned_time)

        if strip:
            empty = []
            for key,value in res.items():
                if value is None:
                    empty.append(key)
            for key in empty:
                del res[key]

        return res

    @classmethod
    def from_dict(cls, d: dict) -> 'JobSchedulerInfo':
        return cls(
            within_max_simultaneous_jobs=d.get('within_max_simultaneous_jobs'),
            queued_explanations=d.get('queued_explanations'),
            assigned_slave_hostname=d.get('assigned_slave_hostname'),
            assigned_instance_id=d.get('assigned_instance_id'),
            assigned_cluster_id=d.get('assigned_cluster_id'),
            assigned_time=_parse_opt_date(d.get('assigned_time')),
        )

    def make_copy(self) -> 'JobSchedulerInfo':
        return JobSchedulerInfo.from_dict(self.to_dict())

    def is_empty(self) -> bool:
        return not \
            (self.within_max_simultaneous_jobs or
             self.queued_explanations or
             self.assigned_slave_hostname or
             self.assigned_instance_id or
             self.assigned_cluster_id or
             self.assigned_time)

    def is_default(self) -> bool:
        return self.is_empty()


class NVDockerDataResources:
    def __init__(self,
                 system_memory: Optional[int] = None,
                 cpu_cores: Optional[int] = None,
                 gpus: Optional[int] = None,
                 gpu_model: Optional[Union[List[str], str]] = None,
                 min_cuda_version: Optional[int] = None,
                 ):
        self.system_memory = int(system_memory) if system_memory else 0  # in MB
        self.cpu_cores = int(cpu_cores) if cpu_cores else 0
        self.gpus = int(gpus) if gpus else 0
        self.min_cuda_version = int(min_cuda_version) if min_cuda_version else None

        if not gpu_model:  # None, or empty list
            self.gpu_model = None
        elif isinstance(gpu_model, str):
            self.gpu_model = str(gpu_model)
        else:  # assume it's a list of str
            self.gpu_model = [str(m) for m in gpu_model]

    @property
    def system_memory_mb(self) -> int:
        # while MB is sometimes 1000^2 instead of 1024^2 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        if not self.system_memory:
            return 0
        return self.system_memory

    @property
    def system_memory_gb(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        if not self.system_memory:
            return 0
        return self.system_memory // 1024

    def sanitized_copy(self, logged_in=True) -> 'NVDockerDataResources':
        return self.make_copy()  # nothing ot sanitize

    def generate_resources_gpu_model_likepatterns(self) -> List[str]:
        if self.gpu_model is None:
            return []
        if isinstance(self.gpu_model, str):
            return ['%{}%'.format(self.gpu_model)]
        if hasattr(self.gpu_model, "__getitem__") or hasattr(self.gpu_model, "__iter__"): # Some type of iterable/List
            return list(map(lambda r: '%{}%'.format(r), self.gpu_model))
        raise ValueError('unsupported resources.gpuModel type: {}'.format(type(self.gpu_model)))

    def to_dict(self, strip=True) -> dict:
        res = dict()
        res['systemMemory'] = self.system_memory or 0
        res['cpuCores'] = self.cpu_cores or 0
        res['gpus'] = self.gpus or 0
        res['gpuModel'] = self.gpu_model
        res['minCudaVersion'] = self.min_cuda_version

        if strip:
            empty = []
            for key, value in res.items():
                if value is None:
                    empty.append(key)
            for key in empty:
                del res[key]

        return res

    @classmethod
    def from_dict(cls, d: dict) -> 'NVDockerDataResources':
        return cls(
            system_memory=d.get('systemMemory') or 0,
            cpu_cores=d.get('cpuCores') or 0,
            gpus=d.get('gpus') or 0,
            gpu_model=d.get('gpuModel'),
            min_cuda_version=d.get('minCudaVersion'),
        )

    def make_copy(self) -> 'NVDockerDataResources':
        return NVDockerDataResources.from_dict(self.to_dict())


class JobDataLocation:
    def __init__(self,
                 mount_point: Optional[str] = None,
                 share_path: Optional[str] = None,
                 protocol: Optional[str] = None,
                 share_host: Optional[str] = None,
                 ):
        """

        :param mount_point: The mountpoint INSIDE the container
        :param share_path: The local map on the slave (or the remote path if NFS is used)
        :param protocol:
        :param share_host:
        """
        self.mount_point = str(mount_point) if mount_point else None
        self.share_path = str(share_path) if share_path else None
        self.protocol = str(protocol) if protocol else None
        self.share_host = str(share_host) if share_host else None

    def to_dict(self, strip=True) -> dict:
        res = dict()
        res['mountPoint'] = self.mount_point
        res['sharePath'] = self.share_path
        res['protocol'] = self.protocol
        res['shareHost'] = self.share_host

        if strip:
            empty = []
            for key, value in res.items():
                if value is None:
                    empty.append(key)
            for key in empty:
                del res[key]

        return res

    @classmethod
    def from_dict(cls, d: dict) -> 'JobDataLocation':
        return cls(
            mount_point=d.get('mountPoint', d.get('mount_point')),
            share_path=d.get('sharePath', d.get('share_path')),
            protocol=d.get('protocol'),
            share_host=d.get('shareHost'),
        )

    def make_copy(self) -> 'JobDataLocation':
        return JobDataLocation.from_dict(self.to_dict())


class NVDockerData:
    def __init__(self,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 command: Optional[Union[List[str], str]] = None,  # this is passed to dockerpy container.run which allows str and list
                 docker_image: Optional[str] = None,
                 cluster_id: Optional[Union[List[int], int]] = None,
                 job_data_locations: Optional[List[Union[dict, JobDataLocation]]] = None,  # mountPoint and sharePath
                 job_type: Optional[str] = None,
                 port_mappings: Optional[List[Union[dict, JobPortMapping]]] = None,
                 resources: Optional[Union[dict, NVDockerDataResources]] = None,
                 environment: Optional[dict] = None,
                 ssh_pubkeys: Optional[List[str]] = None,
                 project_gid_variable_name: Optional[str] = None,
                 user_uid_variable_name: Optional[str] = None,
                 working_dir: Optional[str] = None,
                 docker_group_add: Optional[Union[List[str], str]] = None,
                 docker_user: Optional[str] = None,
                 ):
        self.description = str(description) if description else None
        self.docker_image = str(docker_image) if docker_image else None
        self.job_type = str(job_type) if job_type else None
        self.name = str(name) if name else None
        self.environment = dict(environment) if environment else {}
        self.ssh_pubkeys = list(ssh_pubkeys) if ssh_pubkeys else []
        self.docker_user = str(docker_user) if docker_user else None
        self.project_gid_variable_name = str(project_gid_variable_name) if project_gid_variable_name else None
        self.user_uid_variable_name = str(user_uid_variable_name) if user_uid_variable_name else None
        self.working_dir = str(working_dir) if working_dir else None

        if not cluster_id:  # None, or empty list
            self.cluster_id = None
        elif isinstance(cluster_id, int):
            self.cluster_id = int(cluster_id)
        elif isinstance(cluster_id, str):
            self.cluster_id = int(cluster_id)
        else:  # assume it's a list of int
            self.cluster_id = [int(ci) for ci in cluster_id]

        if not command:  # None, or empty list
            self.command = None
        elif isinstance(command, str):
            self.command = str(command)
        else:  # assume it's a list of str
            self.command = [str(c) for c in command]

        if not docker_group_add:  # None, or empty list
            self.docker_group_add = None
        elif isinstance(docker_group_add, str):
            self.docker_group_add = str(docker_group_add)
        else:  # assume it's a list of str
            self.docker_group_add = [str(c) for c in docker_group_add]

        if not job_data_locations:  # None, or empty list
            self.job_data_locations = []
        elif isinstance(job_data_locations[0], JobDataLocation):
            self.job_data_locations = list(job_data_locations)
        else:  # assume it's a list of dict like
            self.job_data_locations = [JobDataLocation.from_dict(d) for d in job_data_locations]

        if not port_mappings:  # None or empty list
            self.port_mappings = []
        elif isinstance(port_mappings[0], JobPortMapping):
            self.port_mappings = list(port_mappings)
        else:  # assume it's a dict like
            self.port_mappings = [JobPortMapping.from_dict(d) for d in port_mappings]

        if not resources:
            self.resources = NVDockerDataResources()
        elif isinstance(resources, NVDockerDataResources):
            self.resources = resources
        else:  # assume it's a dict like
            self.resources = NVDockerDataResources.from_dict(resources)

    @property
    def docker_image_nopass(self) -> Optional[str]:
        if self.docker_image:
            res = self.docker_image
            match = DOCKER_IMAGE_USERPASS_PATTERN.match(res)
            if match:
                return "{}:XXXX@{}".format(match.group(1), match.group(3))
            else:
                return res
        else:
            return None

    @property
    def docker_group_add_list(self) -> List[str]:
        if self.docker_group_add is None:
            return []
        elif isinstance(self.docker_group_add, str):
            return [self.docker_group_add]
        else:
            return self.docker_group_add

    @property
    def docker_command_list(self) -> List[str]:
        if self.command is None:
            return []
        elif isinstance(self.command, str):
            return [self.command]
        else:
            return self.command

    @property
    def requested_cluster_id_list(self) -> List[int]:
        """:return a list of cluster IDs that the user allows. Can be an empty list, but never None. An empty list means: accept any cluster."""
        res = self.cluster_id
        if res is None:
            return []
        elif isinstance(res, int):
            return [res]
        elif isinstance(res, str):
            return [int(res)]
        else:
            assert isinstance(res, (list, tuple))
            assert not isinstance(res, str)
            return list(map(int, res))

    def sanitized_copy(self, logged_in=True) -> 'NVDockerData':
        return NVDockerData(
            name=self.name,
            description=self.description,
            cluster_id=self.cluster_id,
            resources=self.resources.sanitized_copy(),
        )

    def to_dict(self, strip=True) -> dict:
        res = dict()
        res['name'] = self.name
        res['description'] = self.description
        res['command'] = self.command
        res['dockerImage'] = self.docker_image
        res['clusterId'] = self.cluster_id
        res['jobDataLocations'] = [dl.to_dict(strip) for dl in self.job_data_locations] if self.job_data_locations else None
        res['jobType'] = self.job_type
        res['portMappings'] = [pm.to_dict(strip=strip, snake_case=False) for pm in self.port_mappings] if self.port_mappings else None
        res['resources'] = self.resources.to_dict(strip)
        res['environment'] = self.environment
        res['ssh_pubkeys'] = self.ssh_pubkeys  # Correct: this one has snake_case instead of camelCase!
        res['projectGidVariableName'] = self.project_gid_variable_name
        res['userUidVariableName'] = self.user_uid_variable_name
        res['workingDir'] = self.working_dir
        res['dockerGroupAdd'] = self.docker_group_add
        res['dockerUser'] = self.docker_user

        if strip:
            empty = []
            for key, value in res.items():
                if not value:
                    empty.append(key)
            for key in empty:
                del res[key]

        return {
            NVDATA_JOBDEFINITION: res
        }

    @classmethod
    def from_jobdef_dict(cls, job_def: dict, *, strict=True, error_logger: Optional[Callable[[str], None]] = None) -> 'NVDockerData':
        res = cls(
            name=job_def.get('name'),
            description=job_def.get('description'),
            command=job_def.get('command'),
            docker_image=job_def.get('dockerImage'),
            cluster_id=job_def.get('clusterId'),
            job_data_locations=job_def.get('jobDataLocations'),
            job_type=job_def.get('jobType'),
            port_mappings=job_def.get('portMappings'),
            resources=job_def.get('resources'),
            environment=job_def.get('environment'),
            ssh_pubkeys=job_def.get('ssh_pubkeys'),
            project_gid_variable_name=job_def.get('projectGidVariableName'),
            user_uid_variable_name=job_def.get('userUidVariableName'),  # deprecated! does nothing anymore...
            working_dir=job_def.get('workingDir'),
            docker_group_add=job_def.get('dockerGroupAdd'),
            docker_user=job_def.get('dockerUser'),
        )

        allowed_keys = res.to_dict(strip=False)[NVDATA_JOBDEFINITION].keys()
        for key in job_def.keys():
            if key not in allowed_keys:
                if strict:
                    raise ValueError('Invalid Key "{}.{}"'.format(NVDATA_JOBDEFINITION, key))
                elif error_logger:
                    error_logger('Invalid Key in NVDockerData: "{}" - all keys: {}'.format(key, job_def.keys()))

        return res

    @classmethod
    def from_dict(cls, d: dict, *, strict=True, error_logger: Optional[Callable[[str], None]] = None) -> 'NVDockerData':
        res = cls.from_jobdef_dict(d.get(NVDATA_JOBDEFINITION, {}), strict=strict, error_logger=error_logger)

        if strict:
            allowed_keys = (NVDATA_JOBDEFINITION)
        else:
            # some keys ignored here for backward compatibility
            allowed_keys = (NVDATA_JOBDEFINITION, 'ssh_pubkeys', 'emails_end', 'email_run', 'email_done')

        for key in d.keys():
            if key not in allowed_keys:
                if strict:
                    raise ValueError('Invalid Key "{}"'.format(key))
                elif error_logger:
                    error_logger('Invalid Key "{}", only expecting NVDATA_JOBDEFINITION, but saw: {}'.format(key, d.keys()))

        return res

    def make_copy(self) -> 'NVDockerData':
        return NVDockerData.from_dict(self.to_dict())


class Job:
    def __init__(self,
                 uuid: Optional[str],
                 name: str,
                 state: JobState,
                 nvdocker_data: Optional[Union[NVDockerData, Dict]],
                 user_urn: str,
                 project_urn: str,
                 created: datetime.datetime,
                 state_updated: datetime.datetime,
                 queue_time: Optional[datetime.datetime],  # last time the job was put in the queue
                 gpulab_version: str,
                 run_details: Optional[Union[JobRunDetails, dict]],
                 scheduler_info: Optional[Union[JobSchedulerInfo, dict]],
                 ssh_pubkeys: List[str],
                 emails_queue: List[str],
                 emails_run: List[str],
                 emails_end: List[str],
                 user_email: Optional[str] = None,
                 ):
        # naive times not allowed
        assert queue_time is None or queue_time.tzinfo is not None
        assert created is None or created.tzinfo is not None
        assert state_updated is None or state_updated.tzinfo is not None

        assert uuid is None or isinstance(uuid, str)
        self.uuid = uuid
        self.id = uuid   #id and uuid are synonyms for Job
        self.name = name
        self.state = state
        self.user_urn = user_urn
        self.project_urn = project_urn
        self._user_email = user_email
        self.created = created
        self.state_updated = state_updated
        self.queue_time = queue_time
        self.gpulab_version = gpulab_version
        self.ssh_pubkeys = ssh_pubkeys if ssh_pubkeys is not None else []
        self.emails_queue = [str(e).strip() for e in emails_queue] if emails_queue is not None else []
        self.emails_run = [str(e).strip() for e in emails_run] if emails_run is not None else []
        self.emails_end = [str(e).strip() for e in emails_end] if emails_end is not None else []

        if nvdocker_data is None:
            self.nvdocker_data = NVDockerData()
        elif isinstance(nvdocker_data, NVDockerData):
            self.nvdocker_data = nvdocker_data
        else:  # assume it's a dict like
            self.nvdocker_data = NVDockerData.from_dict(nvdocker_data)

        if run_details is None:
            self.run_details = JobRunDetails()
        elif isinstance(run_details, JobRunDetails):
            self.run_details = run_details
        else:  # assume it's a dict like
            self.run_details = JobRunDetails.from_dict(run_details)

        if scheduler_info is None:
            self.scheduler_info = JobSchedulerInfo()
        elif isinstance(scheduler_info, JobSchedulerInfo):
            self.scheduler_info = scheduler_info
        else:  # assume it's a dict like
            self.scheduler_info = JobSchedulerInfo.from_dict(scheduler_info)

    def check_correctness(self) -> List[str]:
        """
        :return: a list of problems with this Job. Empty if there is no problem.
        """
        res = []
        if self.name != self.nvdocker_data.name:
            res.append('name ({}) VS nvdocker_data.jobDefinition.name ({}) mismatch'.format(
                self.name, self.nvdocker_data.name))
        return res

    @property
    def user_email(self) -> Optional[str]:
        if self._user_email:
            return self._user_email
        else:
            # fallback for wall2  TODO remove this legacy
            if self.user_urn and 'all2.ilabt.iminds.be' in self.user_urn:
                return '{}@wall2.ilabt.iminds.be'.format(self.userurn_name)
            return None

    @property
    def userurn_auth(self):
        return urn_to_auth(self.user_urn)

    # forward compatible with new name for gpulab_version
    @property
    def deployment_environment(self):
        return self.gpulab_version

    # forward compatible check if job is "stable" aka "production"
    @property
    def is_production(self) -> bool:
        return self.gpulab_version in ['stable', 'prod', 'production']

    @property
    def userurn_name(self):
        return urn_to_name(self.user_urn)

    @property
    def user_mini_id(self):
        return urn_to_user_mini_id(self.user_urn)

    @property
    def project_name(self):
        if self.project_urn and self.project_urn.startswith('urn:'):
            return URN(urn=self.project_urn).name
        else:
            return None

    def get_queue_duration(self) -> Optional[datetime.timedelta]:
        start = self.queue_time
        end = self.run_details.end_date
        if start is None:
            return None
        if end is None:
            end = datetime.datetime.now(datetime.timezone.utc)
        assert end.tzinfo is not None, 'end is naive "{}"'.format(start)
        assert start.tzinfo is not None, 'start is naive "{}"'.format(self.queue_time)
        return end - start

    def __repr__(self):
        return 'GpuLabJob %s: %s' % (self.name, self.uuid)

    def __eq__(self, rhs):
        return (
                self.uuid == rhs.uuid and
                type(self) == type(rhs))

    # def full_equal(self, rhs):
    #     # TODO: outdated
    #     return (
    #             self.uuid == rhs.uuid and
    #             self.name == rhs.name and
    #             self.state == rhs.state and
    #             self.nvdocker_data == rhs.nvdocker_data and
    #             self.user_urn == rhs.user_urn and
    #             self.project_urn == rhs.project_urn and
    #             self.user_email == rhs.user_email and
    #             self.created == rhs.created and
    #             self.state_updated == rhs.state_updated and
    #             self.gpulab_version == rhs.gpulab_version and
    #             self.run_details == rhs.run_details and
    #             self.ssh_pubkeys == rhs.ssh_pubkeys and
    #             type(self) == type(rhs))

    def sanitized_copy(self, logged_in=True, same_project=False) -> 'Job':
        """copy with removed confidential data
        :param logged_in: sanitized copy for logged in user, or for anonymous user?
        :param same_project: sanitized copy for user in same project, or for someone else?
        """
        copy = Job(
            uuid=self.uuid,
            name=(self.name if same_project or self.name == 'JupyterHub-singleuser' else ('job-'+self.uuid[:6] if self.uuid else 'job')) if self.name else None,
            state=self.state,
            nvdocker_data=self.nvdocker_data.sanitized_copy(logged_in),
            user_urn=self.user_urn,
            project_urn=(self.project_urn if same_project else 'urn:publicid:IDN+hidden+project+hidden') if self.project_urn else None,
            user_email='known by server' if self.user_email else None,  # email is not exposed in sanitized copies
            created=self.created,
            state_updated=self.state_updated,
            queue_time=self.queue_time,
            gpulab_version=self.gpulab_version,
            run_details=self.run_details.sanitized_copy(logged_in),
            scheduler_info=self.scheduler_info.sanitized_copy(logged_in),
            ssh_pubkeys=[], # no need for others to see pubkeys, even though it can't really harm
            emails_queue=[],
            emails_run=[],
            emails_end=[]
        )
        return copy

    def is_fully_sanitized(self) -> bool:
        return self.to_dict(strip=True) == self.sanitized_copy().to_dict(strip=True)
        # if not self.nvdocker_data  # or not self.nvdocker_data.get(NVDATA_JOBDEFINITION):
        #     return True  # Even a sanitized job should not be missing this
        # jobdef = self.nvdocker_data[NVDATA_JOBDEFINITION]
        # # an unsanitized job will have at least "dockerImage" and "command", a sanitized job will have none of the 3
        # return not ('dockerImage' in jobdef or 'command' in jobdef or 'jobDataLocations' in jobdef)

    def get_backward_compat_version(self):
        if self.gpulab_version == 'staging':
            return 'dev'
        if self.gpulab_version in ['production', 'prod']:
            return 'stable'
        return self.gpulab_version

    def to_dict(self, strip=True, backward_compat_version=False) -> dict:
        res = dict()
        res['uuid'] = self.uuid
        res['name'] = self.name
        res['state'] = self.state.name if self.state is not None else None
        res['nvdocker_data'] = self.nvdocker_data.to_dict(strip)
        res['user_urn'] = self.user_urn
        res['userurn_auth'] = urn_to_auth(self.user_urn)
        res['userurn_name'] = urn_to_name(self.user_urn)
        res['user_mini_id'] = urn_to_user_mini_id(self.user_urn)
        res['username'] = res['user_mini_id']  # to have some backward compatibility
        res['project_name'] = self.project_name
        res['project_urn'] = self.project_urn
        res['user_email'] = self.user_email
        res['created'] = _opt_date_str(self.created)
        res['state_updated'] = _opt_date_str(self.state_updated)
        res['queue_time'] = _opt_date_str(self.queue_time)
        res['gpulab_version'] = self.gpulab_version if not backward_compat_version else self.get_backward_compat_version()
        res['run_details'] = self.run_details.to_dict(strip)
        res['scheduler_info'] = self.scheduler_info.to_dict(strip)
        res['ssh_pubkeys'] = self.ssh_pubkeys
        res['emails_queue'] = self.emails_queue
        res['emails_run'] = self.emails_run
        res['emails_end'] = self.emails_end

        if strip:
            empty = []
            for key, value in res.items():
                if not value:
                    empty.append(key)
            for key in empty:
                del res[key]

        return res

    @classmethod
    def from_dict(cls, d: dict, strict=True):
        nvdocker_data = NVDockerData.from_dict(d.get('nvdocker_data'), strict=strict) if d.get('nvdocker_data') else None
        if not nvdocker_data and d.get(NVDATA_JOBDEFINITION):
            # in job request, we also allow jobDefinition directly
            nvdocker_data = NVDockerData.from_jobdef_dict(d.get(NVDATA_JOBDEFINITION))

        res = cls(
            uuid=d.get('uuid'),
            name=d.get('name'),
            state=JobState[d.get('state')] if d.get('state') else None,
            nvdocker_data=nvdocker_data,
            user_urn=d.get('user_urn'),
            project_urn=d.get('project_urn'),
            user_email=d.get('user_email'),
            created=_parse_opt_date(d.get('created')),
            state_updated=_parse_opt_date(d.get('state_updated')),
            queue_time=_parse_opt_date(d.get('queue_time')),
            gpulab_version=d.get('gpulab_version'),
            run_details=d.get('run_details'),
            scheduler_info=d.get('scheduler_info'),
            ssh_pubkeys=d.get('ssh_pubkeys'),
            emails_queue=d.get('emails_queue'),
            emails_run=d.get('emails_run'),
            emails_end=d.get('emails_end'),
        )
        allowed_keys = res.to_dict(strip=False).keys()
        for key in d.keys():
            if key not in allowed_keys and key not in (NVDATA_JOBDEFINITION, ):
                raise ValueError('Invalid Key "{}"'.format(key))
        return res

# Note: Job ID is a 36 char UUID (thus including the hyphens)


def is_partial_job_id(job_id: str):
    if re.search("[^0-9a-fA-F-]", job_id):
        return False
    return len(job_id) < 36


def is_full_job_id(job_id: str):
    return not is_bad_job_id(job_id)


def is_bad_job_id(job_id: str):
    """Identifies job_id for which there is 100% certain a problem (too short, wrong chars, too long)"""
    l = len(job_id)
    if l != 36:
        return True
    if re.search("[^0-9a-fA-F-]", job_id):
        return True
    return not is_valid_job_id(job_id)


def is_valid_job_id(id: str) -> bool:
    return is_valid_uuid(id)
