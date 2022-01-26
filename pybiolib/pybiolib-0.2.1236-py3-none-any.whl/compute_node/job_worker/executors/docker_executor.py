import time
import tarfile
import zipfile
import os
import io
import shlex

import docker  # type: ignore
from docker.errors import ImageNotFound, APIError  # type: ignore
from docker.models.containers import Container  # type: ignore

from biolib import utils
from biolib.biolib_binary_format import ModuleOutput, ModuleInput
from biolib.biolib_docker_client import BiolibDockerClient
from biolib.biolib_errors import DockerContainerNotFoundDuringExecutionException
from biolib.biolib_logging import logger
from biolib.compute_node import utils as compute_node_utils
from biolib.compute_node.job_worker.docker_image_cache import DockerImageCache
from biolib.compute_node.job_worker.executors.base_executor import BaseExecutor
from biolib.compute_node.job_worker.executors.types import StatusUpdate, LocalExecutorOptions
from biolib.compute_node.job_worker.mappings import Mappings, path_without_first_folder
from biolib.compute_node.job_worker.utils import ComputeProcessException
from biolib.compute_node.utils import SystemExceptionCodes
from biolib.typing_utils import List, Any, Dict, Optional
from biolib.utils import get_absolute_container_image_uri


class DockerExecutor(BaseExecutor):

    def __init__(self, options: LocalExecutorOptions):
        super().__init__(options)

        if self._options['root_job_id'] == utils.RUN_DEV_JOB_ID:
            self._image_uri = self._options['module']['image_uri']
        else:
            self._image_uri = get_absolute_container_image_uri(
                base_url=self._options['biolib_base_url'],
                relative_image_uri=self._options['module']['image_uri'],
                job_is_federated=True if self._options['job'].get('federated_job_uuid') else False
            )

        self._send_system_exception = options['send_system_exception']
        self._send_stdout_and_stderr = options['send_stdout_and_stderr']

        federated_job_uuid: Optional[str] = self._options['job'].get('federated_job_uuid')
        if options['compute_node_info'] is not None and not federated_job_uuid:
            compute_node_public_id = options['compute_node_info']['public_id']
            compute_node_auth_token = options['compute_node_info']['auth_token']
            # Use "|" to separate the fields as this makes it easy for the ECR proxy to split
            ecr_proxy_auth_token = f'cloud-{compute_node_public_id}|{compute_node_auth_token}'
        else:
            ecr_proxy_auth_token = options['access_token']

        docker_auth_job_id = federated_job_uuid or self._options['job']['public_id']
        self._docker_auth_config = {'username': 'AWS', 'password': f'{ecr_proxy_auth_token},{docker_auth_job_id}'}

        self._docker_container: Optional[Container] = None
        self._random_docker_id = compute_node_utils.random_string(15)
        self._compute_process_dir = os.path.dirname(os.path.realpath(__file__))
        self._runtime_tar_path = f'{self._compute_process_dir}/tars/runtime_{self._random_docker_id}.tar'
        self._input_tar_path = f'{self._compute_process_dir}/tars/input_{self._random_docker_id}.tar'

    def execute_module(self, module_input_serialized: bytes) -> bytes:
        send_status_update = self._options['send_status_update']
        send_system_exception = self._options['send_system_exception']

        module_input = ModuleInput(module_input_serialized).deserialize()

        # TODO: fix these status updates such that they also make sense for run-dev
        send_status_update(StatusUpdate(progress=55, log_message='Pulling images...'))

        self._pull()

        send_status_update(StatusUpdate(progress=70, log_message='Computing...'))
        start_time = time.time()

        stdout, stderr, exit_code, mapped_output_files = self._execute_helper(module_input)

        try:
            module_output_serialized: bytes = ModuleOutput().serialize(stdout, stderr, exit_code, mapped_output_files)
            logger.debug(f'Compute time: {time.time() - start_time}')
            return module_output_serialized

        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_SERIALIZE_AND_SEND_MODULE_OUTPUT.value,
                send_system_exception
            ) from exception
        finally:
            try:
                self.cleanup()
            except Exception:  # pylint: disable=broad-except
                logger.error('DockerExecutor failed to clean up container')

    def _pull(self):
        try:
            start_time = time.time()
            if utils.IS_RUNNING_IN_CLOUD:
                DockerImageCache().get(
                    image_uri=self._image_uri,
                    estimated_image_size_bytes=self._options['module']['estimated_image_size_bytes'],
                    pull_auth_config=self._docker_auth_config,
                    job_id=self._options['job']['public_id']
                )
            else:
                docker_client = BiolibDockerClient.get_docker_client()
                try:
                    docker_client.images.get(self._image_uri)
                except ImageNotFound:
                    docker_client.images.pull(self._image_uri, auth_config=self._docker_auth_config)
            logger.debug(f'Pulled image in: {time.time() - start_time}')

        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_PULL_DOCKER_IMAGE.value,
                self._send_system_exception,
                may_contain_user_data=False
            ) from exception

    def _execute_helper(self, module_input):
        self._initialize_docker_container(module_input)

        if self._options['runtime_zip_bytes']:
            self._map_and_copy_runtime_files_to_container(self._options['runtime_zip_bytes'], module_input['arguments'])

        self._map_and_copy_input_files_to_container(module_input['files'], module_input['arguments'])

        try:
            docker_api_client = BiolibDockerClient.get_docker_client().api
            logger.debug('Starting Docker container')

            stdout_and_stderr_stream = docker_api_client.attach(
                container=self._docker_container.id,
                stderr=True,
                stdout=True,
                stream=True,
            )

            self._docker_container.start()

            if self._options['job']['app_version'].get('stdout_render_type') != 'markdown':
                for stdout_and_stderr in stdout_and_stderr_stream:
                    if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE and stdout_and_stderr:
                        stdout_and_stderr = stdout_and_stderr.replace(
                            b'OpenBLAS WARNING - could not determine the L2 cache size on this system, assuming 256k\r\n',  # pylint: disable=line-too-long
                            b'',
                        )

                    # Default messages to empty bytestring instead of None
                    stdout_and_stderr = stdout_and_stderr if stdout_and_stderr is not None else b''

                    self._send_stdout_and_stderr(stdout_and_stderr)

            exit_code = docker_api_client.wait(self._docker_container.id)['StatusCode']
            # 137 is the error code from linux OOM killer (Should catch 90% of OOM errors)
            if exit_code == 137:
                raise ComputeProcessException(
                    MemoryError(),
                    SystemExceptionCodes.OUT_OF_MEMORY.value,
                    self._send_system_exception
                )

            logger.debug(f'Docker container exited with code {exit_code}')

            full_stdout = docker_api_client.logs(self._docker_container.id, stdout=True, stderr=False)
            full_stderr = docker_api_client.logs(self._docker_container.id, stdout=False, stderr=True)

            if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
                full_stderr = full_stderr.replace(
                    b'OpenBLAS WARNING - could not determine the L2 cache size on this system, assuming 256k\n',
                    b'',
                )
                full_stdout = full_stdout.replace(
                    b'OpenBLAS WARNING - could not determine the L2 cache size on this system, assuming 256k\r\n',
                    b'',
                )

            mapped_output_files = self._get_output_files(arguments=module_input['arguments'])
            return full_stdout, full_stderr, exit_code, mapped_output_files

        except docker.errors.NotFound as docker_error:
            raise DockerContainerNotFoundDuringExecutionException from docker_error

        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_RUN_COMPUTE_CONTAINER.value,
                self._send_system_exception
            ) from exception

    def cleanup(self):
        # Don't clean up if already in the process of doing so, or done doing so
        if self._is_cleaning_up:
            return
        else:
            self._is_cleaning_up = True

        tar_time = time.time()
        for path_to_delete in [self._input_tar_path, self._runtime_tar_path]:
            if os.path.exists(path_to_delete):
                os.remove(path_to_delete)
        logger.debug(f"Deleted tars in: {time.time() - tar_time}")

        container_time = time.time()
        if self._docker_container:
            self._docker_container.remove(force=True)

        if utils.IS_RUNNING_IN_CLOUD:
            DockerImageCache().detach_job(
                image_uri=self._image_uri,
                job_id=self._options['job']['public_id']
            )

        logger.debug(f"Deleted compute container in: {time.time() - container_time}")

    # TODO: type this method
    def _initialize_docker_container(self, module_input):
        try:
            module = self._options['module']
            logger.debug(f"Initializing docker container with command: {module['command']}")

            docker_volume_mounts = [lfs.docker_mount for lfs in self._options['large_file_systems'].values()]

            internal_network = self._options['internal_network']
            extra_hosts: Dict[str, str] = {}
            dns_list: List[str] = []

            for proxy in self._options['remote_host_proxies']:
                extra_hosts[proxy.hostname] = proxy.get_ip_address_on_network(internal_network)

            if self._options['dns_proxy']:
                container_networks = self._options['dns_proxy'].attrs['NetworkSettings']['Networks']
                dns_proxy_ip_address: str = container_networks[internal_network.name]['IPAddress']
                dns_list = [dns_proxy_ip_address]

            create_container_args = {
                'command': shlex.split(module['command']) + module_input['arguments'],
                'environment': module.get('secrets') or {},
                'extra_hosts': extra_hosts,
                'image': self._image_uri,
                'mounts': docker_volume_mounts,
                'network': internal_network.name,
                'working_dir': module['working_directory'],
                'dns': dns_list
            }

            app_version = self._options['job']['app_version']
            if app_version.get('main_output_file') or app_version.get('stdout_render_type') == 'text':
                create_container_args['tty'] = True

            if utils.IS_RUNNING_IN_CLOUD:
                create_container_args['mem_limit'] = f'{self._options["cloud_job"]["reserved_memory_in_bytes"]}b'
                create_container_args['nano_cpus'] = self._options["cloud_job"]["reserved_cpu_in_nano_shares"]

                if not utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
                    docker_runtime = os.getenv('BIOLIB_DOCKER_RUNTIME')
                    if docker_runtime is not None:
                        create_container_args['runtime'] = docker_runtime

            self._docker_container = BiolibDockerClient.get_docker_client().containers.create(
                **create_container_args
            )

            logger.debug('Finished initializing docker container')
        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_START_COMPUTE_CONTAINER.value,
                self._send_system_exception
            ) from exception

    def _add_file_to_tar(self, tar, current_path, mapped_path, data):
        if current_path.endswith('/'):
            # Remove trailing slash as tarfile.addfile appends it automatically
            tarinfo = tarfile.TarInfo(name=mapped_path[:-1])
            tarinfo.type = tarfile.DIRTYPE
            tar.addfile(tarinfo)

        else:
            tarinfo = tarfile.TarInfo(name=mapped_path)
            file_like = io.BytesIO(data)
            tarinfo.size = len(file_like.getvalue())
            tar.addfile(tarinfo, file_like)

    def _make_input_tar(self, files, arguments: List[str]):
        module = self._options['module']
        input_tar = tarfile.open(self._input_tar_path, 'w')
        input_mappings = Mappings(module['input_files_mappings'], arguments)
        for path, data in files.items():
            # Make all paths absolute
            if not path.startswith('/'):
                path = '/' + path

            mapped_file_names = input_mappings.get_mappings_for_path(path)
            for mapped_file_name in mapped_file_names:
                self._add_file_to_tar(tar=input_tar, current_path=path, mapped_path=mapped_file_name, data=data)

        input_tar.close()

    def _make_runtime_tar(self, runtime_zip_data, arguments: List[str], remove_root_folder=True):
        module = self._options['module']
        runtime_tar = tarfile.open(self._runtime_tar_path, 'w')
        runtime_zip = zipfile.ZipFile(io.BytesIO(runtime_zip_data))
        source_mappings = Mappings(module['source_files_mappings'], arguments)

        for zip_file_name in runtime_zip.namelist():
            # Make paths absolute and remove root folder from path
            if remove_root_folder:
                file_path = '/' + path_without_first_folder(zip_file_name)
            else:
                file_path = '/' + zip_file_name
            mapped_file_names = source_mappings.get_mappings_for_path(file_path)
            for mapped_file_name in mapped_file_names:
                file_data = runtime_zip.read(zip_file_name)
                self._add_file_to_tar(
                    tar=runtime_tar,
                    current_path=zip_file_name,
                    mapped_path=mapped_file_name,
                    data=file_data,
                )

        runtime_tar.close()

    def _map_and_copy_input_files_to_container(self, files, arguments: List[str]):
        try:
            if self._docker_container is None:
                raise Exception('Docker container was None')

            self._make_input_tar(files, arguments)
            input_tar_bytes = open(self._input_tar_path, 'rb').read()
            BiolibDockerClient.get_docker_client().api.put_archive(self._docker_container.id, '/', input_tar_bytes)
        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_COPY_INPUT_FILES_TO_COMPUTE_CONTAINER.value,
                self._send_system_exception
            ) from exception

    def _map_and_copy_runtime_files_to_container(self, runtime_zip_data, arguments: List[str], remove_root_folder=True):
        try:
            if self._docker_container is None:
                raise Exception('Docker container was None')

            self._make_runtime_tar(runtime_zip_data, arguments, remove_root_folder)
            runtime_tar_bytes = open(self._runtime_tar_path, 'rb').read()
            BiolibDockerClient.get_docker_client().api.put_archive(self._docker_container.id, '/', runtime_tar_bytes)
        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_COPY_RUNTIME_FILES_TO_COMPUTE_CONTAINER.value,
                self._send_system_exception
            ) from exception

    def _get_output_files(self, arguments: List[str]):
        module = self._options['module']
        try:
            if self._docker_container is None:
                raise Exception('Docker container was None')

            docker_api_client = BiolibDockerClient.get_docker_client().api

            # TODO: fix typing
            input_tar: Any = None
            if os.path.exists(self._input_tar_path):
                input_tar = tarfile.open(self._input_tar_path)
                input_tar_filelist = input_tar.getnames()

            # TODO: fix typing
            runtime_tar: Any = None
            if os.path.exists(self._runtime_tar_path):
                runtime_tar = tarfile.open(self._runtime_tar_path)
                runtime_tar_filelist = runtime_tar.getnames()

            mapped_output_files = {}
            for mapping in module['output_files_mappings']:
                try:
                    tar_bytes_generator, _ = docker_api_client.get_archive(
                        self._docker_container.id, mapping['from_path'])
                except APIError:
                    logger.warning(f'Could not get output from path {mapping["from_path"]}')
                    continue

                tar_bytes_obj = io.BytesIO()
                for chunk in tar_bytes_generator:
                    tar_bytes_obj.write(chunk)

                tar = tarfile.open(fileobj=io.BytesIO(tar_bytes_obj.getvalue()))
                for file in tar.getmembers():
                    file_obj = tar.extractfile(file)

                    # Skip empty dirs
                    if not file_obj:
                        continue
                    file_data = file_obj.read()

                    # Remove parent dir from tar file name and prepend from_path.
                    # Except if from_path is root '/', that works out of the box
                    if mapping['from_path'].endswith('/') and mapping['from_path'] != '/':
                        file_name = mapping['from_path'] + path_without_first_folder(file.name)

                    # When getting a file use the from_path.
                    # This is due to directory info (absolute path) being lost when using get_archive on files
                    else:
                        file_name = mapping['from_path']

                    # Filter out unchanged input files
                    if input_tar and file_name in input_tar_filelist and \
                            input_tar.extractfile(file_name).read() == file_data:
                        continue

                    # Filter out unchanged source files if provided
                    if runtime_tar and file_name in runtime_tar_filelist and runtime_tar.extractfile(
                            file_name).read() == file_data:
                        continue

                    mapped_file_names = Mappings([mapping], arguments).get_mappings_for_path(file_name)
                    for mapped_file_name in mapped_file_names:
                        mapped_output_files[mapped_file_name] = file_data

        except Exception as exception:
            raise ComputeProcessException(
                exception,
                SystemExceptionCodes.FAILED_TO_RUN_COMPUTE_CONTAINER.value,
                self._send_system_exception
            ) from exception

        return mapped_output_files
