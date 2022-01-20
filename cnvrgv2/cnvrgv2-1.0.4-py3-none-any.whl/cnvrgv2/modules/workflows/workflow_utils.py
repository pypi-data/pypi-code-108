import time

from cnvrgv2.config.error_messages import WORKFLOW_FINAL_STATE
from cnvrgv2.errors import CnvrgFinalStateReached


class WorkflowStatuses:
    PENDING = "pending"
    PENDING_APPROVAL = "pending_approval"
    INITIALIZING = "initializing"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    RECURRING = "recurring"
    RESTARTING = "restarting"
    ONGOING = "ongoing"
    TERMINATING = "terminating"
    SUCCESS = "success"
    ERROR = "error"
    DEBUG = "debug"
    STOPPED = "stopped"

    FINAL_STATES = [SUCCESS, ERROR, DEBUG, STOPPED]


class WorkflowUtils:

    @staticmethod
    def wait_for_statuses(workflow, statuses, poll_interval=10, max_duration=600):
        """
        Polls on a workflow status until in reaches the wanted status or times out
        @param workflow: The workflow to poll on
        @param statuses: List of required statuses.
        @param poll_interval: Time between polls
        @param max_duration: Polling timeout
        @return: The workflow's status at the end of polling
        """
        start_time = time.time()

        while True:
            if workflow.status in statuses:
                break
            if time.time() >= start_time + max_duration:
                raise TimeoutError()
            # Workflow reached end state different from desired. No need to continue
            if workflow.status in WorkflowStatuses.FINAL_STATES:
                raise CnvrgFinalStateReached(WORKFLOW_FINAL_STATE.format(workflow.status))

            time.sleep(poll_interval)
            workflow.reload()

        return workflow.status
