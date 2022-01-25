"""Platform config client."""
from pkg_resources import get_distribution

from .client import ConfigClient
from .models import (
    ARecord,
    Cluster,
    DNSConfig,
    MetricsConfig,
    MonitoringConfig,
    OrchestratorConfig,
    RegistryConfig,
    ResourcePoolType,
    ResourcePreset,
    SecretsConfig,
    StorageConfig,
    TPUPreset,
    TPUResource,
)

__all__ = [
    "ConfigClient",
    "DNSConfig",
    "ARecord",
    "Cluster",
    "MetricsConfig",
    "MonitoringConfig",
    "OrchestratorConfig",
    "RegistryConfig",
    "ResourcePoolType",
    "ResourcePreset",
    "SecretsConfig",
    "StorageConfig",
    "TPUPreset",
    "TPUResource",
]
__version__ = get_distribution(__name__).version
