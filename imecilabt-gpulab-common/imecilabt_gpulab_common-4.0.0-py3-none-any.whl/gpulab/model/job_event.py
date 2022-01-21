import datetime
import logging

import dateutil.parser
from enum import Enum
from typing import Optional, Union

from imecilabt.gpulab.model.job import JobState as Job1State
from imecilabt.gpulab.model.job2 import JobStatus as Job2Status
from imecilabt.gpulab.model.job_convert import convert_job1state_to_job2status


class JobEventType(Enum):
    STATUS_CHANGE = 'Status Change'
    DEBUG = 'Debug'
    INFO = 'Info'
    WARN = 'Warning'
    ERROR = 'Error'

_levelToJobEventType = {
    logging.CRITICAL: JobEventType.ERROR,
    logging.ERROR: JobEventType.ERROR,
    logging.WARNING: JobEventType.WARN,
    logging.INFO: JobEventType.INFO,
    logging.DEBUG: JobEventType.DEBUG
}
def logginglevel_to_jobeventype(level: int) -> JobEventType:
    if level in _levelToJobEventType:
        return _levelToJobEventType[level]
    else:
        return JobEventType.DEBUG

class JobEvent:
    def __init__(self,
                 job_id: str,
                 type: JobEventType,
                 time: datetime.datetime = None,
                 new_state1_or_status2: Union[Job1State, Job2Status, None] = None,
                 msg: Optional[str] = None,
                 ):
        assert isinstance(job_id, str)
        self.job_id = job_id
        self.type = type
        self.time = time if time is not None else datetime.datetime.now(datetime.timezone.utc)
        assert new_state1_or_status2 is None or \
               isinstance(new_state1_or_status2, Job1State) or \
               isinstance(new_state1_or_status2, Job2Status)
        self.new_state1_or_status2 = new_state1_or_status2
        self.msg = msg

    def to_dict(self) -> dict:
        res = dict()
        res['job_id'] = self.job_id
        res['type'] = self.type.name if self.type else None
        res['time'] = self.time.isoformat() if self.time else None
        res['new_state'] = self.new_status.name if self.new_status else None
        res['msg'] = self.msg
        return res

    def __str__(self) -> str:
        if self.type == JobEventType.STATUS_CHANGE:
            return f'JobEvent(STATUS_CHANGE, {self.new_status.name if self.new_status else None}, {self.job_id}, {self.time.isoformat() if self.time else None})'
        return f'JobEvent({self.type.name if self.type else None}, {self.msg}, {self.job_id}, {self.time.isoformat() if self.time else None})'

    @property
    def new_status(self) -> Optional[Job2Status]:
        if self.new_state1_or_status2 is None:
            return None
        if isinstance(self.new_state1_or_status2, Job2Status):
            return self.new_state1_or_status2
        if self.new_state1_or_status2:
            return Job2Status.find_case_insensitive(self.new_state1_or_status2.name)
        return None

    # @property
    # def new_state(self):
    #     return Job1State[self.new_state1_or_status2.name] if self.new_state1_or_status2 else None

    @classmethod
    def from_dict(cls, d: dict):
        job_id = d['job_id']
        job_event_type = JobEventType[d['type']] if 'type' in d else None
        job_event_time = dateutil.parser.parse(d['time']) if 'time' in d and d['time'] else None
        msg = d['msg'] if 'msg' in d else None

        if job_event_type == JobEventType.STATUS_CHANGE:
            new_status = d['new_status'] if 'new_status' in d and d['new_status'] else None
            if not new_status:
                new_status = d['new_state'] if 'new_state' in d and d['new_state'] else None
            if new_status:
                try:
                    new_state1_or_status2 = Job2Status.find_case_insensitive(new_status)
                    assert new_state1_or_status2
                except ValueError:
                    new_state1_or_status2 = convert_job1state_to_job2status(Job1State[new_status])
            else:
                new_state1_or_status2 = None
                print(f'JobEvent.from_dict did not find new status in d={d}')
            return cls(job_id, job_event_type, job_event_time, new_state1_or_status2, msg)
        else:
            return cls(job_id, job_event_type, job_event_time, None, msg)
