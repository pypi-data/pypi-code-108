from urllib.parse import urlparse
from biolib.biolib_api_client import RemoteHost
from biolib.biolib_docker_client import BiolibDockerClient
from biolib.biolib_logging import logger
from biolib.compute_node.remote_host_proxy import RemoteHostProxy
from biolib.compute_node.webserver.webserver_types import WebserverConfig
from biolib.typing_utils import List



def start_enclave_remote_hosts(config: WebserverConfig) -> None:
    logger.debug('Starting Docker network for enclave remote host proxies')
    docker = BiolibDockerClient.get_docker_client()
    public_network = docker.networks.create(
        driver='bridge',
        internal=False,
        name='biolib-enclave-remote-hosts-network',
    )

    biolib_remote_hosts: List[RemoteHost] = []
    biolib_remote_host_proxies: List[RemoteHostProxy] = []
    base_hostname = urlparse(config['base_url']).hostname
    # Make sure base_hostname is not None for typing reasons
    if not base_hostname:
        raise Exception('Base hostname not set, likely due to base url not being set. This is required in enclaves')

    if base_hostname == 'biolib.com':
        biolib_remote_hosts.append(RemoteHost(hostname='containers.biolib.com'))
    elif base_hostname == 'staging-elb.biolib.com':
        biolib_remote_hosts.append(RemoteHost(hostname='containers.staging.biolib.com'))

    # Allow reaching backend for self registering and job creation
    biolib_remote_hosts.append(RemoteHost(hostname=base_hostname))
    # For downloading container image layers from S3 URLs returned by ECR proxy
    biolib_remote_hosts.append(RemoteHost(
        hostname=f"prod-{config['ecr_region_name']}-starport-layer-bucket.s3.{config['ecr_region_name']}.amazonaws.com"
    ))
    # For downloading source files zip
    biolib_remote_hosts.append(RemoteHost(
        hostname=f"{config['s3_general_storage_bucket_name']}.s3.amazonaws.com"
    ))

    logger.debug('Starting enclave remote host proxies')
    for remote_host in biolib_remote_hosts:
        remote_host_proxy = RemoteHostProxy(
            remote_host,
            public_network=public_network,
            internal_network=None,
            job_id=None,
            ports=[443]  # biolib hosts are all HTTPS rest endpoints
        )
        remote_host_proxy.start()
        biolib_remote_host_proxies.append(remote_host_proxy)

    logger.debug('Writing to enclave /etc/hosts')
    with open('/etc/hosts', mode='a') as hosts_file:
        for proxy in biolib_remote_host_proxies:
            ip_address = proxy.get_ip_address_on_network(public_network)
            hosts_file.write(f'\n{ip_address} {proxy.hostname}')
