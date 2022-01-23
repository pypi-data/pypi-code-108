from enum import Enum
from typing import Optional, List

from google.protobuf import empty_pb2

from qm.QmPendingJob import QmPendingJob
from qm._errors import FailedToAddJobToQueueException
from qm.pb.frontend_pb2 import (
    JobQueryParams,
    QueryValueMatcher,
    AddToQueueRequest,
    QueuePosition,
    AddCompiledToQueueRequest,
)
import qm.pb.frontend_pb2
from qm.pb.inc_qua_pb2 import QuaProgram
from qm.logger import logger
from qm.program import _Program
from qm.program._execution_overrides_schema import ExecutionOverridesSchema
from qm.utils import _level_map, _set_compiler_options


class JobNotFoundError(Exception):
    pass


class _QueuePosition(Enum):
    Start = 1
    End = 2


class QmQueue(object):
    def __init__(
        self, machine, qmm: "qm.QuantumMachinesManager.QuantumMachinesManager"
    ):
        self._machine = machine
        self._qmm = qmm

    def _get_pending_jobs(
        self, job_id: str = None, position: int = None, user_id: str = None
    ) -> List[QmPendingJob]:
        request = JobQueryParams()
        request.quantumMachineId = self._machine.id
        if job_id is not None:
            job_query_value_matcher = QueryValueMatcher()
            job_query_value_matcher.value = job_id
            request.jobId.CopyFrom(job_query_value_matcher)
        if position is not None:
            request.position.value = position
        if user_id is not None:
            user_query_value_matcher = QueryValueMatcher()
            user_query_value_matcher.value = user_id
            request.userId.CopyFrom(user_query_value_matcher)

        response = self._qmm._frontend.GetPendingJobs(request)
        jobs = [
            (i, response.pendingJobs[i].positionInQueue)
            for i in list(response.pendingJobs)
        ]
        jobs.sort(key=lambda it: it[1])
        result = [
            QmPendingJob(pending_job_id, self._machine, self._qmm)
            for pending_job_id, pos in jobs
        ]
        return result

    def add(self, program: _Program, **kwargs) -> QmPendingJob:
        """
        Adds a QmJob to the queue.
        Programs in the queue will play as soon as possible.

        :param program: A QUA program
        :return: The QmJob

        Example::

        >>> qm.queue.add(program)  # adds at the end of the queue
        >>> qm.queue.insert(program, position)  # adds at position
        """
        return self._insert(program, _QueuePosition.End, **kwargs)

    def add_compiled(self, program_id: str, overrides=None) -> QmPendingJob:
        """
        Adds a compiled QUA program to the end of the queue, optionally
        overriding the values of analog waveforms defined in the program.
        Programs in the queue will play as soon as possible.
        For a detailed explanation see
        `Precompile Jobs <https://qm-docs.qualang.io/guides/features.html#precompile-jobs>`__.

        :param program_id: A QUA program ID returned from the compile function
        :param overrides: Object containing Waveforms to run the program with

        Example::

        >>> program_id = qm.compile(...)
        >>> pending_job = qm.queue.add_compiled(program_id, overrides={
        >>>     'waveforms': {
        >>>         'my_arbitrary_waveform': [0.1, 0.2, 0.3],
        >>>         'my_constant_waveform': 0.2
        >>>     }
        >>> })
        >>> job = pending_job.wait_for_execution()
        """
        if not overrides:
            overrides = {}

        return self._insert_compiled(program_id, overrides)

    def add_to_start(self, program: _Program, **kwargs) -> QmPendingJob:
        """
        Adds a QMJob to the start of the queue.
        Programs in the queue will play as soon as possible.

        :param program: A QUA program
        :return: The QmJob

        """
        return self._insert(program, _QueuePosition.Start, **kwargs)

    def _insert(
        self, program: _Program, position: _QueuePosition, **kwargs
    ) -> QmPendingJob:
        return self._insert_pb(
            program.build(self._machine._pb_config), position, **kwargs
        )

    def _parse_add_compiled_to_queue_response(self, response) -> QmPendingJob:
        job_id = response.jobId

        for err in response.errors:
            logger.error(err.message)

        if not response.ok:
            logger.error("Job " + job_id + " failed. Failed to execute program.")
            raise FailedToAddJobToQueueException(job_id)

        return QmPendingJob(job_id, self._machine, self._qmm)

    def _parse_add_to_queue_response(self, response) -> QmPendingJob:
        messages = [(_level_map[msg.level], msg.message) for msg in response.messages]

        job_id = response.jobId

        for lvl, msg in messages:
            logger.log(lvl, msg)

        if not response.ok:
            logger.error("Job " + job_id + " failed. Failed to execute program.")
            raise FailedToAddJobToQueueException(job_id)

        return QmPendingJob(job_id, self._machine, self._qmm)

    def _insert_compiled(self, program_id, overrides):
        request_queue_position = QueuePosition()
        request_queue_position.end.CopyFrom(empty_pb2.Empty())

        request = AddCompiledToQueueRequest(
            queuePosition=request_queue_position,
            quantumMachineId=self._machine.id,
            programId=program_id,
            executionOverrides=ExecutionOverridesSchema().load(overrides),
        )

        logger.info("Sending pre-compiled program to QOP")

        response = self._qmm._frontend.AddCompiledToQueue(request)
        return self._parse_add_compiled_to_queue_response(response)

    def _insert_pb(
        self, program: QuaProgram, position: _QueuePosition, **kwargs
    ) -> QmPendingJob:
        request = AddToQueueRequest()
        request.quantumMachineId = self._machine.id
        request.highLevelProgram.CopyFrom(program)

        _set_compiler_options(request, **kwargs)

        queue_position = QueuePosition()
        if position == _QueuePosition.Start:
            queue_position.start.CopyFrom(empty_pb2.Empty())
        elif position == _QueuePosition.End:
            queue_position.end.CopyFrom(empty_pb2.Empty())

        logger.info("Sending program to QOP")

        request.queuePosition.CopyFrom(queue_position)
        response = self._qmm._frontend.AddToQueue(request)
        return self._parse_add_to_queue_response(response)

    @property
    def count(self):
        """
        Get the number of jobs currently on the queue

        :return: The number of jobs in the queue

        Example::

        >>> qm.queue.count
        """
        return len(self._get_pending_jobs())

    def __len__(self):
        return self.count

    @property
    def pending_jobs(self) -> List[QmPendingJob]:
        """
        Returns all currently pending jobs

        :return: A list of all of the currently pending jobs
        """
        return self._get_pending_jobs()

    def get(self, job_id) -> QmPendingJob:
        """
        Get a pending job object by job_id

        :param job_id: a QMJob id
        :return: The pending job

        Example::

        >>> qm.queue.get(job_id)

        """
        jobs = self._get_pending_jobs(job_id)
        if len(jobs) == 0:
            raise JobNotFoundError()
        return jobs[0]

    def get_at(self, position: int) -> QmPendingJob:
        """
        Gets the pending job object at the given position in the queue

        :param position: An integer position in queue
        :return: The pending job

        Example::

        >>> qm.queue.get(job_id)

        """
        jobs = self._get_pending_jobs(None, position)
        if len(jobs) == 0:
            raise JobNotFoundError()
        return jobs[0]

    def get_by_user_id(self, user_id: str) -> List[QmPendingJob]:
        return self._get_pending_jobs(None, None, user_id)

    def remove_by_id(self, job_id: str) -> int:
        """
        Removes the pending job object with a specific job id

        :param job_id: a QMJob id
        :return: The number of jobs removed

        Example::

        >>> qm.queue.remove_by_id(job_id)
        """
        if job_id is None or job_id == "":
            raise ValueError("job_id can not be empty")
        return self._remove(job_id=job_id, position=None, user_id=None)

    def remove_by_position(self, position: int) -> int:
        """
        Remove the PendingQmJob object by position in queue

        :param position: position in queue
        :return: The number of jobs removed

        Example::

        >>> qm.queue.remove_by_position(position)

        """
        if position is None or position <= 0:
            raise ValueError("position must be positive")
        return self._remove(job_id=None, position=position, user_id=None)

    def remove_by_user_id(self, user_id: str):
        return self._remove(job_id=None, position=None, user_id=user_id)

    def _remove(
        self,
        job_id: Optional[str] = None,
        position: Optional[int] = None,
        user_id: Optional[str] = None,
    ) -> int:
        request = JobQueryParams()
        request.quantumMachineId = self._machine.id
        if job_id is not None:
            job_query_value_matcher = QueryValueMatcher()
            job_query_value_matcher.value = job_id
            request.jobId.CopyFrom(job_query_value_matcher)

        if position is not None:
            request.position.value = position

        if user_id is not None:
            user_query_value_matcher = QueryValueMatcher()
            user_query_value_matcher.value = user_id
            request.userId.CopyFrom(user_query_value_matcher)

        response = self._qmm._frontend.RemovePendingJobs(request)
        return response.numbersOfJobsRemoved

    def __getitem__(self, position) -> QmPendingJob:
        return self.get_at(position)

    def clear(self) -> int:
        """
        Empties the queue from all pending jobs

        :return: The number of jobs removed
        """
        return self._remove()
