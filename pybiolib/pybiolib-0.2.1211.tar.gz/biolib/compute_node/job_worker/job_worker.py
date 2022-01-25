import io
import json
import logging
import socket
import shlex
import tarfile
import zipfile
from time import time, sleep
from queue import Queue
import multiprocessing
import os
import signal
from types import FrameType

import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from docker.errors import ImageNotFound  # type: ignore
from docker.models.networks import Network  # type: ignore
from docker.models.containers import Container  # type: ignore

from biolib.biolib_binary_format.stdout_and_stderr import StdoutAndStderr
from biolib.compute_node.job_worker.large_file_system import LargeFileSystem
from biolib.biolib_errors import DockerContainerNotFoundDuringExecutionException
from biolib.compute_node.job_worker.job_max_runtime_timer_thread import JobMaxRuntimeTimerThread
from biolib.compute_node.remote_host_proxy import RemoteHostProxy
from biolib.typing_utils import Optional, List, Dict
from biolib import utils
from biolib.biolib_api_client import ModuleEnvironment, Job, JobWrapper, Module, AppVersionOnJob, BiolibApiClient, \
    RemoteHost
from biolib.biolib_api_client.biolib_job_api import BiolibJobApi
from biolib.biolib_docker_client import BiolibDockerClient
from biolib.biolib_logging import logger
from biolib.compute_node.job_worker.executors import PyppeteerExecutor, DockerExecutor, RemoteExecutor
from biolib.compute_node.job_worker.executors.base_executor import BaseExecutor
from biolib.compute_node.job_worker.executors.types import LocalExecutorOptions, StatusUpdate, RemoteExecuteOptions
from biolib.compute_node.socker_listener_thread import SocketListenerThread
from biolib.compute_node.socket_sender_thread import SocketSenderThread
from biolib.compute_node.job_worker.mappings import Mappings, path_without_first_folder
from biolib.compute_node.job_worker.utils import ComputeProcessException, log_disk_and_memory_usage_info
from biolib.compute_node.utils import get_package_type, SystemExceptionCodes
from biolib.compute_node.cloud_utils.cloud_utils import CloudUtils
from biolib.biolib_binary_format import AttestationDocument, SavedJob, SystemStatusUpdate, \
    RsaEncryptedAesPackage, AesEncryptedPackage, ModuleInput, SystemException

try:
    from biolib.compute_node.enclave.nitro_secure_module_utils import NitroSecureModuleUtils
except ImportError:
    pass

_DNS_PROXY_IMAGE_URI = 'spx01/blocky@sha256:485ef739233341d3e14a64db646754aba7322c34645f804c3c0c00556d9a2cd1'
DEFAULT_BUFFER_SIZE = 1024
SOCKET_HOST = '127.0.0.1'


class JobWorkerProcess(multiprocessing.Process):

    # note: this method is run in the parent process
    def __init__(self, socket_port: int, log_level: int):
        super().__init__()
        self._socket_port = socket_port
        self._log_level = log_level

    # note: this method is run in the newly started process once called with .start()
    def run(self) -> None:
        _JobWorker(self._socket_port, self._log_level).run_handle_message_loop()


