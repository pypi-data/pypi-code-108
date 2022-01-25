# pylint: disable=unsubscriptable-object

import json
import time
import base64
import logging
from flask import Flask, request, Response, jsonify
from flask_cors import CORS  # type: ignore

from biolib import utils
from biolib.biolib_api_client import BiolibApiClient
from biolib.biolib_binary_format import SavedJob
from biolib.compute_node.enclave.enclave_remote_hosts import start_enclave_remote_hosts
from biolib.compute_node.webserver import webserver_utils
from biolib.compute_node.cloud_utils.cloud_utils import CloudUtils
from biolib.compute_node.webserver.gunicorn_flask_application import GunicornFlaskApplication
from biolib.biolib_logging import logger, TRACE

app = Flask(__name__)
CORS(app)


@app.route('/hello/')
def hello():
    return 'Hello'


@app.route('/v1/job/', methods=['POST'])
def save_job():
    saved_job = json.loads(request.data.decode())

    # TODO: figure out why this shallow validate method is used
    if not webserver_utils.validate_saved_job(saved_job):
        return jsonify({'job': 'Invalid job'}), 400

    job_id = saved_job['job']['public_id']
    saved_job['BASE_URL'] = BiolibApiClient.get().base_url

    compute_state = webserver_utils.get_compute_state(webserver_utils.UNASSIGNED_COMPUTE_PROCESSES)
    compute_state['job_id'] = job_id
    webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id] = compute_state

    if utils.IS_RUNNING_IN_CLOUD:
        config = CloudUtils.get_webserver_config()
        saved_job['compute_node_info'] = config['compute_node_info']
        compute_state['cloud_job_id'] = saved_job['cloud_job']['public_id']

    saved_job_bbf_package = SavedJob().serialize(json.dumps(saved_job))
    send_package_to_compute_process(job_id, saved_job_bbf_package)

    if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
        return Response(base64.b64encode(compute_state['attestation_document']), status=201)
    else:
        return '', 201


@app.route('/v1/job/<job_id>/start/', methods=['POST'])
def start_compute(job_id):
    module_input_package = request.data
    send_package_to_compute_process(job_id, module_input_package)
    return '', 201


@app.route('/v1/job/<job_id>/status/')
def status(job_id):
    # TODO Implement auth token
    current_status = webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id]['status'].copy()
    response = jsonify(current_status)

    if current_status['status_updates']:
        webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id]['status']['status_updates'] = []

    if current_status['stdout_and_stderr_packages_b64']:
        webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id]['status']['stdout_and_stderr_packages_b64'] = []

    # Check if any error occurred
    if 'error_code' in current_status:
        response.call_on_close(lambda: webserver_utils.finalize_and_clean_up_compute_job(job_id))

    return response


@app.route('/v1/job/<job_id>/result/')
def result(job_id):
    if not webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id]['result']:
        time.sleep(2)

    if webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id]['result']:
        result_data = webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id]['result']
        # remove result from state dict, so we know the user has started the download
        webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id]['result'] = None
        response = Response(result_data)
        response.call_on_close(lambda: webserver_utils.finalize_and_clean_up_compute_job(job_id))

        return response

    else:
        return '', 404


def send_package_to_compute_process(job_id, package_bytes):
    message_queue = webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT[job_id]['messages_to_send_queue']
    message_queue.put(package_bytes)


def start_webserver(port, host):
    def worker_exit(server, worker):  # pylint: disable=unused-argument
        active_compute_states = list(
            webserver_utils.JOB_ID_TO_COMPUTE_STATE_DICT.values()) + webserver_utils.UNASSIGNED_COMPUTE_PROCESSES
        logger.debug(f'Sending terminate signal to {len(active_compute_states)} compute processes')
        if active_compute_states:
            for compute_state in active_compute_states:
                if compute_state['worker_thread']:
                    compute_state['worker_thread'].terminate()
            time.sleep(2)
        return

    def post_fork(server, worker):  # pylint: disable=unused-argument
        logger.info('Started compute node')

        if utils.IS_RUNNING_IN_CLOUD:
            logger.debug('Initializing webserver...')
            config = CloudUtils.get_webserver_config()
            utils.IS_DEV = config['is_dev']
            BiolibApiClient.initialize(config['base_url'])

            if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
                start_enclave_remote_hosts(config)

            CloudUtils.initialize()

    if logger.level == TRACE:
        gunicorn_log_level_name = 'DEBUG'
    elif logger.level == logging.DEBUG:
        gunicorn_log_level_name = 'INFO'
    elif logger.level == logging.INFO:
        gunicorn_log_level_name = 'WARNING'
    else:
        gunicorn_log_level_name = logging.getLevelName(logger.level)

    options = {
        'bind': f'{host}:{port}',
        'workers': 1,
        'post_fork': post_fork,
        'worker_exit': worker_exit,
        'timeout': '300',
        'graceful_timeout': 4,
        'loglevel': gunicorn_log_level_name,
    }

    GunicornFlaskApplication(app, options).run()
