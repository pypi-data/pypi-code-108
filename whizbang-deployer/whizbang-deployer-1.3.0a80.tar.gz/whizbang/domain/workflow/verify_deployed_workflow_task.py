from abc import ABC
from time import sleep

import requests

from whizbang.core.workflow_task import WorkflowTask
from whizbang.util.deployment_helpers import timestamp

import logging
_log = logging.getLogger(__name__) 

class VerifyDeployedWorkflowTask(WorkflowTask, ABC):
    def __init__(self):
        WorkflowTask.__init__(self)

    @staticmethod
    def verify_deployed(callback, resource_name: str, timeout_seconds: int, **kwargs):
        seconds = 0
        
        # FIXME this is a hack implementation, especially the timeout handling.
        while True:
            try:
                result = callback(**kwargs)
                return result
            except requests.HTTPError as e:
                _log.debug(timestamp(f'Waiting on {resource_name} to finish deploying. '
                                f'Request failed with error {e}'))
                sleep(1)
                seconds += 1
                if seconds > timeout_seconds:
                    _log.error(f'{resource_name} failed to deploy within {timeout_seconds} seconds')
                    raise TimeoutError
                continue
