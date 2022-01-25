import time

from biolib import utils
from biolib.biolib_logging import logger
from biolib.compute_node.cloud_utils import CloudUtils
from biolib.typing_utils import Dict, List
from biolib.compute_node.webserver.worker_thread import WorkerThread


JOB_ID_TO_COMPUTE_STATE_DICT: Dict = {}
UNASSIGNED_COMPUTE_PROCESSES: List = []


def finalize_and_clean_up_compute_job(job_id: str):
    if job_id in JOB_ID_TO_COMPUTE_STATE_DICT:
        compute_state = JOB_ID_TO_COMPUTE_STATE_DICT[job_id]
        # Signal to the worker thread that the job has been finalized
        compute_state['progress'] = 100
        JOB_ID_TO_COMPUTE_STATE_DICT.pop(job_id)
        if utils.IS_RUNNING_IN_CLOUD:
            system_exception_code = compute_state['status'].get('error_code')  # Get and send exception code if present
            CloudUtils.finish_cloud_job(compute_state['cloud_job_id'], system_exception_code)
    else:
        logger.debug(f"Job id {job_id} could not be found, maybe it has already been finalized")


def get_compute_state(unassigned_compute_processes):
    if len(unassigned_compute_processes) == 0:
        start_compute_process(unassigned_compute_processes)

    return unassigned_compute_processes.pop()


def start_compute_process(unassigned_compute_processes):
    compute_state = {
        'job_id': None,
        'cloud_job_id': None,
        'status': {
            'status_updates': [
                {
                    'progress': 10,
                    'log_message': 'Initializing'
                }
            ],
            'stdout_and_stderr_packages_b64': []
        },
        'progress': 0,
        'result': None,
        'attestation_document': b'',
        'received_messages_queue': None,
        'messages_to_send_queue': None,
        'worker_process': None
    }

    WorkerThread(compute_state).start()

    while True:
        if compute_state['attestation_document']:
            break
        time.sleep(0.25)

    unassigned_compute_processes.append(compute_state)


def validate_saved_job(saved_job):
    if 'app_version' not in saved_job['job']:
        return False

    if 'access_token' not in saved_job:
        return False

    if 'module_name' not in saved_job:
        return False

    return True
