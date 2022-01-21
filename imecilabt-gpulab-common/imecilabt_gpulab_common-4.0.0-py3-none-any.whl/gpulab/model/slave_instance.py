from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict

from stringcase import camelcase

from imecilabt.gpulab.model.slave_info2 import SlaveInstanceBase
from dataclass_dict_convert import dataclass_dict_convert, dataclass_auto_type_check, parse_rfc3339, \
    ignore_unknown_fields


#
# These enums and dataclasses are used by the supervisor.
#


class SlaveInstanceState(Enum):
    DEAD = 0  # no dir/files, or some critical files missing
    STOPPED = 1  # dir/files ok, but not running
    RUNNING = 2  # Currently running (and config does not have shutdown)
    STOPPING = 3  # Currently shutting down (running and config has shutdown)
    UPDATING = 4  # Updating config
    HANG = 5  # RUNNING, but watchdog alive not reported -> internal hang!
    MUST_DELETE = 6  # all files must be deleted (will result in DEAD, but seperate explicit state for safety)


class ResourceState(Enum):
    UNKNOWN = 0
    FREE_ALL = 1
    USED_OTHER = 2
    USED_DEAD = 3
    FREE_SELF = 4
    USED_SELF = 5
    CONFLICT = 6
    WAIT_AFTER_DEAD_CLAIM_CLEANUP = 10


class ResourceType(Enum):
    GPU = 0
    CPU = 1


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass_auto_type_check
@dataclass(frozen=True)
class SlaveInstanceResource:
    type: ResourceType
    id: int
    state: ResourceState


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass_auto_type_check
@dataclass(frozen=True)
class SlaveInstance(SlaveInstanceBase):
    deployment_environment: str
    name: str
    instance_id: str
    state: SlaveInstanceState

    aliases: List[str] = field(default_factory=list)
    comment: Optional[str] = None
    host: Optional[str] = None

    pid: Optional[int] = None
    cluster_id: Optional[int] = None
    commit_id: Optional[str] = None
    commit_date: Optional[datetime] = None
    branch: Optional[str] = None
    config: Optional[Dict] = None
    base_dir: Optional[str] = None
    dir: Optional[str] = None
    config_filename: Optional[str] = None
    pid_file: Optional[str] = None
    pid_create_time: Optional[datetime] = None
    venv_name: Optional[str] = None
    repo_dir: Optional[str] = None
    instance_create_date: Optional[datetime] = None

    updated: Optional[datetime] = None
    resources: List[SlaveInstanceResource] = field(default_factory=list)

    def __post_init__(self):
        # enforce tz aware timestamps
        assert not self.commit_date or self.commit_date.tzinfo is not None
        assert not self.pid_create_time or self.pid_create_time.tzinfo is not None
        assert not self.instance_create_date or self.instance_create_date.tzinfo is not None

    # alias for backward compatibility
    @property
    def hash_id(self):
        return self.instance_id

    # for backward compatibility
    @property
    def hash_nick(self):
        return self.instance_id[0:15]

    @classmethod
    def from_any_dict(cls, d: Dict) -> 'SlaveInstance':
        if SlaveInstance.is_old_dict(d):
            return SlaveInstance.from_old_dict(d)
        else:
            return SlaveInstance.from_dict(d, on_unknown_field_override=ignore_unknown_fields)

    # doesn't overwrite auto-generated!
    # @staticmethod
    # def from_dict_list(s_dict_lst: List[Dict]) -> List['SlaveInstance']:
    #     return [SlaveInstance.from_any_dict(d) for d in s_dict_lst]

    @staticmethod
    def is_old_dict(d: Dict):
        return 'slave_name' in d or 'hash_id' in d

    @classmethod
    def from_old_dict(cls, d: Dict) -> 'SlaveInstance':
        return SlaveInstance(
            name=d.get('slave_name'),
            instance_id=d.get('hash_id'),
            deployment_environment=d.get('deployment_environment'),
            commit_id=d.get('commit_id'),
            commit_date=parse_rfc3339(d.get('commit_date'), none_if_empty_tz=True),
            branch=d.get('branch'),
            base_dir=d.get('base_dir'),
            dir=d.get('dir'),
            config=d.get('config'),
            config_filename=d.get('config_filename'),
            pid_file=d.get('pid_file'),
            pid=d.get('pid'),
            pid_create_time=parse_rfc3339(d.get('pid_create_time'), none_if_empty_tz=True),
            venv_name=d.get('venv_name'),
            repo_dir=d.get('repo_dir'),
            instance_create_date=parse_rfc3339(d.get('instance_create_date'), none_if_empty_tz=True),
            state=SlaveInstanceState[d.get('state')] if 'state' in d else None,

            cluster_id=0,  # fallback, because not present
            host=None  # fallback, because not present
        )
