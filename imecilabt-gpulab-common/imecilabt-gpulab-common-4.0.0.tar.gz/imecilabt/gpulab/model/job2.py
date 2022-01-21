import dataclasses
import datetime
import itertools
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Union, Any, Dict

import dateutil.parser
from stringcase import camelcase
from imecilabt_utils.utils import duration_string_to_seconds

from imecilabt.gpulab.model.job import DOCKER_IMAGE_USERPASS_PATTERN
from imecilabt.gpulab.model.usage_statistics import GPULabUsageStatistics, GpuOverview
from dataclass_dict_convert import dataclass_dict_convert, create_wrap_in_list_from_convertor, \
    dataclass_auto_type_check, dataclass_copy_method, dataclass_multiline_repr
from imecilabt_utils.urn_util import URN, is_valid_urn, check_valid_urn_bytype
from imecilabt_utils.validation_utils import is_valid_uuid, is_valid_email, is_valid_ssh_key, ALLOWED_HOST_KEY_ALGOS

from imecilabt.gpulab.util.convert_utils import urn_to_user_mini_id, urn_to_name, urn_to_auth


def is_valid_job_id(id: str) -> bool:
    return is_valid_uuid(id)  # we allow both version 1 and 4 UUIDs (version 4 is used for new jobs)
    #return is_valid_uuid4(id)


def _test_char_list(tested_list: Optional[List[str]], tested_list_name: str, *, dont_allow_any_single_char: bool = False) -> None:
    if isinstance(tested_list, list) and (len(tested_list) >= 5 or dont_allow_any_single_char):
        if len(tested_list) == 0:
            return
        has_single_char = any(len(el) == 1 for el in tested_list)
        all_single_char = all(len(el) == 1 for el in tested_list)
        if all_single_char:
            if dont_allow_any_single_char:
                # Almost certain: there is a programming error somewhere, and we have a list of chars made from a single string...
                raise ValueError('Bug: {} is list of single char str, instead a list of str'.format(tested_list_name))
            elif len(tested_list) >= 5:
                # Extremely low chance this is a real list of str
                # Most likely: there is a programming error somewhere, and we have a list of chars made from a single string...
                raise ValueError('Bug: {} is list of single char str, instead a list of str'.format(tested_list_name))
            else:
                # short list with single chars. We're not sure.
                pass
        if has_single_char and dont_allow_any_single_char:
            raise ValueError('{} contains a single char str. This is not correct.'.format(tested_list_name))


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


class JobStatus(Enum):
    ONHOLD = 'On Hold'             # On hold, not planned to run at this time (not in queue)
    QUEUED = 'Queued'              # Available to run, waiting in queue
    ASSIGNED = 'Assigned'          # Assigned to a specific node by the scheduler, but not yet "picked up" by that node.
    STARTING = 'Starting'          # Received by worker, setup in progress, not yet running
    RUNNING = 'Running'            # Running on worker
    CANCELLED = 'Cancelled'        # Cancelled during run (due to user request)
    FINISHED = 'Finished'          # Run completed
    DELETED = 'Deleted'            # Marked as deleted. This causes it to be ignored in "queue" view
    FAILED = 'Failed'              # Failure due to job definition problem, system problems, or other.

    # HALT = stopped, but a new job was QUEUED to continue it's work.  (restartable jobs can be halted)
    MUSTHALT = 'Must Halt'         # Master has requested to "halt" the job
    HALTING = 'Halting'            # Worker is attempting to "halt" the job
    HALTED = 'Halted'              # The job was correctly "halted"

    @classmethod
    def find_case_insensitive(cls, searched: str) -> 'JobStatus':
        for cur_name, cur_status in JobStatus.__members__.items():  # type: str, JobStatus
            assert JobStatus[cur_name] == cur_status
            assert JobStatus[cur_name].name == cur_name
            if cur_name.lower() == searched.lower():
                return cur_status
            if cur_status.value.lower() == searched.lower():
                return cur_status
        raise ValueError(f'JobStatus "{searched}" does not exist')


# dataclasses_json.cfg.global_config.encoders[JobStatus] = lambda js: js.name if js is not None else None
# dataclasses_json.cfg.global_config.decoders[JobStatus] = JobStatus.__members__.get

class HaltReason(Enum):
    UNKNOWN = 'Unknown'
    USER = 'User requested fallback manually'
    ADMIN = 'Admin requested fallback'
    SCORE = 'Score'
    RESERVATION = 'Reservation Priority'
    CLUSTER = 'Private Cluster Priority'

    @classmethod
    def find_case_insensitive(cls, searched: str) -> 'HaltReason':
        for cur_name, cur_status in HaltReason.__members__.items():  # type: str, HaltReason
            assert HaltReason[cur_name] == cur_status
            assert HaltReason[cur_name].name == cur_name
            if cur_name.lower() == searched.lower():
                return cur_status
            if cur_status.value.lower() == searched.lower():
                return cur_status
        # raise ValueError(f'HaltReason "{searched}" does not exist')
        # for forward compatible reasons, when nothing found, return unknown.
        return HaltReason.UNKNOWN


