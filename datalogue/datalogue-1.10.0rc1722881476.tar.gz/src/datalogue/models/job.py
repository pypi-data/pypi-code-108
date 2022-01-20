from datetime import datetime
from uuid import UUID
from typing import Union, Optional, List

from dateutil.parser import parse

from datalogue.dtl_utils import SerializableStringEnum
from datalogue.dtl_utils import _parse_list, _parse_uuid
from datalogue.errors import _enum_parse_error, DtlError


class JobStatus(SerializableStringEnum):
    Scheduled = "Scheduled"
    Defined = "Defined"
    Running = "Running"
    Succeeded = "Succeeded"
    Failed = "Failed"
    Unknown = "Unknown"
    Cancelled = "Cancelled"

    @staticmethod
    def parse_error(s: str) -> str:
        return DtlError(_enum_parse_error("job status", s))

    @staticmethod
    def job_status_from_str(string: str) -> Union[DtlError, "JobStatus"]:
        return SerializableStringEnum.from_str(JobStatus)(string)


class JobType(SerializableStringEnum):
    Pipeline = "Pipeline"
    Sampling = "Sampling"

    @staticmethod
    def parse_error(s: str) -> str:
        return DtlError(_enum_parse_error("job type", s))

    @staticmethod
    def job_type_from_str(string: str) -> Union[DtlError, "JobType"]:
        return SerializableStringEnum.from_str(JobType)(string)


