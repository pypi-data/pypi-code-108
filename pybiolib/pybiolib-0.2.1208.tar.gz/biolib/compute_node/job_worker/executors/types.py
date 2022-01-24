from docker.models.containers import Container  # type: ignore
from docker.models.networks import Network  # type: ignore

from biolib.compute_node.job_worker.large_file_system import LargeFileSystem
from biolib.compute_node.webserver.webserver_types import ComputeNodeInfo
from biolib.typing_utils import TypedDict, Callable, Optional, List, Dict
from biolib.compute_node.remote_host_proxy import RemoteHostProxy
from biolib.biolib_api_client.app_types import Module
from biolib.biolib_api_client.job_types import Job, CloudJob
from biolib.compute_node.utils import SystemExceptionCodes


class StatusUpdate(TypedDict):
    progress: int
    log_message: str


class RemoteExecuteOptions(TypedDict):
    biolib_base_url: str
    job: Job
    root_job_id: str


SendStatusUpdateType = Callable[[StatusUpdate], None]
SendSystemExceptionType = Callable[[SystemExceptionCodes], None]
SendStdoutAndStderrType = Callable[[bytes], None]


class LocalExecutorOptions(TypedDict):
    access_token: str
    biolib_base_url: str
    compute_node_info: Optional[ComputeNodeInfo]
    internal_network: Optional[Network]
    job: Job
    cloud_job: Optional[CloudJob]
    large_file_systems: Dict[str, LargeFileSystem]
    module: Module
    dns_proxy: Optional[Container]
    remote_host_proxies: List[RemoteHostProxy]
    root_job_id: str
    runtime_zip_bytes: Optional[bytes]  # TODO: replace this with a module_source_serialized
    send_status_update: SendStatusUpdateType
    send_system_exception: SendSystemExceptionType
    send_stdout_and_stderr: SendStdoutAndStderrType
