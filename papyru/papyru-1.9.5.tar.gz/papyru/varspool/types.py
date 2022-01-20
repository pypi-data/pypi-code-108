from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from papyru.utils import PAPEnum


class JobStatus(PAPEnum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    FAILED_TEMPORARILY = 'failed_temporarily'
    FAILED = 'failed'
    DONE = 'done'


@dataclass
class JobStatusEntry:
    status: JobStatus
    checksum: Optional[str] = None
    date: Optional[datetime] = None
    data: Optional[dict] = None

    @staticmethod
    def from_dict(entry_dict: dict):
        date = (datetime.fromisoformat(entry_dict['date'])
                if entry_dict.get('date', None) is not None
                else None)
        return JobStatusEntry(status=JobStatus(entry_dict['status']),
                              checksum=entry_dict.get('checksum'),
                              date=date,
                              data=entry_dict.get('data'))

    def to_dict(self):
        return {
            'status': str(self.status),
            **({'checksum': self.checksum}
               if self.checksum is not None else {}),
            **({'date': self.date.isoformat()}
               if self.date is not None else {}),
            **({'data': self.data} if self.data is not None else {})
        }


@dataclass
class JobStatusHistory:
    location: str
    items: List[JobStatusEntry]

    @staticmethod
    def from_dict(history_dict: dict):
        return JobStatusHistory(location=history_dict['location'],
                                items=list(map(JobStatusEntry.from_dict,
                                               history_dict['items'])))

    def to_dict(self):
        return {
            'location': self.location,
            'items': list(map(lambda it: it.to_dict(),
                              self.items)),
        }


@dataclass
class Job:
    id: int
    status_history: JobStatusHistory

    @staticmethod
    def from_dict(job_dict: dict):
        return Job(id=job_dict['id'],
                   status_history=JobStatusHistory.from_dict(
                       job_dict['status_history']))

    def to_dict(self):
        return {
            'id': self.id,
            'status_history': self.status_history.to_dict(),
        }


class JobResult:
    def __init__(self,
                 status: JobStatus,
                 data: dict):
        self.status = status
        self.data = data

    def __str__(self):
        return ('%s(status=%s, data=%s)'
                % (type(self).__name__, self.status, self.data))

    def to_status_entry(self) -> JobStatusEntry:
        return JobStatusEntry(status=self.status,
                              data=self.data)
