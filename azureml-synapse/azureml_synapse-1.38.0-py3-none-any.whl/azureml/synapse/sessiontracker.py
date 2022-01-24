# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""SessionTracker module."""

import base64
import threading
import time
from typing import Dict, Tuple
from datetime import datetime

from IPython.display import Image
from dateutil import parser
from six import text_type, binary_type
from sparkmagic.livyclientlib.exceptions import SparkStatementException, LivyUnexpectedStatusException
from sparkmagic.utils.constants import BUSY_SESSION_STATUS, FINAL_STATUS
from sparkmagic.utils.constants import FINAL_STATEMENT_STATUS
from sparkmagic.utils.constants import MIMETYPE_IMAGE_PNG, MIMETYPE_TEXT_HTML, MIMETYPE_TEXT_PLAIN

from . import utils
from .consts import SESSION_STATUS_TIMEOUT, SESSION_STATUS_STARTED, SESSION_STATUS_STOPPED
from .synapsecomm import SynapseComm
from .telemetryutils import log_telemetry


class SessionKeeper(threading.Thread):
    """SessionKepper is similar to HeartBeatThread in LivySession.

    Plus, it periodically send Synapse specific timeout_reset msg to keep the Synapse session alive.
    """

    def __init__(self, session, interval_minutes: int = 1):
        """Create a SessionKeeper.

        :param session: the Synapse session that this keeper needs to keep alive
        :type session: SynapseSession
        """
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval_minutes * 60
        self.session = session
        self.start_time = datetime.utcnow()
        self.last_time = datetime.now()
        self.timeout_seconds = self.session.timeout * 60
        self.telemetry_info = {
            'synapse_session_guid': str(self.session.guid),
            'start_time': self.start_time.isoformat()
        }
        self.telemetry_info.update(self.session.meta)
        self.telemetry_info.pop('spark_conf', None)  # don't need t log spark_conf

    def stop(self):
        """Stop the keeper, hence the session."""
        self.telemetry_info['final_status'] = self.session.status
        self.stopped.set()

    def reset_timeout(self):
        """Reset the last session visit time to now."""
        self.last_time = datetime.now()

    def send_session_telemetry(self, status):
        """Send telemetry."""
        self.telemetry_info['status'] = status
        log_telemetry('azureml.synapse.session.{}'.format(status), self.telemetry_info, "session")

    def run(self):
        """Virtual method inherit from Thread."""
        while not self.stopped.wait(self.interval):
            self.session._refresh_status()
            idle_seconds = (datetime.now() - self.last_time).total_seconds()
            self.telemetry_info['left_seconds'] = self.timeout_seconds - idle_seconds

            if self.session.status in FINAL_STATUS:
                self.stop()
            elif idle_seconds > self.timeout_seconds:
                self.session.mark_timeout()
                self.send_session_telemetry(SESSION_STATUS_TIMEOUT)
            else:
                if self.session.status == BUSY_SESSION_STATUS:
                    self.reset_timeout()
                self.send_session_telemetry(self.session.status)

        self.send_session_telemetry(SESSION_STATUS_STOPPED)


