from biolib.typing_utils import TypedDict


class ComputeNodeInfo(TypedDict):
    auth_token: str
    public_id: str
    ip_address: str


class ShutdownTimes(TypedDict):
    auto_shutdown_time_in_seconds: int
    job_max_runtime_shutdown_time_in_seconds: int


class WebserverConfig(TypedDict):
    base_url: str
    ecr_region_name: str
    max_docker_image_cache_size_bytes: int
    s3_general_storage_bucket_name: str
    s3_lfs_bucket_name: str
    compute_node_info: ComputeNodeInfo
    is_dev: bool
    shutdown_times: ShutdownTimes
