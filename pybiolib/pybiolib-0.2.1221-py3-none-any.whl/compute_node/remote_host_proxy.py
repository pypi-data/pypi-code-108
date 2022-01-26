import io
import tarfile
import subprocess
import time

from docker.models.containers import Container  # type: ignore
from docker.errors import ImageNotFound  # type: ignore
from docker.models.images import Image  # type: ignore
from docker.models.networks import Network  # type: ignore

from biolib import utils
from biolib.compute_node import enclave
from biolib.compute_node.cloud_utils.enclave_parent_types import VsockProxyResponse
from biolib.compute_node.cloud_utils import CloudUtils
from biolib.typing_utils import Optional, List
from biolib.biolib_api_client import RemoteHost
from biolib.biolib_docker_client import BiolibDockerClient
from biolib.biolib_logging import logger


# Prepare for remote hosts with specified port
class RemoteHostExtended(RemoteHost):
    ports: List[int]


class RemoteHostProxy:
    _DOCKER_IMAGE_URI = 'nginx:1.21.1-alpine'
    _TRAFFIC_FORWARDER_PORT_OFFSET = 10000  # Port offset relative to port of a VSOCK proxy

    def __init__(
            self,
            remote_host: RemoteHost,
            public_network: Network,
            internal_network: Optional[Network],
            job_id: Optional[str],
            ports: List[int]
    ):
        # Default to port 443 for now until backend serves remote_hosts with port specified
        self._remote_host: RemoteHostExtended = RemoteHostExtended(
            hostname=remote_host['hostname'],
            ports=ports
        )
        self._public_network: Network = public_network
        self._internal_network: Optional[Network] = internal_network

        if job_id:
            self._name = f"biolib-remote-host-proxy-{job_id}-{self.hostname}"
        else:
            if not utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
                raise Exception('RemoteHostProxy missing argument "job_id"')
            self._name = f"biolib-enclave-remote-host-proxy-{self.hostname}"

        self._container: Optional[Container] = None
        self._enclave_traffic_forwarder_processes: List[subprocess.Popen] = []
        self._enclave_vsock_proxies: List[VsockProxyResponse] = []

    @property
    def hostname(self) -> str:
        return self._remote_host['hostname']

    def get_ip_address_on_network(self, network: Network) -> str:
        if not self._container:
            raise Exception('RemoteHostProxy not yet started')

        container_networks = self._container.attrs['NetworkSettings']['Networks']
        if network.name in container_networks:
            ip_address: str = container_networks[network.name]['IPAddress']
            return ip_address

        raise Exception(f'RemoteHostProxy not connected to network {network.name}')

    def start(self) -> None:
        # TODO: Implement nice error handling in this method

        upstream_server_name = self._remote_host['hostname']
        upstream_server_ports = self._remote_host['ports']

        if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
            # In an enclave the flow is: application -> remote host proxy -> traffic forwarder -> VSOCK proxy -> remote
            upstream_server_name = self._public_network.attrs['IPAM']['Config'][0]['Gateway']
            upstream_server_ports = self._start_vsock_proxy_and_traffic_forwarder_and_return_local_ports()

        docker = BiolibDockerClient.get_docker_client()
        self._container = docker.containers.create(
            detach=True,
            image=self._get_nginx_docker_image(),
            name=self._name,
            network=self._public_network.name,
        )

        self._write_nginx_config_to_container(
            upstream_server_name,
            upstream_server_ports,
        )

        if self._internal_network:
            self._internal_network.connect(self._container.id)

        self._container.start()

        proxy_is_ready = False
        for retry_count in range(1, 5):
            time.sleep(0.5 * retry_count)
            # Use the container logs as a health check.
            # By using logs instead of a http endpoint on the NGINX we avoid publishing a port of container to the host
            if b'start worker process ' in self._container.logs():
                proxy_is_ready = True
                break

        if not proxy_is_ready:
            self.terminate()
            raise Exception('RemoteHostProxy did not start properly')

        self._container.reload()

    def terminate(self):
        # TODO: Implement nice error handling in this method

        if self._container:
            self._container.remove(force=True)

        for process in self._enclave_traffic_forwarder_processes:
            process.terminate()

        for proxy in self._enclave_vsock_proxies:
            CloudUtils.enclave.stop_vsock_proxy(proxy['id'])

    def _get_nginx_docker_image(self) -> Image:
        docker = BiolibDockerClient.get_docker_client()
        try:
            return docker.images.get(self._DOCKER_IMAGE_URI)
        except ImageNotFound:
            logger.debug('Pulling remote host docker image...')
            return docker.images.pull(self._DOCKER_IMAGE_URI)

    def _start_vsock_proxy_and_traffic_forwarder_and_return_local_ports(self) -> List[int]:
        # TODO: Implement nice error handling in this method

        if not utils.BIOLIB_IS_RUNNING_IN_ENCLAVE:
            raise Exception('VSOCK proxy and traffic forwarder should only be started in enclave')

        logger.debug(f"Requesting vsock proxies for hostname {self.hostname}")
        traffic_forwarder_local_ports = []
        for port in self._remote_host['ports']:
            enclave_vsock_proxy = CloudUtils.enclave.start_vsock_proxy(
                hostname=self.hostname,
                port=port
            )
            self._enclave_vsock_proxies.append(enclave_vsock_proxy)

            traffic_forwarder_local_port = enclave_vsock_proxy['port'] + self._TRAFFIC_FORWARDER_PORT_OFFSET
            traffic_forwarder_local_ports.append(traffic_forwarder_local_port)
            logger.debug(
                f"Starting traffic forwarder on local port {traffic_forwarder_local_port} to "
                f"VSOCK port {enclave_vsock_proxy['port']} for hostname {self.hostname}"
            )
            self._enclave_traffic_forwarder_processes.append(
                subprocess.Popen([
                    'biolib_traffic_forwarder',
                    str(traffic_forwarder_local_port),
                    str(enclave.PARENT_CID),
                    str(enclave_vsock_proxy['port']),
                ])
            )
        return traffic_forwarder_local_ports

    def _write_nginx_config_to_container(self, upstream_server_name: str, upstream_server_ports: List[int]) -> None:
        if not self._container:
            raise Exception('RemoteHostProxy container not defined when attempting to write NGINX config')

        docker = BiolibDockerClient.get_docker_client()
        nginx_config = '''
events {}
error_log /dev/stdout info;
stream {
    resolver 127.0.0.11 valid=30s;'''
        for idx, upstream_server_port in enumerate(upstream_server_ports):
            nginx_config += f'''
    map "" $upstream_{idx} {{
        default {upstream_server_name}:{upstream_server_port};
    }}

    server {{
        listen          {self._remote_host['ports'][idx]};
        proxy_pass      $upstream_{idx};
    }}

    server {{
        listen          {self._remote_host['ports'][idx]} udp;
        proxy_pass      $upstream_{idx};
    }}'''

        nginx_config += '''
}
'''
        nginx_config_bytes = nginx_config.encode()
        tarfile_in_memory = io.BytesIO()
        with tarfile.open(fileobj=tarfile_in_memory, mode='w:gz') as tar:
            info = tarfile.TarInfo('/nginx.conf')
            info.size = len(nginx_config_bytes)
            tar.addfile(info, io.BytesIO(nginx_config_bytes))

        tarfile_bytes = tarfile_in_memory.getvalue()
        tarfile_in_memory.close()
        docker.api.put_archive(self._container.id, '/etc/nginx', tarfile_bytes)