@dataclass_dict_convert(
    dict_letter_case=camelcase,
    custom_from_dict_convertors={
        'halt_reason': HaltReason.find_case_insensitive
    })
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class HaltInfo:
    reason: HaltReason
    time: datetime.datetime
    started_job_uuids: List[str]
    halted_job_uuids: List[str]
    slave_name: str  # slave name of the slave the halted jobs run on
    slave_instance: str  # slave instance the started job(s) will run on (halted jobs might be on this instance, or on stopping instances)
    started_job_scores: List[Optional[float]]  # same order as UUIDs
    halted_job_scores: List[Optional[float]]  # same order as UUIDs


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class JobPortMapping:
    container_port: int = None
    host_port: Optional[int] = None
    host_ip: Optional[str] = None

    @classmethod
    def from_docker_dict(cls, d: dict, *, container_port: Optional[Union[int, str]] = None) -> 'JobPortMapping':
        """
        Make JobPortMapping from the port mapping dict that docker returns
        :param d: the dict that docker returns
        :param container_port: set the container_port directly instead of using the dict (optional)
        :return:
        """
        def _handle_port_val(val: Union[str, int]) -> Optional[int]:
            if val is None:
                return None
            if isinstance(val, int):
                return val
            val = str(val)
            val = val.replace("/tcp", "").replace("/udp", "")
            return int(val)

        return cls(
            container_port=_handle_port_val(container_port if container_port else d.get('ContainerPort', d.get('containerPort', d.get('container_port')))),
            host_port=_handle_port_val(d.get('HostPort', d.get('hostPort', d.get('host_port')))),
            host_ip=d.get('HostIp', d.get('hostIp', d.get('host_ip'))),
        )
    #
    # @staticmethod
    # def from_dict_list(pm_dict_lst: List[Dict]) -> List['JobPortMapping']:
    #     # Note: normally, you can do this with Job.schema().load(pm_dict_lst, many=True)
    #     #       that seems to ignore global decoders however
    #     #       (which is not a problem here, but we also avoid it here for consistency)
    #     return [JobPortMapping.from_dict(d) for d in pm_dict_lst]


def camelCaseOrAllCaps(input: str) -> str:
    if input.isupper():
        return input
    else:
        from stringcase import camelcase
        return camelcase(input)


# @dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass_dict_convert(dict_letter_case=camelCaseOrAllCaps)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class JobEventTimes:
    created: datetime.datetime
    status_updated: datetime.datetime

    QUEUED: Optional[datetime.datetime] = None
    ASSIGNED: Optional[datetime.datetime] = None
    STARTING: Optional[datetime.datetime] = None
    RUNNING: Optional[datetime.datetime] = None
    FINISHED: Optional[datetime.datetime] = None
    FAILED: Optional[datetime.datetime] = None
    CANCELLED: Optional[datetime.datetime] = None
    DELETED: Optional[datetime.datetime] = None
    MUSTHALT: Optional[datetime.datetime] = None
    HALTING: Optional[datetime.datetime] = None
    HALTED: Optional[datetime.datetime] = None

    long_run_notify: Optional[datetime.datetime] = None # last time long run notify email was sent

    def end_date(self) -> Optional[datetime.datetime]:
        if self.FINISHED:
            return self.FINISHED
        if self.HALTED:
            return self.HALTED
        if self.FAILED:
            return self.FAILED
        if self.CANCELLED:
            return self.CANCELLED
        if self.DELETED:
            return self.DELETED
        return None

    def get_duration(self) -> Optional[datetime.timedelta]:
        start = self.RUNNING
        end = self.FINISHED or self.CANCELLED or self.FAILED or self.HALTED or self.DELETED
        if start is None:
            return None
        if end is None:
            end = datetime.datetime.now(datetime.timezone.utc)
        assert end.tzinfo is not None, 'end is naive "{}"'.format(end)
        assert start.tzinfo is not None, 'start is naive "{}"'.format(start)
        return end - start

    def get_queue_duration(self) -> Optional[datetime.timedelta]:
        start = self.QUEUED
        end = self.STARTING or self.RUNNING or self.FAILED or self.HALTED or self.CANCELLED or self.DELETED
        if start is None:
            return None
        if end is None:
            end = datetime.datetime.now(datetime.timezone.utc)
        assert end.tzinfo is not None, 'end is naive "{}"'.format(start)
        assert start.tzinfo is not None, 'start is naive "{}"'.format(self.queue_time)
        return end - start

    def sanitized_copy(self, logged_in=True, same_project=False) -> 'JobEventTimes':
        # all may be known
        # TODO maybe hide some more if not logged_in
        return dataclasses.replace(self, long_run_notify=None)


def custom_tmpfs_mem_gb_to_dict(tmpfs_mem_gb: Optional[int]) -> Optional[int]:
    if tmpfs_mem_gb is None or tmpfs_mem_gb == 0:
        return None
    else:
        return tmpfs_mem_gb


def custom_tmpfs_mem_gb_from_dict(tmpfs_mem_gb: Optional[int]) -> Optional[int]:
    if tmpfs_mem_gb is None or tmpfs_mem_gb == 0:
        return 0
    else:
        return tmpfs_mem_gb


