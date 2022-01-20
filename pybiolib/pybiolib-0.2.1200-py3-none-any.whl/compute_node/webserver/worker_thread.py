import base64
import logging
import random
import sys
import time
import threading
import socket
from queue import Queue

from biolib import utils
from biolib.compute_node.cloud_utils import CloudUtils
from biolib.compute_node.job_worker import JobWorkerProcess
from biolib.compute_node.socker_listener_thread import SocketListenerThread
from biolib.compute_node.socket_sender_thread import SocketSenderThread
from biolib.compute_node.webserver import webserver_utils
from biolib.biolib_binary_format import AttestationDocument, SystemStatusUpdate, SystemException
from biolib.compute_node.utils import get_package_type, WorkerThreadException, SystemExceptionCodes
from biolib.biolib_logging import logger

SOCKET_HOST = '127.0.0.1'


class WorkerThread(threading.Thread):
    def __init__(self, compute_state):
        try:
            super().__init__()
            self.compute_state = compute_state
            self._socket_port = random.choice(range(6000, 65000))
            self._socket = None
            self._connection = None
            self._job_worker_process = None
            self._connection_thread = None
            self._listener_thread = None
            self._sender_thread = None
            self._start_and_connect_to_compute_process()

            logger.debug(f"WorkerThread connected to port {self._socket_port}")

        except Exception as exception:
            raise WorkerThreadException(exception, SystemExceptionCodes.FAILED_TO_INITIALIZE_WORKER_THREAD.value,
                                        worker_thread=self) from exception

    def run(self):
        try:
            while True:
                package = self.compute_state['received_messages_queue'].get()
                package_type = get_package_type(package)

                if package_type == 'AttestationDocument':
                    self.compute_state['attestation_document'] = AttestationDocument(package).deserialize()

                elif package_type == 'StdoutAndStderr':
                    self.compute_state['status']['stdout_and_stderr_packages_b64'].append(
                        base64.b64encode(package).decode()
                    )

                elif package_type == 'SystemStatusUpdate':
                    progress, log_message = SystemStatusUpdate(package).deserialize()
                    self.compute_state['status']['status_updates'].append({'progress': progress,
                                                                           'log_message': log_message})
                    self.compute_state['progress'] = progress

                elif package_type == 'SystemException':
                    error_code = SystemException(package).deserialize()
                    self.compute_state['status']['error_code'] = error_code
                    logger.debug("Hit error. Terminating Worker Thread and Compute Process")
                    self.compute_state['progress'] = 95
                    self.terminate()

                elif package_type == 'ModuleOutput':
                    self.compute_state['result'] = package
                    self.terminate()

                elif package_type == 'AesEncryptedPackage':
                    if self.compute_state['progress'] == 95:  # Check if encrypted package is ModuleOutput
                        self.compute_state['result'] = package
                        self.terminate()
                    else:  # Else it is StdoutAndStderr
                        self.compute_state['status']['stdout_and_stderr_packages_b64'].append(
                            base64.b64encode(package).decode()
                        )

                else:
                    raise Exception(f'Package type from child was not recognized: {package}')

                self.compute_state['received_messages_queue'].task_done()

        except Exception as exception:
            raise WorkerThreadException(exception, SystemExceptionCodes.FAILED_TO_HANDLE_PACKAGE_IN_WORKER_THREAD.value,
                                        worker_thread=self) from exception

    def _start_and_connect_to_compute_process(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug(f"Trying to bind to socket on {SOCKET_HOST}:{self._socket_port}")
        self._socket.bind((SOCKET_HOST, self._socket_port))

        logger.debug(f"Starting to listen to socket on port {self._socket_port}")
        self._socket.listen()
        logger.debug(f"Listening to port {self._socket_port}")

        received_messages_queue = Queue()
        messages_to_send_queue = Queue()

        # Starting a thread for accepting connections before starting the process that should to connect to the socket
        logger.debug("Starting connection thread")
        self._connection_thread = threading.Thread(target=self._accept_new_socket_connection, args=[
            received_messages_queue,
            messages_to_send_queue
        ])
        self._connection_thread.start()
        logger.debug("Started connection thread")
        logger.debug("Starting compute process")

        self._job_worker_process = JobWorkerProcess(socket_port=self._socket_port, log_level=logger.level)
        self._job_worker_process.start()

        self.compute_state['received_messages_queue'] = received_messages_queue
        self.compute_state['messages_to_send_queue'] = messages_to_send_queue
        self.compute_state['worker_thread'] = self

    def _accept_new_socket_connection(self, received_messages_queue, messages_to_send_queue):
        self._connection, _ = self._socket.accept()
        self._listener_thread = SocketListenerThread(self._connection, received_messages_queue)
        self._listener_thread.start()

        self._sender_thread = SocketSenderThread(self._connection, messages_to_send_queue)
        self._sender_thread.start()

    def terminate(self):
        if self._job_worker_process:
            logger.debug(f'Terminating JobWorkerProcess with PID {self._job_worker_process.pid}')
            self._job_worker_process.terminate()

        if self._socket:
            self._socket.close()

        if self._connection:
            self._connection.close()

        job_id = self.compute_state['job_id']
        if self.compute_state['progress'] == 95:
            seconds_to_sleep = 60
            logger.debug(f'Worker thread sleeping for {seconds_to_sleep} seconds before cleaning up job {job_id}')
            # sleep to see if the user has begun finalizing the job
            time.sleep(seconds_to_sleep)
            # Check if job has not been finalized yet
            if self.compute_state['progress'] != 100:
                if utils.IS_RUNNING_IN_CLOUD:
                    CloudUtils.log(
                        f"Job {job_id} was not fetched within {seconds_to_sleep}s, cleaning up...",
                        logging.DEBUG
                    )
                else:
                    logger.debug(f"Job {job_id} was not fetched within {seconds_to_sleep}s, cleaning up...")

        webserver_utils.finalize_and_clean_up_compute_job(job_id)

        logger.debug("Terminating Worker Thread")
        sys.exit()