class Job:
    def __init__(
        self,
        id: UUID,
        pipeline_id: Optional[UUID],
        run_at: datetime,
        status: "JobStatus",
        job_type: Optional["JobType"],
        created_by: UUID,
        errors: Optional[str],
        started_at: Optional[datetime],
        ended_at: Optional[datetime],
        percentage_progress: Optional[float],
        average_records_speed: Optional[float],
        estimated_processed_records_count: Optional[int],
        total_source_records: Optional[int],
        dropped_record_count: Optional[int],
        wait_on: List[UUID] = [],
        abort_if_overlong: bool = True,
        frequency: Optional[str] = None,
        parent_job_id: Optional[UUID] = None,
        created_by_email: Optional[str] = None,
        duration: Optional[int] = None,
        source_connection_id: Optional[UUID] = None,
        source_connection_name: Optional[str] = None,
        source_resource_name: Optional[str] = None,
        target_connection_id: Optional[UUID] = None,
        target_connection_name: Optional[str] = None,
        target_resource_name: Optional[str] = None,
        runner_id: str = "",
    ):
        self.id = id
        self.pipeline_id = pipeline_id
        self.run_at = run_at
        self.status = status
        self.job_type = job_type
        self.created_by = created_by
        self.errors = errors
        self.ended_at = ended_at
        self.started_at = started_at
        self.percentage_progress = percentage_progress
        self.average_records_speed = average_records_speed
        self.estimated_processed_records_count = estimated_processed_records_count
        self.total_source_records = total_source_records
        self.dropped_record_count = dropped_record_count
        self.wait_on = wait_on
        self.abort_if_overlong = abort_if_overlong
        self.frequency = frequency
        self.parent_job_id = parent_job_id
        self.created_by_email = created_by_email
        self.duration = duration
        self.source_connection_id = source_connection_id
        self.source_connection_name = source_connection_name
        self.source_resource_name = source_resource_name
        self.target_connection_id = target_connection_id
        self.target_connection_name = target_connection_name
        self.target_resource_name = target_resource_name
        self.runner_id = runner_id

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"id= {self.id!r}, "
            f"pipeline_id= {self.pipeline_id!r}, "
            f"status= {self.status!r}, "
            f"job_type= {self.job_type!r}, "
            f"run_at= {self.run_at!r}, "
            f"wait_on= {self.wait_on!r}, "
            f"created_by= {self.created_by!r}, "
            f"created_by_email= {self.created_by_email!r}, "
            f"errors= {self.errors!r}, "
            f"ended_at= {self.ended_at!r}, "
            f"started_at= {self.started_at!r}, "
            f"abort_if_overlong= {self.abort_if_overlong}, "
            f"frequency= {self.frequency}, "
            f"parent_job_id= {self.parent_job_id}, "
            f"percent_progress= {self.percentage_progress!r}, "
            f"average_records_speed= {self.average_records_speed!r}, "
            f"estimated_processed_records_count= {self.estimated_processed_records_count!r}, "
            f"total_source_records= {self.total_source_records!r}, "
            f"duration= {self.duration!r}, "
            f"dropped_record_count= {self.dropped_record_count!r}, "
            f"source_connection_id= {self.source_connection_id!r}, "
            f"source_connection_name= {self.source_connection_name!r}, "
            f"source_resource_name= {self.source_resource_name!r}, "
            f"target_connection_id= {self.target_connection_id!r}, "
            f"target_connection_name= {self.target_connection_name!r}, "
            f"target_resource_name= {self.target_resource_name!r},"
            f"runner_id= {self.runner_id!r})"
        )

    @classmethod
    def _from_payload(cls, json: dict) -> Union[DtlError, "Job"]:
        """
        Parses a dictionary into a Job object. Currently configured
        to parse the (latest) job data model returned by v2 jobs service.
        """
        job_id = json.get("id")
        if job_id is None:
            return DtlError("Job object should have a 'id' property")
        else:
            try:
                job_id = UUID(job_id)
            except ValueError:
                return DtlError("'id' field was not a proper uuid")

        status = json.get("status")
        if status is None:
            return DtlError("Job object should have a 'status' property")
        else:
            status = JobStatus.job_status_from_str(status)
            if isinstance(status, DtlError):
                return status

        job_type = json.get("jobType")
        if job_type is None:
            return DtlError("Job object should have a 'jobType' property")
        else:
            job_type = JobType.job_type_from_str(job_type)
            if isinstance(job_type, DtlError):
                return job_type

        run_at = json.get("scheduledAt")
        if run_at is None:
            return DtlError("Job object should have a 'runDate' property")
        else:
            try:
                run_at = parse(run_at)
            except ValueError:
                return DtlError("The 'runDate' could not be parsed as a valid date")

        created_by = json.get("owner")
        if created_by is None:
            return DtlError("Job object should have a 'owner' property")
        else:
            try:
                created_by = UUID(created_by)
            except ValueError:
                return DtlError("'owner' was not a proper uuid")

        job_type = json.get("jobType")
        if job_type is None:
            return DtlError("Job object should have a 'jobType' property")
        else:
            job_type = JobType.job_type_from_str(job_type)
            if isinstance(job_type, DtlError):
                return job_type

        # optional fields now

        ### Temporary optional fields ###
        wait_on = json.get("waitOn")
        if wait_on is not None:
            wait_on = _parse_list(_parse_uuid)(wait_on)
            if isinstance(wait_on, DtlError):
                return wait_on

        # make op metrics optional for now
        average_records_speed = json.get("averageRecordsSpeed")
        if average_records_speed is not None:
            try:
                average_records_speed = float(average_records_speed)
            except ValueError:
                return DtlError("'averageRecordsSpeed' was not a proper number")

        percentage_progress = json.get("percentage")
        if percentage_progress is not None:
            try:
                percentage_progress = float(percentage_progress)
            except ValueError:
                return DtlError("'percentage' was not a proper number")

        total_source_records = json.get("totalSourceRecords")
        if total_source_records is not None:
            try:
                total_source_records = int(total_source_records)
            except ValueError:
                return DtlError("'totalSourceRecords' was not a proper int")

        estimated_processed_records_count = json.get("records")
        if estimated_processed_records_count is not None:
            try:
                estimated_processed_records_count = int(estimated_processed_records_count)
            except ValueError:
                return DtlError("'records' was not a proper int")

        errors = json.get("details")

        parent_job_id = json.get("parentJobId")

        abort_if_overlong = json.get("abortIfOverlong")

        created_by_email = json.get("ownerEmail")

        # ended_at is optional
        ended_at = json.get("endTime")
        if ended_at is not None:
            try:
                ended_at = parse(ended_at)
            except ValueError:
                return DtlError("The 'endTime' could not be parsed as a valid date")

        # started_at is optional
        started_at = json.get("startTime")
        if started_at is not None:
            try:
                started_at = parse(started_at)
            except ValueError:
                return DtlError("The 'startTime' could not be parsed as a valid date")

        duration = json.get("duration")
        if duration is not None:
            try:
                duration = int(duration)
            except ValueError:
                return DtlError("'duration' was not a proper int")

        dropped_records = json.get("droppedRecords")
        if dropped_records is not None:
            try:
                dropped_records = int(dropped_records)
            except ValueError:
                return DtlError("'droppedRecords' was not a proper int")

        frequency = json.get("scheduleFrequency")
        if frequency is not None:
            try:
                frequency = int(frequency)
            except ValueError:
                return DtlError("'scheduleFrequency' was not a proper int")

        pipeline_id = json.get("pipelineId")
        if pipeline_id is not None:
            try:
                pipeline_id = UUID(pipeline_id)
            except ValueError:
                return DtlError("'pipelineId' field was not a proper uuid")

        source_connection_id = json.get("sourceId")
        if source_connection_id is not None:
            try:
                source_connection_id = UUID(source_connection_id)
            except ValueError:
                return DtlError("The 'sourceId' was not a proper uuid")

        source_connection_name = json.get("sourceName")
        source_resource_name = json.get("sourceResourceName")

        target_connection_id = json.get("targetId")
        if target_connection_id is not None:
            try:
                target_connection_id = UUID(target_connection_id)
            except ValueError:
                return DtlError("The 'targetId' was not a proper uuid")

        target_connection_name = json.get("targetName")
        target_resource_name = json.get("targetResourceName")
        runner_id = json.get("runnerId")

        return cls(
            id=job_id,
            pipeline_id=pipeline_id,
            run_at=run_at,
            status=status,
            job_type=job_type,
            created_by=created_by,
            errors=errors,
            started_at=started_at,
            ended_at=ended_at,
            percentage_progress=percentage_progress,
            average_records_speed=average_records_speed,
            estimated_processed_records_count=estimated_processed_records_count,
            total_source_records=total_source_records,
            duration=duration,
            dropped_record_count=dropped_records,
            wait_on=wait_on,
            abort_if_overlong=abort_if_overlong,
            frequency=frequency,
            parent_job_id=parent_job_id,
            created_by_email=created_by_email,
            source_connection_id=source_connection_id,
            source_connection_name=source_connection_name,
            source_resource_name=source_resource_name,
            target_connection_id=target_connection_id,
            target_connection_name=target_connection_name,
            target_resource_name=target_resource_name,
            runner_id=runner_id,
        )

    @classmethod
    def _from_payload_v1(cls, json: dict) -> Union[DtlError, "Job"]:
        """
        Parses a dictionary into a Job object. Currently configured
        to parse the old job data model, which is still used by the streams api.
        Should be only used within the pipeline client(for now)
        """
        job_id = json.get("jobId")
        if job_id is None:
            return DtlError("Job object should have a 'jobId' property")
        else:
            try:
                job_id = UUID(job_id)
            except ValueError:
                return DtlError("'jobId' field was not a proper uuid")

        pipeline_id = json.get("streamId")
        if pipeline_id is not None:
            try:
                pipeline_id = UUID(pipeline_id)
            except ValueError:
                return DtlError("'streamId' field was not a proper uuid")

        run_at = json.get("runDate")
        if run_at is None:
            return DtlError("Job object should have a 'runDate' property")
        else:
            try:
                run_at = parse(run_at)
            except ValueError:
                return DtlError("The 'runDate' could not be parsed as a valid date")

        status = json.get("status")
        if status is None:
            return DtlError("Job object should have a 'status' property")
        else:
            status = JobStatus.job_status_from_str(status)
            if isinstance(status, DtlError):
                return status

        remaining_time_millis = json.get("remainingTimeInMillis")
        if remaining_time_millis is not None:
            try:
                remaining_time_millis = int(remaining_time_millis)
            except ValueError:
                return DtlError("'remainingTimeInMillis' was not a proper int")

        percentage_progress = json.get("percentage")
        if percentage_progress is None:
            percentage_progress = None
        else:
            try:
                percentage_progress = float(percentage_progress)
            except ValueError:
                return DtlError("'percentage' was not a proper number")

        created_by = json.get("createdBy")
        if created_by is None:
            return DtlError("Job object should have a 'createdBy' property")
        else:
            try:
                created_by = UUID(created_by)
            except ValueError:
                return DtlError("'createdBy' was not a proper uuid")

        # details is optional
        errors = json.get("details")

        # ended_at is optional
        ended_at = json.get("endDate")
        if ended_at is not None:
            try:
                ended_at = parse(ended_at)
            except ValueError:
                return DtlError("The 'endDate' could not be parsed as a valid date")

        # started_at is optional
        started_at = json.get("startDate")
        if started_at is not None:
            try:
                started_at = parse(started_at)
            except ValueError:
                return DtlError("The 'startDate' could not be parsed as a valid date")

        wait_on = json.get("waitOn")
        if wait_on is not None:
            wait_on = _parse_list(_parse_uuid)(wait_on)
            if isinstance(wait_on, DtlError):
                return wait_on
        else:
            return DtlError("Job object should have a 'waitOn' property")

        frequency = None
        if json.get("intervalInSec") is not None:
            # TODO rename in scout so we have the same naming in both
            frequency = str(json.get("intervalInSec"))

        parent_job_id = None
        if json.get("parentJobId") is not None:
            parent_job_id = json.get("parentJobId")

        abort_if_overlong = json.get("abortIfOverlong")

        average_records_speed = json.get("averageRecordsSpeed")
        if average_records_speed is None:
            return DtlError("Job object should have a 'averageRecordsSpeed' property")
        else:
            try:
                average_records_speed = float(average_records_speed)
            except ValueError:
                return DtlError("'averageRecordsSpeed' was not a proper number")

        current_records_speed = json.get("currentRecordsSpeed")
        if current_records_speed is None:
            return DtlError("Job object should have a 'currentRecordsSpeed' property")
        else:
            try:
                current_records_speed = float(current_records_speed)
            except ValueError:
                return DtlError("'currentRecordsSpeed' was not a proper number")

        estimated_processed_records_count = json.get("estimatedProcessedRecordsCount")
        if estimated_processed_records_count is None:
            return DtlError("Job object should have a 'estimatedProcessedRecordsCount' property")
        else:
            try:
                estimated_processed_records_count = int(estimated_processed_records_count)
            except ValueError:
                return DtlError("'estimatedProcessedRecordsCount' was not a proper int")

        average_bytes_speed = json.get("averageBytesSpeed")
        if average_bytes_speed is not None:
            try:
                average_bytes_speed = float(average_bytes_speed)
            except ValueError:
                return DtlError("'averageBytesSpeed' was not a proper number")

        current_bytes_speed = json.get("currentBytesSpeed")
        if current_bytes_speed is not None:
            try:
                current_bytes_speed = float(current_bytes_speed)
            except ValueError:
                return DtlError("'currentBytesSpeed' was not a proper number")

        estimated_processed_bytes_count = json.get("estimatedProcessedBytesCount")
        if estimated_processed_bytes_count is not None:
            try:
                estimated_processed_bytes_count = int(estimated_processed_bytes_count)
            except ValueError:
                return DtlError("'estimatedProcessedBytesCount' was not a proper int")

        total_source_records = json.get("totalSourceRecords")
        if total_source_records is not None:
            try:
                total_source_records = int(total_source_records)
            except ValueError:
                return DtlError("'totalSourceRecords' was not a proper int")

        total_source_bytes = json.get("totalSourceBytes")
        if total_source_bytes is not None:
            try:
                total_source_bytes = int(total_source_bytes)
            except ValueError:
                return DtlError("'totalSourceBytes' was not a proper int")

        dropped_records = json.get("rejectedRecordsCount")
        if dropped_records is not None:
            try:
                dropped_records = int(dropped_records)
            except ValueError:
                return DtlError("'rejectedRecordsCount' was not a proper int")

        job = cls(
            id=job_id,
            pipeline_id=pipeline_id,
            job_type=None,
            run_at=run_at,
            status=status,
            percentage_progress=percentage_progress,
            created_by=created_by,
            errors=errors,
            started_at=started_at,
            ended_at=ended_at,
            average_records_speed=average_records_speed,
            estimated_processed_records_count=estimated_processed_records_count,
            total_source_records=total_source_records,
            wait_on=wait_on,
            abort_if_overlong=abort_if_overlong,
            frequency=frequency,
            parent_job_id=parent_job_id,
            dropped_record_count=dropped_records,
        )
        return job