class SessionTracker:
    """SessionTracker track the session and job status running in the session.

    It talks to Livy service to get Livy session status, and pass the status to Jupyter frontend via SynapseComm.
    Jupyter frontend will render the SparkMonitor in notebook UI based on the tracking status.
    """

    def __init__(self, session):
        """Create the SessionTracker.

        :param session: the target session to track
        :type session: SynapseSession
        """
        self._session = session
        self._session_guid = session.guid
        self._session_id = session.id
        self._app_id = session._app_id
        self._http_client = session._http_client
        self._executors = {}
        self._total_cores = 0
        self._start_time = None
        self._session_keeper = None

    def session_create_end(self):
        """Call this method when session creation is completed."""
        self._send_application_start(self._app_id)
        self._session_keeper = SessionKeeper(self._session)
        self._session_keeper.send_session_telemetry(SESSION_STATUS_STARTED)
        self._session_keeper.start()
        self._check_and_send_executor_msg()

    def session_delete_end(self):
        """Call this method when session deletion is completed."""
        self.close()
        if self._session_keeper is not None:
            try:
                self._session_keeper.stop()
                self._session_keeper = None
            except Exception:
                pass

    def statement_execution_start(self, cell_uuid, statement_id):
        """Entry point of the tracking."""
        # spark object hierarchy: hierarchy: session<1--1?>application<1--*>statement<1--*>job<1--*>stage<1--*>task
        # for each level, use tracking_xxx and completed_xxx to record queued/running and completed items

        SynapseComm.send({
            "msgtype": "sparkJobReceived",
            "cellGuid": cell_uuid,
        })
        self._session_keeper.reset_timeout()
        self.track_statement(statement_id, cell_uuid)

    def track_statement(self, statement_id, cell_uuid):
        """Track the statement status."""
        tracking_jobs = {}  # TODO: why split into tracking and completed? Consider store them in one list?
        completed_jobs = {}
        job_stages = {}
        stage_tasks = {}
        # keep checking the statement status until it is completed
        while True:
            # update statement status
            statement = self._http_client.get_statement(self._session_id, statement_id)
            status = statement[u"state"].lower()
            if tracking_jobs:
                running_job = None
                for job_id, old_job in tracking_jobs.items():
                    job = self._http_client.get_job_by_id(self._session_id, self._app_id, job_id)
                    job_status = job['status']

                    if old_job['status'] == "UNKNOWN" and job_status != "UNKNOWN":
                        self._send_job_start(job, cell_uuid)

                    if job_status == "SUCCEEDED" or job_status == "FAILED":
                        self._track_job(job, job_stages, stage_tasks, cell_uuid)
                        completed_jobs[job_id] = job
                        self._send_job_end(job, cell_uuid)
                    else:
                        tracking_jobs[job_id] = job
                        if job_status == "RUNNING":
                            # only track one running job for simplicity, and in most cases,
                            # there will be only one running job per statement
                            running_job = job

                for job_id in completed_jobs:
                    tracking_jobs.pop(job_id, None)

                if running_job:
                    self._track_job(running_job, job_stages, stage_tasks, cell_uuid)

            self._check_new_jobs(statement_id, tracking_jobs, completed_jobs, cell_uuid)

            if status in FINAL_STATEMENT_STATUS:
                if len(tracking_jobs) == 0:
                    self.handle_output(statement)
                    return

            self._check_and_send_executor_msg()
            time.sleep(1)

    def _track_job(self, job: dict, job_stages: Dict[str, Tuple[dict, dict]], stage_tasks, cell_uuid):
        """Track the job status.

        :param job_stages: A dictionary, key is job id, value is tuple of tracking_stages and completed_stages
        :type job_stages: dict
        """
        job_id = job['jobId']

        if job_id not in job_stages:
            job_stages[job_id] = ({}, {})
        tracking_stages, completed_stages = job_stages[job_id]

        if tracking_stages:
            running_stage_key = None
            running_stage = None
            for stage_key, old_stage in tracking_stages.items():
                stage_id = stage_key[0]
                attempt_id = stage_key[1]
                stage = self._http_client.get_stage_attempt_by_id(self._session_id, self._app_id, stage_id, attempt_id)
                stage_status = stage['status']

                if old_stage['status'] == "PENDING" and stage_status != "PENDING":
                    self._send_stage_submitted(stage, job_id, cell_uuid)

                if stage_status == "COMPLETE" or stage_status == "FAILED" or stage_status == "SKIPPED":
                    self._track_stage(stage_key, stage, stage_tasks, cell_uuid)
                    completed_stages[stage_key] = stage
                    self._send_stage_completed(stage, cell_uuid)
                else:
                    tracking_stages[stage_key] = stage
                    if stage_status == "ACTIVE":
                        running_stage_key = stage_key
                        running_stage = stage

            for stage_key in completed_stages:
                tracking_stages.pop(stage_key, None)

            if running_stage_key:
                self._track_stage(running_stage_key, running_stage, stage_tasks, cell_uuid)

        # job['stageIds'] holds all stages in the job, may add new stages during job execution
        self._check_new_stages(job_id, job['stageIds'], tracking_stages, completed_stages, cell_uuid)

    def _track_stage(self, stage_key, stage, stage_tasks, cell_uuid):
        if stage_key not in stage_tasks:
            stage_tasks[stage_key] = ({}, {})
        tracking_tasks, completed_tasks = stage_tasks[stage_key]

        for task in stage["tasks"].values():
            task_id = task["taskId"]
            status = self._task_status(task)
            if status == "SUCCESS" or status == "FAILED":
                if task_id in tracking_tasks:
                    completed_tasks[task_id] = task
                    tracking_tasks.pop(task_id, None)
                    self._send_task_end(task, stage, cell_uuid)
                elif task_id not in completed_tasks:
                    completed_tasks[task_id] = task
                    self._send_msgs_for_fast_task(task, stage, cell_uuid)

            elif task_id not in tracking_tasks:
                tracking_tasks[task_id] = task
                self._send_task_start(task, stage, cell_uuid)
            # all available tasks will be returned within stage response, no need to check_new_tasks()

    def _check_new_jobs(self, statement_id, tracking: dict, completed: dict, cell_uuid):
        # Add new job of the statement to tracking or completed if it is a fast job.
        # New jobs will be added during the execution of the statement

        job_list = self._http_client.get_jobs(self._session_id, self._app_id)
        if job_list is not None:
            for job in job_list:
                job_id = job['jobId']
                job_group = job.get('jobGroup', '')
                if str(job_group) == str(statement_id) and job_id not in tracking and job_id not in completed:
                    status = job['status']
                    if status == "SUCCEEDED" or status == "FAILED":
                        completed[job_id] = job
                        self._send_msgs_for_fast_job(job, cell_uuid)
                    else:
                        tracking[job_id] = job
                        if status == "RUNNING":
                            self._send_job_start(job, cell_uuid)

    def _check_new_stages(self, job_id, stage_ids, tracking, completed, cell_uuid):
        for stage_id in stage_ids:
            stage_with_id = self._http_client.get_stage_by_id(self._session_id, self._app_id, stage_id)
            if stage_with_id is not None:
                for stage in stage_with_id:
                    attempt_id = stage["attemptId"]
                    key = (stage_id, attempt_id)
                    if key not in tracking and key not in completed:
                        stage_status = stage['status']
                        if stage_status == "COMPLETE" or stage_status == "FAILED" or stage_status == "SKIPPED":
                            completed[key] = stage
                            self._send_msgs_for_fast_stage(stage, job_id, cell_uuid)
                        else:
                            tracking[key] = stage
                            if stage_status == "ACTIVE":
                                self._send_stage_submitted(stage, job_id, cell_uuid)

    def handle_output(self, statement):
        """Write output to stdout, hence the notebook."""
        assert statement is not None
        statement_output = statement[u"output"]
        if statement_output is None:
            utils.writeln("")
            return
        if statement_output[u"status"] == "ok":
            data = statement_output[u"data"]
            if MIMETYPE_IMAGE_PNG in data:
                image = Image(base64.b64decode(data[MIMETYPE_IMAGE_PNG]))
                utils.display.display(image)
            elif MIMETYPE_TEXT_HTML in data:
                utils.display_html(data[MIMETYPE_TEXT_HTML])
            else:
                utils.writeln(data[MIMETYPE_TEXT_PLAIN])
            return
        elif statement_output[u"status"] == "error":
            raise SparkStatementException(
                "{}\n{}".format(statement_output[u"evalue"], "".join(statement_output[u"traceback"])))
        else:
            raise LivyUnexpectedStatusException(
                "Unknown output status from Livy: '{}'".format(statement_output[u"status"]))

    def close(self):
        """Close and end the tracker."""
        self._send_application_end()

    def _check_and_send_executor_msg(self):
        executors = self._http_client.get_executors(self._session_id, self._app_id)
        if executors is None:
            return

        new_executors = {executor["id"]: executor for executor in executors}

        to_be_added = set(new_executors.keys()) - set(self._executors.keys())
        to_be_removed = set(self._executors.keys()) - set(new_executors.keys())

        for key in to_be_removed:
            self._send_remove_executor(self._executors[key])

        for key in to_be_added:
            self._send_add_executor(new_executors[key])

        self._executors = new_executors

    def _send_msgs_for_fast_job(self, job, cell_uuid):
        self._send_job_start(job, cell_uuid)
        stage_ids = job["stageIds"]
        for stage_id in stage_ids:
            stage_with_id = self._http_client.get_stage_by_id(self._session_id, self._app_id, stage_id)
            if stage_with_id is None:
                continue
            for stage in stage_with_id:
                self._send_msgs_for_fast_stage(stage, job["jobId"], cell_uuid)
        self._send_job_end(job, cell_uuid)

    def _send_msgs_for_fast_stage(self, stage, job_id, cell_uuid):
        self._send_stage_submitted(stage, job_id, cell_uuid)
        for task in stage["tasks"].values():
            self._send_msgs_for_fast_task(task, stage, cell_uuid)
        self._send_stage_completed(stage, cell_uuid)

    def _send_msgs_for_fast_task(self, task, stage, cell_uuid):
        self._send_task_start(task, stage, cell_uuid)
        self._send_task_end(task, stage, cell_uuid)

    def _send_application_start(self, application_id):
        self._start_time = self._timestamp()
        msg = {
            "msgtype": "sparkApplicationStart",
            "appId": application_id,
            "appName": application_id,
            "startTime": self._start_time,
            "appAttemptId": "null",  # TODO: why include these useless fields?
            "sparkUser": ""
        }

        SynapseComm.send(msg)

    def _send_application_end(self):
        msg = {
            "msgtype": "sparkApplicationEnd",
            "endTime": self._timestamp()
        }

        SynapseComm.send(msg)

    def _send_add_executor(self, executor):
        self._total_cores += executor["totalCores"]
        msg = {
            "msgtype": "sparkExecutorAdded",
            "executorId": executor["id"],
            "time": self._timestamp(),
            "host": executor["hostPort"].split(":")[0],
            "numCodes": executor["totalCores"],
            "totalCores": self._total_cores
        }

        SynapseComm.send(msg)

    def _send_remove_executor(self, executor):
        self._total_cores -= executor["totalCores"]
        msg = {
            "msgtype": "sparkExecutorRemoved",
            "executorId": executor["id"],
            "time": self._timestamp(),
            "totalCores": self._total_cores
        }

        SynapseComm.send(msg)

    def _send_job_start(self, job: dict, cell_uuid):
        stage_ids = job["stageIds"]
        stage_infos = {}
        stages = self._http_client.get_stages(self._session_id, self._app_id)

        if stages is not None:
            stage_dict = {stage["stageId"]: stage for stage in stages}

            for stageId in stage_ids:
                stage = stage_dict[stageId]
                stage_infos[stageId] = {
                    "attemptId": stage["attemptId"],
                    "name": stage["name"],
                    "numTasks": stage["numActiveTasks"] + stage["numCompleteTasks"] + stage["numFailedTasks"],
                    "submissionTime": self._timestamp(stage.get("submissionTime", -1)),
                    "completionTime": self._timestamp(stage.get("completionTime", -1))
                }

        # Completed status will be sent at job end
        status = job["status"]
        if status == "SUCCEEDED" or status == "FAILED":
            status = "RUNNING"

        msg = {
            "msgtype": "sparkJobStart",
            "jobGroup": job.get("jobGroup", "null"),
            "jobId": job["jobId"],
            "status": status,
            "submissionTime": self._timestamp(job["submissionTime"]),
            "stageIds": stage_ids,
            "stageInfos": stage_infos,
            "numTasks": job["numTasks"],
            "totalCores": self._total_cores,
            "appId": self._app_id,
            "numExecutors": len(self._executors),
            "name": job["name"],
            "sparkUiUrl": self._session.get_spark_ui_url(),
            "cellGuid": cell_uuid,
        }

        SynapseComm.send(msg)

    def _send_job_end(self, job, cell_uuid):
        msg = {
            "msgtype": "sparkJobEnd",
            "jobId": job["jobId"],
            "status": job["status"],
            "completionTime": self._timestamp(job["completionTime"]),
            "cellGuid": cell_uuid,
        }

        SynapseComm.send(msg)

    def _send_stage_submitted(self, stage, job_id, cell_uuid):
        msg = {
            "msgtype": "sparkStageSubmitted",
            "stageId": stage["stageId"],
            "stageAttemptId": stage["attemptId"],
            "name": stage["name"],
            "numTasks": stage["numTasks"],
            "parentIds": [],
            "submissionTime": self._timestamp(stage.get("submissionTime", -1)),
            "jobIds": [job_id],
            "cellGuid": cell_uuid,
        }

        SynapseComm.send(msg)

    def _send_stage_completed(self, stage, cell_uuid):
        msg = {
            "msgtype": "sparkStageCompleted",
            "stageId": stage["stageId"],
            "stageAttemptId": stage["attemptId"],
            "numTasks": stage["numTasks"],
            "submissionTime": self._timestamp(stage.get("submissionTime", -1)),
            "completionTime": self._timestamp(stage.get("completionTime", -1)),
            # frontend require a "COMPLETED" instead of "COMPLETE"
            "status": "COMPLETED" if stage["status"] == "COMPLETE" else stage["status"],
            "cellGuid": cell_uuid,
        }

        SynapseComm.send(msg)

    def _send_task_start(self, task, stage, cell_uuid):
        msg = {
            "msgtype": "sparkTaskStart",
            "launchTime": self._timestamp(task["launchTime"]),
            "taskId": task["taskId"],
            "stageId": stage["stageId"],
            "stageAttemptId": stage["attemptId"],
            "index": task["index"],
            "attemptNumber": task["attempt"],
            "executorId": task["executorId"],
            "host": task["host"],
            "status": "RUNNING",
            "speculative": task["speculative"],
            "cellGuid": cell_uuid,
        }

        SynapseComm.send(msg)

    def _send_task_end(self, task, stage, cell_uuid):
        launch_time = self._timestamp(task["launchTime"])
        msg = {
            "msgtype": "sparkTaskEnd",
            "launchTime": launch_time,
            "finishTime": launch_time + self._task_execute_time(task),
            "taskId": task["taskId"],
            "stageId": stage["stageId"],
            "taskType": None,
            "stageAttemptId": stage["attemptId"],
            "index": task["index"],
            "attemptNumber": task["attempt"],
            "executorId": task["executorId"],
            "host": task["host"],
            "status": self._task_status(task),
            "speculative": task["speculative"],
            "errorMessage": task.get("errorMessage"),
            "metrics": self._task_metrics(task),
            "cellGuid": cell_uuid,
        }

        SynapseComm.send(msg)

    def _task_status(self, task):
        if "errorMessage" in task:
            return "FAILED"
        elif "taskMetrics" in task:
            metrics = task["taskMetrics"]
            if (metrics.get("executorDeserializeTime", 0) != 0
                    or metrics.get("executorDeserializeCpuTime", 0) != 0
                    or metrics.get("executorRunTime", 0) != 0
                    or metrics.get("executorCpuTime", 0) != 0):
                return "SUCCESS"
        return "RUNNING"

    def _task_execute_time(self, task):
        metrics = task.get("taskMetrics")
        return metrics.get("executorRunTime", 0) + metrics.get("executorDeserializeTime", 0) + metrics.get(
            "resultSerializationTime", 0)

    def _task_metrics(self, task):
        metrics = task.get("taskMetrics")
        if metrics is None:
            return {}

        total_execution_time = self._task_execute_time(task)

        def _to_proportion(time):
            return time / total_execution_time * 100

        shuffle_read_metrics = metrics["shuffleReadMetrics"]
        shuffle_write_metrics = metrics["shuffleWriteMetrics"]

        shuffle_read_time = shuffle_read_metrics.get("fetchWaitTime", 0)
        shuffle_write_time = shuffle_write_metrics.get("writeTime", 0) / 1000000  # It's in nanoseconds, interesting
        serialization_time = metrics.get("resultSerializationTime", 0)
        deserialization_time = metrics.get("executorDeserializeTime", 0)
        getting_result_time = 0  # Cannot get this
        executor_computing_time = metrics.get("executorRunTime", 0) - shuffle_read_time - shuffle_write_time
        scheduler_delay = 0  # Cannot get this

        shuffle_read_time_proportion = _to_proportion(shuffle_read_time)
        shuffle_write_time_proportion = _to_proportion(shuffle_write_time)
        serialization_time_proportion = _to_proportion(serialization_time)
        deserialization_time_proportion = _to_proportion(deserialization_time)
        getting_result_time_proportion = _to_proportion(getting_result_time)
        executor_computing_time_proportion = _to_proportion(executor_computing_time)
        scheduler_delay_proportion = _to_proportion(scheduler_delay)

        scheduler_delay_proportion_pos = 0
        deserialization_time_proportion_pos = scheduler_delay_proportion_pos + scheduler_delay_proportion
        shuffle_read_time_proportion_pos = deserialization_time_proportion_pos + deserialization_time_proportion
        executor_computing_time_proportion_pos = shuffle_read_time_proportion_pos + shuffle_read_time_proportion
        shuffle_write_time_proportion_pos = executor_computing_time_proportion_pos + executor_computing_time_proportion
        serialization_time_proportion_pos = shuffle_write_time_proportion_pos + shuffle_write_time_proportion
        getting_result_time_proportion_pos = serialization_time_proportion_pos + serialization_time_proportion

        return {
            "shuffleReadTime": shuffle_read_time,
            "shuffleWriteTime": shuffle_write_time,
            "serializationTime": serialization_time,
            "deserializationTime": deserialization_time,
            "gettingResultTime": getting_result_time,
            "executorComputingTime": executor_computing_time,
            "schedulerDelay": scheduler_delay,
            "shuffleReadTimeProportion": shuffle_read_time_proportion,
            "shuffleWriteTimeProportion": shuffle_write_time_proportion,
            "serializationTimeProportion": serialization_time_proportion,
            "deserializationTimeProportion": deserialization_time_proportion,
            "gettingResultTimeProportion": getting_result_time_proportion,
            "executorComputingTimeProportion": executor_computing_time_proportion,
            "schedulerDelayProportion": scheduler_delay_proportion,
            "shuffleReadTimeProportionPos": shuffle_read_time_proportion_pos,
            "shuffleWriteTimeProportionPos": shuffle_write_time_proportion_pos,
            "serializationTimeProportionPos": serialization_time_proportion_pos,
            "deserializationTimeProportionPos": deserialization_time_proportion_pos,
            "gettingResultTimeProportionPos": getting_result_time_proportion_pos,
            "executorComputingTimeProportionPos": executor_computing_time_proportion_pos,
            "schedulerDelayProportionPos": scheduler_delay_proportion_pos,
            "resultSize": metrics.get("resultSize", 0),
            "jvmGCTime": metrics.get("jvmGcTime", 0),
            "memoryBytesSpilled": metrics.get("memoryBytesSpilled", 0),
            "diskBytesSpilled": metrics.get("diskBytesSpilled", 0),
            "peakExecutionMemory": 0  # Cannot get this
        }

    def _timestamp(self, time_source=None):
        if time_source is None:
            return time.time() * 1000
        elif isinstance(time_source, text_type) or isinstance(time_source, binary_type):
            t = parser.parse(time_source)
            try:
                result = t.timestamp() * 1000
            except AttributeError:
                utc_naive = t.replace(tzinfo=None) - t.utcoffset()
                result = (utc_naive - datetime(1970, 1, 1)).total_seconds() * 1000
            return result
        elif type(time_source) is int or type(time_source) is float:
            return time_source
