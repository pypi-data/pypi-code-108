from enum import Enum

from vectice.entity._versioned_entity import VersionedEntity


class Run(VersionedEntity):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def status(self) -> str:
        return str(self["status"])

    @property
    def job_id(self) -> int:
        return int(self["jobId"])

    @property
    def start_date(self) -> str:
        return str(self["startDate"])

    @property
    def end_date(self) -> str:
        return str(self["endDate"])

    @property
    def duration(self) -> int:
        return int(self["duration"])

    @property
    def system_name(self) -> str:
        return str(self["systemName"])

    @property
    def metadata_source(self) -> str:
        return str(self["metadataSource"])


class JobRunStatus(Enum):
    SCHEDULED = "SCHEDULED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"