class _JobWorker:
    _STOP_HANDLE_MESSAGE_LOOP = b'STOP_HANDLE_MESSAGE_LOOP'

    def __init__(self, socket_port: int, log_level: int):
        try:
            logger.setLevel(log_level)

            # handle interrupt from keyboard (CTRL + C)
            signal.signal(signal.SIGINT, self._handle_exit_gracefully)
            # handle termination signal from parent
            signal.signal(signal.SIGTERM, self._handle_exit_gracefully)

            self._socket_port = socket_port
            self._received_messages_queue: Queue = Queue()
            self._messages_to_send_queue: Queue = Queue()

            self._app_version_id_to_runtime_zip: Dict[str, bytes] = {}
            self._jobs: Dict[str, Job] = {}
            self._root_job_wrapper: Optional[JobWrapper] = None

            self._dns_proxy: Optional[Container] = None

            self._remote_host_proxies: List[RemoteHostProxy] = []
            self._internal_network: Optional[Network] = None
            self._public_network: Optional[Network] = None
            self._executors: List[BaseExecutor] = []
            self.is_cleaning_up: bool = False

            if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
                self._nsm_util = NitroSecureModuleUtils()
                self._aes_key_buffer = b''
                logger.setLevel(logging.DEBUG)
        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_INIT_COMPUTE_PROCESS_VARIABLES.value,
                self.send_system_exception,
                may_contain_user_data=False
            ) from exception

        self._connect_to_parent()

    def _handle_exit_gracefully(self, signum: int, frame: FrameType) -> None:  # pylint: disable=unused-argument
        logger.debug(f'_JobWorker got exit signal {signal.Signals(signum).name}')  # pylint: disable=no-member
        self._received_messages_queue.put(self._STOP_HANDLE_MESSAGE_LOOP)
        self._cleanup()

    def run_handle_message_loop(self):
        logger.debug(f'Started JobWorkerProcess {os.getpid()}')
        while True:
            try:
                package = self._received_messages_queue.get()
                if package == self._STOP_HANDLE_MESSAGE_LOOP:
                    break

                package_type = get_package_type(package)
                if package_type == 'RsaEncryptedAesPackage':
                    encrypted_aes_key, iv, _, encrypted_data = RsaEncryptedAesPackage(package).deserialize()
                    self._aes_key_buffer = self._nsm_util.decrypt(encrypted_aes_key)
                    aes_key = AES.new(self._aes_key_buffer, AES.MODE_GCM, iv)

                    package = aes_key.decrypt(encrypted_data)
                    package_type = get_package_type(package)

                if package_type == 'SavedJob':
                    self._handle_save_job_wrapper(package)
                    if utils.IS_RUNNING_IN_CLOUD:
                        logger.debug("Starting Job Max Run Time Timer")
                        JobMaxRuntimeTimerThread(job_worker=self).start()
                        CloudUtils.start_auto_shutdown_timer()

                elif package_type == 'ModuleInput':
                    if not self._root_job_wrapper:
                        raise Exception('No job saved yet')

                    try:
                        module_output_serialized = self._run_job(
                            job=self._root_job_wrapper['job'],
                            module_input_serialized=package,
                        )

                    # This error occurs when trying to access the container after the job worker has cleaned it up.
                    # In that case stop the computation.
                    except DockerContainerNotFoundDuringExecutionException as err:
                        if self.is_cleaning_up:
                            break
                        else:
                            raise err

                    if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
                        module_output_to_send = self._wrap_in_aes_encrypted_package(module_output_serialized)
                    else:
                        module_output_to_send = module_output_serialized

                    self._send_status_update(StatusUpdate(progress=95, log_message='Result Ready'))
                    self._messages_to_send_queue.put(module_output_to_send)

                else:
                    logger.error(f'Package type from parent was not recognized: {package}')

                self._received_messages_queue.task_done()
            except ComputeProcessException:
                continue

            except Exception as exception:
                raise ComputeProcessException(
                    exception,
                    SystemExceptionCodes.UNKOWN_COMPUTE_PROCESS_ERROR.value,
                    self.send_system_exception
                ) from exception

    def _cleanup(self) -> None:
        self.is_cleaning_up = True

        proxy_count = len(self._remote_host_proxies)
        if proxy_count > 0:
            proxy_cleanup_start_time = time()

            for proxy in self._remote_host_proxies:
                try:
                    proxy.terminate()
                except Exception as exception:  # pylint: disable=broad-except
                    logger.error(f'Failed to clean up remote host proxy: {exception}')

            self._remote_host_proxies = []
            logger.debug(f'Cleaned up {proxy_count} proxies in {time() - proxy_cleanup_start_time}')

        if self._dns_proxy:
            try:
                self._dns_proxy.remove(force=True)
                logger.debug('Cleaned up DNS Proxy')
            except Exception as exception:  # pylint: disable=broad-except
                logger.error(f'Failed to clean up DNS Proxy: {exception}')

        self._cleanup_network(self._internal_network)
        self._internal_network = None
        self._cleanup_network(self._public_network)
        self._public_network = None

        for executor in self._executors:
            executor.cleanup()

    @staticmethod
    def _cleanup_network(network: Optional[Network]) -> None:
        if network:
            network_cleanup_start_time = time()
            network_name = network
            try:
                network.remove()
            except Exception as exception:  # pylint: disable=broad-except
                logger.error(f'Failed to clean up {network_name}: {exception}')
            logger.debug(f'Removed network {network_name} in {time() - network_cleanup_start_time}')

    def _handle_save_job_wrapper(self, package: bytes):
        job_wrapper_json_string = SavedJob(package).deserialize()
        job_wrapper: JobWrapper = json.loads(job_wrapper_json_string)
        BiolibApiClient.initialize(
            base_url=job_wrapper['BASE_URL'],
            access_token=job_wrapper['access_token']
        )
        self._root_job_wrapper = job_wrapper
        if not utils.IS_RUNNING_IN_CLOUD:
            job_wrapper['cloud_job'] = None

        job = job_wrapper['job']
        self._jobs[job['public_id']] = job

        if job['app_version'].get('modules') is not None and BiolibDockerClient.is_docker_running():
            self._start_network_and_remote_host_proxies(job)

        # TODO: start downloading runtime zip already at this point

    def _start_network_and_remote_host_proxies(self, job: Job) -> None:
        job_id = job['public_id']
        remote_hosts = job['app_version']['remote_hosts']

        docker_client = BiolibDockerClient.get_docker_client()
        try:
            self._internal_network = docker_client.networks.create(
                name=f'biolib-sandboxed-network-{job_id}',
                internal=True,
                driver='bridge',
            )
        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_CREATE_DOCKER_NETWORKS.value,
                self.send_system_exception,
                may_contain_user_data=False
            ) from exception

        if len(remote_hosts) > 0:
            logger.debug(f'Creating networks for remote host proxies for job: {job_id}')
            try:
                self._public_network = docker_client.networks.create(
                    name=f'biolib-proxy-network-{job_id}',
                    internal=False,
                    driver='bridge',
                )
            except Exception as exception:
                raise ComputeProcessException(
                    exception,
                    SystemExceptionCodes.FAILED_TO_CREATE_DOCKER_NETWORKS.value,
                    self.send_system_exception,
                    may_contain_user_data=False
                ) from exception
            logger.debug(f'Starting remote host proxies for job: {job_id}')
            try:
                hostname_to_ports: Dict[str, List[int]] = {}
                for remote_host in remote_hosts:
                    if ':' in remote_host['hostname']:
                        hostname, port_str = remote_host['hostname'].split(':')
                        port = int(port_str)
                    else:
                        port = 443
                        hostname = remote_host['hostname']

                    if hostname in hostname_to_ports:
                        hostname_to_ports[hostname].append(port)
                    else:
                        hostname_to_ports[hostname] = [port]

                for hostname, ports in hostname_to_ports.items():
                    remote_host_proxy = RemoteHostProxy(
                        RemoteHost(hostname=hostname),
                        self._public_network,
                        self._internal_network,
                        job_id,
                        ports
                    )
                    remote_host_proxy.start()
                    self._remote_host_proxies.append(remote_host_proxy)

                if utils.BIOLIB_ENABLE_DNS_PROXY:
                    logger.debug("Starting DNS Proxy")
                    domains_to_whitelist = list(hostname_to_ports.keys())
                    self._start_dns_proxy(domains_to_whitelist=domains_to_whitelist)

            except Exception as exception:
                raise ComputeProcessException(
                    exception,
                    SystemExceptionCodes.FAILED_TO_START_REMOTE_HOST_PROXIES.value,
                    self.send_system_exception,
                    may_contain_user_data=False
                ) from exception

            logger.debug(f'Completed startup of remote host proxies for job: {job_id}')

    def _get_dns_proxy_image(self):
        docker = BiolibDockerClient.get_docker_client()
        try:
            return docker.images.get(_DNS_PROXY_IMAGE_URI)
        except ImageNotFound:
            logger.debug('Pulling DNS Proxy docker image...')
            return docker.images.pull(_DNS_PROXY_IMAGE_URI)

    def _start_dns_proxy(self, domains_to_whitelist):
        docker = BiolibDockerClient.get_docker_client()
        self._dns_proxy = docker.containers.create(
            detach=True,
            image=self._get_dns_proxy_image(),
            name=f'biolib-dns-proxy-{self._root_job_wrapper["job"]["public_id"]}',
            network=self._public_network.name,
        )

        blocky_config = '''
upstream:
    default:
        - 127.0.0.11
blocking:
    whiteLists:
        remoteHosts:
            - |'''
        for domain in domains_to_whitelist:
            blocky_config += f'''
              {domain}'''
        blocky_config += '''
    clientGroupsBlock:
        default:
            - remoteHosts
port: 53
'''

        blocky_config_bytes = blocky_config.encode()
        tarfile_in_memory = io.BytesIO()
        with tarfile.open(fileobj=tarfile_in_memory, mode='w:gz') as tar:
            info = tarfile.TarInfo('/config.yml')
            info.size = len(blocky_config_bytes)
            tar.addfile(info, io.BytesIO(blocky_config_bytes))

        tarfile_bytes = tarfile_in_memory.getvalue()
        tarfile_in_memory.close()
        docker.api.put_archive(self._dns_proxy.id, '/app', tarfile_bytes)

        self._internal_network.connect(self._dns_proxy.id)

        self._dns_proxy.start()

        proxy_is_ready = False
        for retry_count in range(1, 5):
            sleep(0.5 * retry_count)
            # Use the container logs as a health check.
            if b'TCP server is up and running' in self._dns_proxy.logs():
                proxy_is_ready = True
                break

        if not proxy_is_ready:
            self._dns_proxy.remove(force=True)
            raise Exception('DNS Proxy did not start properly')

        self._dns_proxy.reload()

    def _run_app_version(self, app_version_id: str, module_input_serialized: bytes, caller_job: Job) -> bytes:
        job: Job = BiolibJobApi.create(app_version_id, caller_job=caller_job['public_id'])
        self._jobs[job['public_id']] = job
        return self._run_job(job, module_input_serialized)

    def _run_job(self, job: Job, module_input_serialized: bytes) -> bytes:
        logger.info(f"Running job with id {job['public_id']}")
        if self._root_job_wrapper is None:
            raise Exception('root_job_wrapper was None')

        root_job = job
        while root_job['caller_job'] is not None and self._jobs.get(root_job['caller_job']) is not None:
            root_job = self._jobs[root_job['caller_job']]

        root_job_id = root_job['public_id']

        modules = job['app_version'].get('modules')

        if modules is None or not BiolibDockerClient.is_docker_running():
            return RemoteExecutor.execute_job(
                RemoteExecuteOptions(
                    biolib_base_url=self._root_job_wrapper['BASE_URL'],
                    job=job,
                    root_job_id=root_job_id,
                ),
                module_input_serialized,
            )

        main_module = self._get_module_from_name(modules, module_name='main')

        source_files_are_mapped = False
        lfs_dict: Dict[str, LargeFileSystem] = {}
        for module in modules:
            if len(module['source_files_mappings']) > 0:
                source_files_are_mapped = True

            for lfs_mapping in module['large_file_systems']:
                lfs = LargeFileSystem(
                    job_id=job['public_id'],
                    lfs_mapping=lfs_mapping,
                    send_status_update=self._send_status_update,
                )
                lfs.initialize()
                lfs_dict[lfs.uuid] = lfs

        runtime_zip_bytes: Optional[bytes] = None
        if source_files_are_mapped:
            runtime_zip_bytes = self._get_runtime_zip_as_bytes(root_job_id=root_job_id, app_version=job['app_version'])

        module_output_serialized = self._run_module(
            LocalExecutorOptions(
                access_token=self._root_job_wrapper['access_token'],
                biolib_base_url=self._root_job_wrapper['BASE_URL'],
                compute_node_info=self._root_job_wrapper.get('compute_node_info'),
                internal_network=self._internal_network,
                job=job,
                cloud_job=self._root_job_wrapper['cloud_job'],
                large_file_systems=lfs_dict,
                module=main_module,
                remote_host_proxies=self._remote_host_proxies,
                root_job_id=root_job_id,
                dns_proxy=self._dns_proxy,
                runtime_zip_bytes=runtime_zip_bytes,
                send_status_update=self._send_status_update,
                send_system_exception=self.send_system_exception,
                send_stdout_and_stderr=self.send_stdout_and_stderr,
            ),
            module_input_serialized,
        )

        for lfs in lfs_dict.values():
            lfs.detach()

        if utils.IS_RUNNING_IN_CLOUD:
            # Log memory and disk after pulling and executing module
            log_disk_and_memory_usage_info()

        return module_output_serialized

    def _run_module(self, options: LocalExecutorOptions, module_input_serialized: bytes) -> bytes:
        module = options['module']
        executor_instance: BaseExecutor

        if module['environment'] == ModuleEnvironment.BIOLIB_APP.value:
            module_input = ModuleInput(module_input_serialized).deserialize()
            module_input_with_runtime_zip = self._add_runtime_zip_and_command_to_module_input(options, module_input)
            module_input_with_runtime_zip_serialized = ModuleInput().serialize(
                stdin=module_input_with_runtime_zip['stdin'],
                arguments=module_input_with_runtime_zip['arguments'],
                files=module_input_with_runtime_zip['files']
            )
            return self._run_app_version(module['image_uri'], module_input_with_runtime_zip_serialized, options['job'])

        elif module['environment'] == ModuleEnvironment.BIOLIB_ECR.value:
            executor_instance = DockerExecutor(options)

        elif module['environment'] == ModuleEnvironment.BIOLIB_CUSTOM.value:
            executor_instance = PyppeteerExecutor(options)
        else:
            raise Exception(f"Unsupported module environment {module['environment']}")
        self._executors.append(executor_instance)

        if utils.IS_RUNNING_IN_CLOUD:
            # Log memory and disk before pulling and executing module
            log_disk_and_memory_usage_info()

        return executor_instance.execute_module(module_input_serialized)

    def _connect_to_parent(self):
        try:
            parent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            parent_socket.connect((SOCKET_HOST, int(self._socket_port)))

        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_CONNECT_TO_WORKER_THREAD_SOCKET.value,
                self.send_system_exception,
                may_contain_user_data=False
            ) from exception

        try:
            SocketListenerThread(parent_socket, self._received_messages_queue).start()
            SocketSenderThread(parent_socket, self._messages_to_send_queue).start()
        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_START_SENDER_THREAD_OR_RECEIVER_THREAD.value,
                self.send_system_exception,
                may_contain_user_data=False
            ) from exception

        try:
            if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
                attestation_document = self._nsm_util.get_attestation_doc()
            else:
                attestation_document = b'Running locally'
        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_GET_ATTESTATION_DOCUMENT.value,
                self.send_system_exception,
                may_contain_user_data=False
            ) from exception

        self._messages_to_send_queue.put(AttestationDocument().serialize(attestation_document))

    # TODO: move this mapping logic to the ModuleInput class
    def _add_runtime_zip_and_command_to_module_input(self, options: LocalExecutorOptions, module_input):
        module = options['module']
        runtime_zip_byes = options['runtime_zip_bytes']
        # TODO: Figure out if we ever forward output mappings correctly (Do we only the mapping of the base image?)
        # TODO: Reuse much of the make_runtime_tar logic in BiolibDockerClient
        try:
            if runtime_zip_byes:
                runtime_zip = zipfile.ZipFile(io.BytesIO(runtime_zip_byes))
                source_mappings = Mappings(module['source_files_mappings'], module_input['arguments'])
                for zip_file_name in runtime_zip.namelist():
                    file_path = '/' + path_without_first_folder(zip_file_name)
                    mapped_file_names = source_mappings.get_mappings_for_path(file_path)
                    for mapped_file_name in mapped_file_names:
                        file_data = runtime_zip.read(zip_file_name)
                        module_input['files'].update({mapped_file_name: file_data})

            for command_part in reversed(shlex.split(module['command'])):
                module_input['arguments'].insert(0, command_part)

        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_CREATE_NEW_JOB.value,
                self.send_system_exception,
                may_contain_user_data=False
            ) from exception

        return module_input

    def _get_runtime_zip_as_bytes(self, root_job_id: str, app_version: AppVersionOnJob) -> Optional[bytes]:
        runtime_zip_url = app_version['client_side_executable_zip']

        # TODO: change this to a is None check when backend is fixed to not return empty string
        if not runtime_zip_url:
            return None

        runtime_zip_bytes: Optional[bytes] = self._app_version_id_to_runtime_zip.get(app_version['public_id'])

        if runtime_zip_bytes is None:
            if root_job_id == utils.RUN_DEV_JOB_ID:
                with open(runtime_zip_url, mode='rb') as runtime_zip_file:
                    runtime_zip_bytes = runtime_zip_file.read()

            else:
                self._send_status_update(StatusUpdate(progress=25, log_message='Downloading Source Files...'))

                start_time = time()
                logger.debug('Downloading runtime zip from S3')
                try:
                    runtime_zip_bytes = requests.get(runtime_zip_url).content
                except Exception as exception:
                    raise ComputeProcessException(
                        exception,
                        SystemExceptionCodes.FAILED_TO_DOWNLOAD_RUNTIME_ZIP.value,
                        self.send_system_exception,
                        may_contain_user_data=False
                    ) from exception
                finally:
                    logger.debug(f'Downloading runtime zip took: {time() - start_time}s')

            self._app_version_id_to_runtime_zip[app_version['public_id']] = runtime_zip_bytes

        return runtime_zip_bytes

    @staticmethod
    def _get_module_from_name(modules: List[Module], module_name: str):
        for module in modules:
            if module['name'] == module_name:
                return module
        raise Exception(f'Could not find module with name {module_name}')

    def _wrap_in_aes_encrypted_package(self, package):
        iv = get_random_bytes(12)
        aes_key = AES.new(self._aes_key_buffer, AES.MODE_GCM, iv)
        encrypted_package, tag = aes_key.encrypt_and_digest(package)
        aes_encrypted_package = AesEncryptedPackage().serialize(iv, tag, encrypted_package)
        return aes_encrypted_package

    def send_system_exception(self, biolib_exception_code: SystemExceptionCodes) -> None:
        if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
            CloudUtils.log(
                log_message=str(biolib_exception_code),  # TODO: Switch back to logging full error message
                level=logging.ERROR
            )

        system_exception_package = SystemException().serialize(biolib_exception_code)
        self._messages_to_send_queue.put(system_exception_package)

    def send_stdout_and_stderr(self, stdout_and_stderr_bytes: bytes):
        stdout_and_stderr_package = StdoutAndStderr().serialize(
            stdout_and_stderr_bytes=stdout_and_stderr_bytes,
        )

        if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
            stdout_and_stderr_package = self._wrap_in_aes_encrypted_package(stdout_and_stderr_package)

        self._messages_to_send_queue.put(stdout_and_stderr_package)

    def _send_status_update(self, status_update: StatusUpdate) -> None:
        try:
            if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
                CloudUtils.log(
                    log_message=status_update['log_message'],
                    level=logging.INFO
                )

            status_update_package = SystemStatusUpdate().serialize(
                status_update['progress'],
                status_update['log_message'],
            )
            logger.debug(status_update['log_message'])
            self._messages_to_send_queue.put(status_update_package)
        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_SEND_STATUS_UPDATE.value,
                self.send_system_exception,
                may_contain_user_data=False
            ) from exception
