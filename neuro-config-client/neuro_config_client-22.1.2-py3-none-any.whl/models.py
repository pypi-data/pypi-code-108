import enum
from collections.abc import Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from yarl import URL


@dataclass(frozen=True)
class VolumeConfig:
    size_mb: Optional[int] = None
    path: Optional[str] = None


@dataclass(frozen=True)
class StorageConfig:
    url: URL
    volumes: Sequence[VolumeConfig] = ()


@dataclass(frozen=True)
class BlobStorageConfig:
    url: URL


@dataclass(frozen=True)
class RegistryConfig:
    url: URL


@dataclass(frozen=True)
class MonitoringConfig:
    url: URL


@dataclass(frozen=True)
class MetricsConfig:
    url: URL


@dataclass(frozen=True)
class SecretsConfig:
    url: URL


@dataclass(frozen=True)
class DisksConfig:
    url: URL
    storage_limit_per_user_gb: int


@dataclass(frozen=True)
class BucketsConfig:
    url: URL
    disable_creation: bool = False


class ACMEEnvironment(str, enum.Enum):
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass(frozen=True)
class IngressConfig:
    acme_environment: ACMEEnvironment
    cors_origins: Sequence[str] = ()


@dataclass(frozen=True)
class TPUResource:
    ipv4_cidr_block: str
    types: Sequence[str] = field(default_factory=list)
    software_versions: Sequence[str] = field(default_factory=list)


@dataclass(frozen=True)
class TPUPreset:
    type: str
    software_version: str


@dataclass(frozen=True)
class ResourcePreset:
    name: str
    credits_per_hour: Decimal
    cpu: float
    memory_mb: int
    gpu: Optional[int] = None
    gpu_model: Optional[str] = None
    tpu: Optional[TPUPreset] = None
    scheduler_enabled: bool = False
    preemptible_node: bool = False
    resource_affinity: Sequence[str] = ()


@dataclass(frozen=True)
class ResourcePoolType:
    name: str
    min_size: int = 0
    max_size: int = 1
    idle_size: int = 0
    cpu: float = 1.0
    available_cpu: float = 1.0
    memory_mb: int = 1024
    available_memory_mb: int = 1024
    disk_size_gb: int = 150
    gpu: Optional[int] = None
    gpu_model: Optional[str] = None
    price: Decimal = Decimal()
    currency: Optional[str] = None
    tpu: Optional[TPUResource] = None
    is_preemptible: bool = False


@dataclass(frozen=True)
class Resources:
    cpu_m: int
    memory_mb: int
    gpu: int = 0


@dataclass(frozen=True)
class IdleJobConfig:
    count: int
    image: str
    resources: Resources
    image_secret: str = ""
    env: dict[str, str] = field(default_factory=dict)
    node_selector: dict[str, str] = field(default_factory=dict)


@dataclass
class OrchestratorConfig:
    job_hostname_template: str
    job_internal_hostname_template: str
    job_fallback_hostname: str
    job_schedule_timeout_s: float
    job_schedule_scale_up_timeout_s: float
    is_http_ingress_secure: bool = True
    resource_pool_types: Sequence[ResourcePoolType] = field(default_factory=list)
    resource_presets: Sequence[ResourcePreset] = field(default_factory=list)
    allow_privileged_mode: bool = False
    pre_pull_images: Sequence[str] = ()
    idle_jobs: Sequence[IdleJobConfig] = field(default_factory=list)


@dataclass
class ARecord:
    name: str
    ips: Sequence[str] = field(default_factory=list)
    dns_name: str = ""
    zone_id: str = ""
    evaluate_target_health: bool = False


@dataclass
class DNSConfig:
    name: str
    a_records: Sequence[ARecord] = field(default_factory=list)


@dataclass(frozen=True)
class Cluster:
    name: str
    orchestrator: Optional[OrchestratorConfig] = None
    storage: Optional[StorageConfig] = None
    blob_storage: Optional[BlobStorageConfig] = None
    registry: Optional[RegistryConfig] = None
    monitoring: Optional[MonitoringConfig] = None
    secrets: Optional[SecretsConfig] = None
    metrics: Optional[MetricsConfig] = None
    dns: Optional[DNSConfig] = None
    disks: Optional[DisksConfig] = None
    buckets: Optional[BucketsConfig] = None
    ingress: Optional[IngressConfig] = None
