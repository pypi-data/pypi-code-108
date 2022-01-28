import os
from uuid import uuid4

from ..basis.timestamped_immutable import TimestampedImmutable
from ..procedures.procedure import Procedure


class Task(TimestampedImmutable):
    def __init__(self, procedure: Procedure, is_source_blocking: bool = False):
        super(Task, self).__init__()
        self.task_id = str(uuid4())
        self.procedure = procedure
        self.source_pid = os.getpid()
        self.is_source_blocking = is_source_blocking

    def __eq__(self, other):
        return self.task_id == other.task_id

    def __hash__(self):
        return hash(self.task_id)