@dataclass_dict_convert(
    dict_letter_case=camelcase,
    custom_to_dict_convertors={
        'tmpfs_mem_gb': custom_tmpfs_mem_gb_to_dict
    },
    custom_from_dict_convertors={
        'tmpfs_mem_gb': custom_tmpfs_mem_gb_from_dict
    }
)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class JobStateResources:
    cluster_id: int
    gpu_ids: List[int]
    cpu_ids: List[int]
    cpu_memory_gb: int  # does NOT include tmpfs memory (it is listed separately below)
    gpu_memory_gb: int  # if less than a GB, this is rounded DOWN (so it can be 0!)

    slave_name: str
    slave_host: str
    slave_instance_id: str
    slave_instance_pid: int
    worker_id: int

    ssh_host: Optional[str] = None
    ssh_port: Optional[int] = None
    ssh_username: Optional[str] = None
    ssh_proxy_host: Optional[str] = None
    ssh_proxy_port: Optional[int] = None
    ssh_proxy_username: Optional[str] = None

    port_mappings: List[JobPortMapping] = field(default_factory=list)
    gpu_details: Optional[GpuOverview] = None

    tmpfs_mem_gb: Optional[int] = 0  # None = 0

    @property
    def cpu_memory_mb(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return self.cpu_memory_gb * 1024

    @property
    def cpu_memory_byte(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return self.cpu_memory_gb * 1024 * 1024 * 1024

    @property
    def tmpfs_mem_mb(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return (self.tmpfs_mem_gb or 0) * 1024

    @property
    def tmpfs_mem_byte(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return (self.tmpfs_mem_gb or 0) * 1024 * 1024 * 1024

    @property
    def all_cpu_memory_gb(self) -> int:
        return self.cpu_memory_gb + (self.tmpfs_mem_gb or 0)

    @property
    def all_cpu_memory_mb(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return (self.all_cpu_memory_gb or 0) * 1024

    @property
    def all_cpu_memory_byte(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return (self.all_cpu_memory_gb or 0) * 1024 * 1024 * 1024

    def sanitized_copy(self, logged_in=True, same_project=False) -> 'JobStateResources':
        # not entirely public, but all not that private
        res = dataclasses.replace(
            self,
            ssh_username='hidden',
            ssh_proxy_username='hidden',
            port_mappings=[],
            gpu_details=None
        )
        if not logged_in:
            res = dataclasses.replace(
                res,
                gpu_ids=[],
                cpu_ids=[],
                slave_host='hidden',
                slave_name='hidden',
                slave_instance_id='hidden',
                slave_instance_pid=-1,
                worker_id=-1,
                ssh_host='hidden',
                ssh_port=-1,
                ssh_proxy_host='hidden',
                ssh_proxy_port=-1,
            )
        return res


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class MaxSimultaneousJobs:
    bucket_name: str
    bucket_max: int


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True, repr=False)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class JobRequestExtra:
    ssh_pub_keys: List[str] = field(default_factory=list)
    email_on_queue: List[str] = field(default_factory=list)  # also email on queueing of restart job
    email_on_run: List[str] = field(default_factory=list)  # no email on restart
    email_on_end: List[str] = field(default_factory=list)  # no email on successful halt
    email_on_halt: List[str] = field(default_factory=list)  # email on MUSTHALT
    email_on_restart: List[str] = field(default_factory=list)

    def __post_init__(self):
        for email in itertools.chain(self.email_on_queue, self.email_on_run, self.email_on_end):
            if not is_valid_email(email):
                raise ValueError('Invalid email "{}"'.format(email))
        for ssh_pub_key in self.ssh_pub_keys:
            if not is_valid_ssh_key(ssh_pub_key):
                raise ValueError('Invalid SSH public key "{}" (allowed host key algos: {})'
                                 .format(ssh_pub_key, ALLOWED_HOST_KEY_ALGOS))

    def sanitized_copy(self, logged_in=True, same_project=False) -> 'JobRequestExtra':
        # hide all
        return JobRequestExtra([], [], [], [], [], [])


def _backward_compat_preprocess_job_request_scheduling(d: Dict) -> Dict:
    # For a while JobRequestScheduling.min_duration was named JobRequestScheduling.killable_after
    # We want to be 100% backward compatible to this
    if 'killableAfter' in d:
        if 'minDuration' not in d:
            d['minDuration'] = d['killableAfter']
        del d['killableAfter']

    # Initially, reservation_id was a single reservation ID, not a list.
    # We want to stay backward compatible with this.
    # Probably good to keep this forever.
    if 'reservationId' in d:
        if 'reservationIds' not in d:
            d['reservationIds'] = [d['reservationId']] if isinstance(d['reservationId'], str) else d['reservationId']
        del d['reservationId']
    return d


@dataclass_dict_convert(
    dict_letter_case=camelcase,
    preprocess_from_dict=_backward_compat_preprocess_job_request_scheduling,
)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class JobRequestScheduling:
    """
    GPULab scheduling instructions.

    Attributes:
      interactive: Interactive jobs will either run immediately, or fail directly. They will never be QUEUED for a long time.
      min_duration: GPULab might stop this job after this duration. Setting this allows GPULab to schedule this job earlier than it can otherwise, but there is a chance your job will be stopped after this time. (If it is restartable, it will however restart later.) Format: a number followed by a unit (ex: 5 minutes, 3 hour, 2 days, 1 week, ...)
      restartable: Restartable jobs can be stopped and later restarted by GPULab. Before stopping, GPULab will send a signal to the job. In exchange for this flexibility, GPULab can start the jobs sooner than it otherwise would.
      reservation_id: The reservation ID(s) to use it for the job. This allows the job to start when it otherwise would not be able to start due to a reservation.
      max_duration: The maximum duration of this job. GPULab will always stop your job after this time. If the job has been restarted once or more, the total duration of all the job runs is used. Format: a number followed by a unit (ex: 5 minutes, 3 hour, 2 days, 1 week, ...)
      max_simultaneous_jobs: Control how many of your jobs can run at the same time. Format: { "bucket_name": <bucketname>, "bucket_max": <max number> }
      not_before: Request GPULab not to start the job before a specified date. It will stay QUEUED at least until the requested time. Format: an RFC3339 date.
      not_after: Request GPULab to FAIL the job if it is still QUEUED at a specified date. (Does not affect an already running job, only prevents start after the date.) Format: an RFC3339 date.
    """
    interactive: bool = False
    min_duration: Optional[str] = None  # duration str
    restartable: bool = False
    reservation_ids: List[str] = field(default_factory=list)
    max_duration: Optional[str] = None  # duration str
    max_simultaneous_jobs: Optional[MaxSimultaneousJobs] = None
    not_before: Optional[datetime.datetime] = None
    not_after: Optional[datetime.datetime] = None

    def __post_init__(self):
        if self.min_duration is not None and duration_string_to_seconds(self.min_duration) is None:
            raise AttributeError('min_duration must be a number followed by a time unit, not "{}"'
                                 .format(self.min_duration))
        if self.max_duration is not None:
            max_dur_s = duration_string_to_seconds(self.max_duration)
            if max_dur_s is None:
                raise AttributeError('max_duration must be a number followed by a time unit, not "{}"'
                                     .format(self.max_duration))
            if max_dur_s < 60:
                raise AttributeError('max_duration must be at least 1 minute, not "{}"'
                                     .format(self.max_duration))
        if self.not_before and self.interactive:
            raise AttributeError('not_before cannot be combined with interactive')
        if self.not_after and self.interactive:
            raise AttributeError('not_after cannot be combined with interactive')
        if self.not_before and self.not_after and self.not_before >= self.not_after:
            raise AttributeError(f'not_before ({self.not_before}) must be before not_after ({self.not_after})')

    @property
    def max_duration_s(self) -> Optional[int]:
        return duration_string_to_seconds(self.max_duration) if self.max_duration is not None else None

    @property
    def min_duration_s(self) -> Optional[int]:
        return duration_string_to_seconds(self.min_duration) if self.min_duration is not None else None

    def get_min_duration_delta(self, *, default_s: Optional[int]) -> Optional[datetime.timedelta]:
        if self.min_duration is None:
            if default_s is None:
                return None
            else:
                return datetime.timedelta(seconds=default_s)
        res = duration_string_to_seconds(self.min_duration)
        if res is None:
            return None  # invalid duration string
        return datetime.timedelta(seconds=res)

    def sanitized_copy(self, logged_in=True, same_project=False) -> 'JobRequestScheduling':
        # hide only reservation ID
        return dataclasses.replace(self, reservation_ids=['hidden'] if self.reservation_ids else [])


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class JobStateScheduling:
    assigned_cluster_id: Optional[int] = None
    assigned_instance_id: Optional[str] = None
    assigned_slave_name: Optional[str] = None
    # assigned_time: Optional[datetime.datetime] = None  # Not needed, stored in JobEventTimes
    queued_explanations: List[str] = field(default_factory=list)
    within_max_simultaneous_jobs: Optional[bool] = None  # deprecated now! Scheduling determines this internally on the fly instead
    tally_increment: Optional[float] = None  # The tally increment each 5 minutes caused by the resource use of this job

    # Halt events describe why which job(s) where stopped (for which job(s))
    # They can be added when a job is started because other jobs were halted, or when a job is halted
    halt_events: List[HaltInfo] = field(default_factory=list)

    # The 3 schedulers look at this job at different times. (basic scheduler, advanced score/prio based halt scheduler)
    # These values might be None, if the corresponding scheduler part hasn't seen the job yet.
    # If this is not none, the corresponding scheduler part has looked at least once.
    # Some values _might_ not be updated after the first time the corresponding scheduler part sees them.
    #    (because that info is not needed, and there's a cost to updating it.)
    scheduler_seen_base: Optional[datetime.datetime] = None
    scheduler_seen_score_halt: Optional[datetime.datetime] = None  # updated when scheduler actually checks if job can be started by halting others
    scheduler_seen_prio_halt: Optional[datetime.datetime] = None  # updated when scheduler actually checks if job can be started by halting others

    # The scheduler is letting this job use these reservations, even though the job is not allowed too use them.
    # This makes the job a target to automatically HALT when users of the reservation start jobs.
    # (At the moment, the scheduler allowes jobs to ignore only 1 reservation at a time.
    #  This field is future proof by allowing multiple.)
    ignoring_reservation_ids: List[str] = field(default_factory=list)

    def sanitized_copy(self, logged_in=True, same_project=False) -> 'JobStateScheduling':
        # Nothing to hide
        # TODO maybe hide some more if not logged_in
        return self.make_copy()

    def make_compatible_with(self, gpulab_api_version: str) -> 'JobStateScheduling':
        """
        Return a version of this that is backwards compatible with version 3.X.
        :param gpulab_api_version: version to be compatible with.
        :return:
        """
        if gpulab_api_version == '3.1':
            return self
        else:
            assert gpulab_api_version == '3.0'
            return JobStateScheduling(
                assigned_cluster_id=self.assigned_cluster_id,
                assigned_instance_id=self.assigned_instance_id,
                assigned_slave_name=self.assigned_slave_name,
                queued_explanations=list(self.queued_explanations),
                within_max_simultaneous_jobs=self.within_max_simultaneous_jobs,
                tally_increment=None,  # tally_increment is not compatible with 3.0
                halt_events=[],  # halt_events is not compatible with 3.0
            )


@dataclass_dict_convert(
    dict_letter_case=camelcase,
    custom_from_dict_convertors={
        'gpu_model': create_wrap_in_list_from_convertor(str),
    }
)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class JobRequestResources:
    cpus: int
    gpus: int
    cpu_memory_gb: int
    gpu_memory_gb: Optional[int] = None

    features: List[str] = field(default_factory=list)
    gpu_model: List[str] = field(default_factory=list)  # We used to allow None, a str or a list of str. We don't allow a naked str anymore.
    min_cuda_version: Optional[int] = None
    cluster_id: Optional[int] = None
    slave_name: Optional[str] = None
    slave_instance_id: Optional[str] = None

    def __post_init__(self):
        _test_char_list(self.gpu_model, 'Job.request.resources.gpu_model', dont_allow_any_single_char=True)
        _test_char_list(self.features, 'Job.request.resources.features', dont_allow_any_single_char=True)

    def sanitized_copy(self, logged_in=True, same_project=False) -> 'JobRequestResources':
        """copy with removed confidential data
        :param logged_in: sanitized copy for logged in user, or for anonymous user?
        :param same_project: sanitized copy for user in same project, or for someone else?
        """
        return self.make_copy()  # nothing to sanitize

    @property
    def cluster_id_list(self) -> List[int]:
        return [self.cluster_id] if self.cluster_id else []

    @property
    def cpu_memory_mb(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return self.cpu_memory_gb * 1024

    @property
    def cpu_memory_byte(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return self.cpu_memory_gb * 1024 * 1024 * 1024

    def matches_gpu_model(self, tested_model: str) -> bool:
        return any(my_model.lower() in tested_model.lower() for my_model in self.gpu_model)


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class JobStorage:
    container_path: Optional[str] = None  # default: host_path
    host_path: Optional[str] = None  # default: container_path
    size_gb: Optional[int] = None  # default: None

    def __post_init__(self):
        if not self.container_path and not self.host_path:
            raise AttributeError('need at least one of host_path and container_path')
        if not self.container_path:
            object.__setattr__(self, 'container_path', self.host_path)
        if not self.host_path:
            object.__setattr__(self, 'host_path', self.container_path)

    # only useful for backward compat testing
    def _without_size(self) -> 'JobStorage':
        return JobStorage(container_path=self.container_path, host_path=self.host_path)

    @property
    def is_tmpfs(self) -> bool:
        return self.host_path == 'tmpfs'

    @property
    def is_ssh_dir(self) -> bool:
        return self.host_path == '.ssh' or self.host_path == '.ssh/' or \
               (not self.host_path and (self.container_path == '/root/.ssh' or self.container_path == '/root/.ssh/'))

    @classmethod
    def from_string(cls, s: str) -> 'JobStorage':
        return cls(container_path=s, host_path=s, size_gb=None)

    def normalize(self) -> 'JobStorage':
        """
        Normalises the JobStorage.
        This involves:
          - both paths always end with /
          - both paths are present: if only container_path or only host_path is filled in,
            the other gets automatically filled in (an error is raised when this is not possible)
        :return: The normalized form of this job storage.
        """
        def add_end_slash_ifneeded(dir: str):
            return dir + '/' if not dir.endswith('/') else dir

        def samedir(dira, dirb):
            if not dira.endswith('/'):
                dira += '/'
            if not dirb.endswith('/'):
                dirb += '/'
            return dira == dirb

        if self.is_tmpfs:
            assert self.host_path
            assert self.container_path
            assert self.size_gb
            # tmpfs is the only case where host_path doesn't end with /
            return JobStorage(
                host_path=self.host_path,
                container_path=add_end_slash_ifneeded(self.container_path),
                size_gb=self.size_gb,
            )

        container_path = add_end_slash_ifneeded(self.container_path)
        host_path = self.host_path

        if host_path and container_path:
            host_path = add_end_slash_ifneeded(host_path)
            container_path = add_end_slash_ifneeded(host_path)

        if host_path and not container_path:
            if samedir(host_path, '.ssh/'):
                host_path = add_end_slash_ifneeded(host_path)
                container_path = '/root/.ssh/'
            else:
                host_path = add_end_slash_ifneeded(host_path)
                container_path = add_end_slash_ifneeded(host_path)

        if container_path and not host_path:
            if samedir(container_path, '/root/.ssh/'):
                host_path = '.ssh/'
            else:
                host_path = add_end_slash_ifneeded(container_path)

        if not container_path:
            raise ValueError(f'Illegal single path: container_path={container_path}')
        if not host_path:
            raise ValueError(f'Illegal single path: host_path={host_path}')
        assert host_path.endswith('/'), f'host_path does not end in /: host_path={host_path} container_path={host_path}'
        assert container_path.endswith('/'), f'container_path does not end in /: host_path={host_path} container_path={host_path}'

        return JobStorage(
            host_path=host_path,
            container_path=self.container_path,
            size_gb=self.size_gb,
        )


def _convert_portmappings(pm_list: List):
    if not pm_list:
        return pm_list
    res = []
    for pm in pm_list:
        if isinstance(pm, int):
            res.append(JobPortMapping(container_port=pm, host_port=None))
        else:
            assert isinstance(pm, dict)
            res.append(JobPortMapping.from_dict(pm))
    return res


def _convert_storage(storage_list: List):
    if not storage_list:
        return storage_list
    res = []
    for s in storage_list:
        if isinstance(s, str):
            res.append(JobStorage(container_path=s, host_path=s, size_gb=None))
        else:
            assert isinstance(s, dict)
            res.append(JobStorage.from_dict(s))
    return res

# def _pre_process_portmappings(pm_list: List):
#     if not pm_list:
#         return pm_list
#     res = []
#     for pm in pm_list:
#         if isinstance(pm, int):
#             res.append(JobPortMapping(container_port=pm, host_port=None))
#         else:
#             assert isinstance(pm, dict)
#             res.append(pm)
#     return res
#
#
# def _pre_process_storage(storage_list: List):
#     if not storage_list:
#         return storage_list
#     res = []
#     for s in storage_list:
#         if isinstance(s, str):
#             res.append(JobStorage(container_path=s, host_path=s))
#         else:
#             assert isinstance(s, dict)
#             res.append(s)
#     return res


# @dataclass_json_pre_modify_dict_field(modifier_by_fieldname={'port_mappings': _pre_process_portmappings, 'storage': _pre_process_storage})
@dataclass_dict_convert(dict_letter_case=camelcase,
                        direct_fields=['command', 'environment'],
                        custom_from_dict_convertors={
                            'group_add': create_wrap_in_list_from_convertor(str),
                            'port_mappings': _convert_portmappings,
                            'storage': _convert_storage,
                        },)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class JobRequestDocker:
    image: str
    # A single command not in a list has a different meaning than a single command in a list (!):
    #   In the 1st case, the command can includes spaces and is processed like a shell
    #   In the 2nd case, the first element is the executable and the other the literal arguments
    # Note that dockerpy container.run directly accepts the same 2 types of arguments in the same way
    command: Union[str, List[str]] = field(default_factory=list)
    environment: dict = field(default_factory=dict)
    storage: List[JobStorage] = field(default_factory=list)
    port_mappings: List[JobPortMapping] = field(default_factory=list)
    project_gid_variable_name: Optional[str] = None
    # user_uid_variable_name: Optional[str] = None  # deprecated
    working_dir: Optional[str] = None
    group_add: List[str] = field(default_factory=list)
    user: Optional[str] = None

    def __post_init__(self):
        _test_char_list(self.command, 'Job.request.docker.command', dont_allow_any_single_char=False)
        _test_char_list(self.group_add, 'Job.request.docker.group_add', dont_allow_any_single_char=False)

    @property
    def tmpfs_memory_gb(self) -> int:
        res = 0
        for s in self.storage:
            if s.is_tmpfs and s.size_gb:
                res += s.size_gb
        return res

    @property
    def tmpfs_memory_mb(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return self.tmpfs_memory_gb * 1024

    @property
    def tmpfs_memory_byte(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return self.tmpfs_memory_gb * 1024 * 1024 * 1024

    @property
    def image_nopass(self) -> str:
        res = self.image
        match = DOCKER_IMAGE_USERPASS_PATTERN.match(res)
        if match:
            return "{}:XXXX@{}".format(match.group(1), match.group(3))
        else:
            return res

    @property
    def command_as_str(self) -> Optional[str]:
        if not self.command:
            return None
        if isinstance(self.command, str):
            return self.command
        return ' '.join(self.command)

    def sanitized_copy(self, logged_in=True, same_project=False) -> 'JobRequestDocker':
        if logged_in and same_project:
            return JobRequestDocker(
                image=self.image_nopass,  # password is stipped from docker image if shown to project members
                command=self.command,
                environment=self.environment,
                storage=self.storage,
                port_mappings=self.port_mappings,
                project_gid_variable_name=self.project_gid_variable_name,
                working_dir=self.working_dir,
                group_add=self.group_add,
                user=self.user,
            )
        else:
            return JobRequestDocker(
                image='hidden',
                command=[],
                environment={},
                storage=[],
                port_mappings=[],
                project_gid_variable_name=None,
                working_dir=None,
                group_add=[],
                user=None,
            )


# @dataclass_json_hack_nested_from_dict  # needed for JobRequestResources and JobRequestDocker
@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class JobRequest:
    resources: JobRequestResources
    docker: JobRequestDocker
    scheduling: JobRequestScheduling = field(default_factory=JobRequestScheduling)
    extra: JobRequestExtra = field(default_factory=JobRequestExtra)

    @property
    def all_cpu_memory_gb(self) -> int:
        return (self.resources.cpu_memory_gb or 0) + (self.docker.tmpfs_memory_gb or 0)

    @property
    def all_cpu_memory_mb(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return self.all_cpu_memory_gb * 1024

    @property
    def all_cpu_memory_byte(self) -> int:
        # while GB is sometimes 1000^3 instead of 1024^3 (typically HD size etc), for memory, base 1024 is always used.
        # (and docker seems to use 1000 based, which is silly)
        return self.all_cpu_memory_gb * 1024 * 1024 * 1024

    def sanitized_copy(self, logged_in=True, same_project=False) -> 'JobRequest':
        """copy with removed confidential data
        :param logged_in: sanitized copy for logged in user, or for anonymous user?
        :param same_project: sanitized copy for user in same project, or for someone else?
        """
        copy = JobRequest(
            resources=self.resources.sanitized_copy(logged_in, same_project),
            docker=self.docker.sanitized_copy(logged_in, same_project),
            scheduling=self.scheduling.sanitized_copy(logged_in, same_project),
            extra=self.extra.sanitized_copy(logged_in, same_project),
        )
        return copy


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class RestartInfo:
    initial_job_uuid: str
    restart_count: int

    def __post_init__(self):
        if not is_valid_uuid(self.initial_job_uuid):
            raise ValueError('Invalid initial_job_uuid "{}"'.format(self.initial_job_uuid))
        if self.restart_count < 0:
            raise ValueError('Invalid restart_count "{}"'.format(self.restart_count))


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class UserDetails:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    portal_home: Optional[str] = None
    organization: Optional[str] = None
    affiliation: Optional[str] = None
    creation_date: Optional[str] = None
    eppn: Optional[str] = None
    country: Optional[str] = None
    idlab: Optional[str] = None


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class JobOwner:
    user_urn: str
    user_email: str
    project_urn: str
    user_details: Optional[UserDetails] = None

    def __post_init__(self):
        if not is_valid_email(self.user_email):
            raise ValueError('Invalid user_email "{}"'.format(self.user_email))
        if not check_valid_urn_bytype(self.user_urn, 'user'):
            raise ValueError('Invalid user_urn "{}"'.format(self.user_urn))
        if not check_valid_urn_bytype(self.project_urn, 'project'):
            raise ValueError('Invalid project_urn "{}"'.format(self.project_urn))

    @property
    def userurn_auth(self):
        return urn_to_auth(self.user_urn)

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

    def is_partially_sanitized(self) -> bool:
        return self.project_urn == 'urn:publicid:IDN+hidden+project+hidden' or self.user_email == 'hidden@hidden.hidden'

    def sanitized_copy(self, logged_in=True, same_project=False) -> 'JobOwner':
        # hide the user details, email address and project
        return dataclasses.replace(
            self,
            user_email='hidden@hidden.hidden',
            project_urn=self.project_urn if logged_in and same_project else 'urn:publicid:IDN+hidden+project+hidden',
            user_details=None
        )

#
# State vs Status
#
#   -> in the english language: very related, and often synonyms
#   -> typically in technical language, state is used in a more broad sense, and status is more "one-dimensional"
#       -> thus you can have a state containing multiple statuses
#
#  Here:
#   -> in JobState we describe the entire variable state of the Job.
#      "status" holds the ID of the current discrete step in the Job's lifecycle ("the workflow of job execution")
#      so "lifecycle_step" or "workflow_position" would be a synonym for our "status", but both feels too convoluted
#
@dataclass_dict_convert(
    dict_letter_case=camelcase,
    custom_from_dict_convertors={
        'status': JobStatus.find_case_insensitive
    }
)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class JobState:
    status: JobStatus  # The ID of the current step in the Job's lifecycle
    scheduling: JobStateScheduling  # mandatory, but content can all be None
    event_times: JobEventTimes  # mandatory, but content can be empty
    resources: Optional[JobStateResources] = None  # only filled in once job is at least STARTING
    final_usage_statistics: Optional[GPULabUsageStatistics] = None

    # updatable fields: FIELDNAME_PORT_MAPPINGS, FIELDNAME_GPU_INFO, FIELDNAME_END_DATE, FIELDNAME_SUMMARY_STATISTICS

    def sanitized_copy(self, logged_in=True, same_project=False) -> 'JobState':
        # most is public here
        return JobState(
            status=self.status,
            resources=self.resources.sanitized_copy(logged_in, same_project) if self.resources else None,
            scheduling=self.scheduling.sanitized_copy(logged_in, same_project),
            event_times=self.event_times.sanitized_copy(logged_in, same_project),
            final_usage_statistics=self.final_usage_statistics.make_copy() if self.final_usage_statistics and logged_in else None,
        )

    def make_compatible_with(self, gpulab_api_version: str) -> 'JobState':
        """
        Return a version of this that is backwards compatible with version 3.X.
        :param gpulab_api_version: version to be compatible with.
        :return:
        """
        if gpulab_api_version == '3.1':
            return self
        else:
            assert gpulab_api_version == '3.0'
            return JobState(
                status=self.status,
                resources=self.resources,
                scheduling=self.scheduling.make_compatible_with(gpulab_api_version),
                event_times=self.event_times,
                final_usage_statistics=self.final_usage_statistics,
            )


# @dataclass_json_hack_nested_from_dict  # needed for JobRequest.JobRequestResources and JobRequest.JobRequestDocker
@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
@dataclass_multiline_repr
class Job:
    # Note: Job ID is a 36 char UUID4 (thus including the hyphens)
    name: str
    deployment_environment: str
    request: JobRequest
    uuid: Optional[str] = None
    description: Optional[str] = None
    # Note: Owner is mandatory, except for the Job specified by the user.
    #       The client will add the owner info based on the PEM and specified project,
    #       before sending the Job to GPULab master.
    #       GPULab will check the JobOwner user against the authorized URN
    owner: Optional[JobOwner] = None
    state: Optional[JobState] = None
    restart_info: Optional[RestartInfo] = None

    def __post_init__(self):
        if self.uuid and not is_valid_job_id(self.uuid):
            raise ValueError('Invalid Job UUID "{}"'.format(self.uuid))
        if self.uuid and not self.restart_info:
            # restart_info is known explicitly for jobs with uuid that do not have it.
            # to make things auto-consistent, we add it here automatically
            # (Job is still "frozen", since this is only set during init.)
            super().__setattr__('restart_info', RestartInfo(initial_job_uuid=self.uuid, restart_count=0))

    # backward compatible check if job is "stable" aka "production"
    @property
    def is_production(self) -> bool:
        return self.deployment_environment in ['stable', 'prod', 'production']

    def replace_event_times_attrs(self, **kwargs) -> 'Job':
        assert self.state
        new_event_times = dataclasses.replace(self.state.event_times, **kwargs)
        new_state = dataclasses.replace(self.state, event_times=new_event_times)
        return dataclasses.replace(self, state=new_state)

    def replace_request_resources_attrs(self, **kwargs) -> 'Job':
        assert self.request and self.request.resources
        new_resources = dataclasses.replace(self.request.resources, **kwargs)
        new_request = dataclasses.replace(self.request, resources=new_resources)
        return dataclasses.replace(self, request=new_request)

    def replace_request_scheduling_attrs(self, **kwargs) -> 'Job':
        assert self.request and self.request.scheduling
        new_scheduling = dataclasses.replace(self.request.scheduling, **kwargs)
        new_request = dataclasses.replace(self.request, scheduling=new_scheduling)
        return dataclasses.replace(self, request=new_request)

    def replace_request_extra_attrs(self, **kwargs) -> 'Job':
        assert self.request and self.request.extra
        new_extra = dataclasses.replace(self.request.extra, **kwargs)
        new_request = dataclasses.replace(self.request, extra=new_extra)
        return dataclasses.replace(self, request=new_request)

    def replace_owner_attrs(self, **kwargs) -> 'Job':
        if self.owner:
            new_owner = dataclasses.replace(self.owner, **kwargs)
            return dataclasses.replace(self, owner=new_owner)
        else:
            return dataclasses.replace(self, owner=JobOwner(**kwargs))

    def replace_state_scheduling(self, new_scheduling: JobStateScheduling) -> 'Job':
        assert self.state
        new_state = dataclasses.replace(self.state, scheduling=new_scheduling)
        return dataclasses.replace(self, state=new_state)

    def add_halt_info(self, halt_info: HaltInfo) -> 'Job':
        new_scheduling = dataclasses.replace(
            self.state.scheduling,
            halt_events=self.state.scheduling.halt_events + [halt_info]
        )
        new_state = dataclasses.replace(self.state, scheduling=new_scheduling)
        return dataclasses.replace(self, state=new_state)

    def replace_state_scheduling_attrs(self, **kwargs) -> 'Job':
        assert self.state
        new_scheduling = dataclasses.replace(self.state.scheduling, **kwargs)
        new_state = dataclasses.replace(self.state, scheduling=new_scheduling)
        return dataclasses.replace(self, state=new_state)

    def replace_state_final_usage_statistics(self, final_usage_statistics: GPULabUsageStatistics) -> 'Job':
        assert self.state
        new_state = dataclasses.replace(self.state, final_usage_statistics=final_usage_statistics)
        return dataclasses.replace(self, state=new_state)

    def replace_state_resources(self, new_resources: JobStateResources) -> 'Job':
        assert self.state
        new_state = dataclasses.replace(self.state, resources=new_resources)
        return dataclasses.replace(self, state=new_state)

    def replace_state_resources_fields(self, **kwargs) -> 'Job':
        assert self.state
        new_resources = dataclasses.replace(self.state.resources, **kwargs)
        new_state = dataclasses.replace(self.state, resources=new_resources)
        return dataclasses.replace(self, state=new_state)

    def sanitized_copy(self, logged_in=True, same_project=False) -> 'Job':
        """copy with removed confidential data
        :param logged_in: sanitized copy for logged in user, or for anonymous user?
        :param same_project: sanitized copy for user in same project, or for someone else?
        """
        copy = Job(
            uuid=self.uuid,
            name=self.name if same_project or self.name == 'JupyterHub-singleuser' else ('job-'+self.uuid[:6] if self.uuid else 'job'),
            deployment_environment=self.deployment_environment,
            request=self.request.sanitized_copy(logged_in, same_project),
            description=self.description if logged_in and same_project else None,
            owner=self.owner.sanitized_copy(logged_in, same_project),
            state=self.state.sanitized_copy(logged_in, same_project),
            restart_info=self.restart_info,
        )
        return copy

    def make_compatible_with(self, gpulab_api_version: Optional[str]) -> 'Job':
        """
        Return a version of this job that is backwards compatible with version 3.X.
        :param gpulab_api_version: version to be compatible with. If None, 3.0 is assumed.
        :return:
        """
        if gpulab_api_version == '3.1':
            return self
        else:
            return Job(
                uuid=self.uuid,
                name=self.name,
                deployment_environment=self.deployment_environment,
                request=self.request,
                description=self.description,
                owner=self.owner,
                state=self.state.make_compatible_with('3.0')
            )

    def is_fully_sanitized(self) -> bool:
        return self == self.sanitized_copy()

    def is_partially_sanitized(self) -> bool:
        """
        :return: True if this job is at least partially sanitized
        """
        return self.is_fully_sanitized() or \
               self.owner.is_partially_sanitized() or \
               self.request.docker.image == 'hidden'

    def get_backward_compat_version(self):
        if self.deployment_environment == 'staging':
            return 'dev'
        if self.deployment_environment in ['production', 'prod']:
            return 'stable'
        return self.deployment_environment

    @property
    def short_uuid(self) -> Optional[str]:
        if not self.uuid:
            return None
        if '-' in self.uuid:
            return self.uuid[:self.uuid.index('-')]
        return self.uuid
