from decimal import Decimal
from unittest import mock

import pytest
from yarl import URL

from neuro_config_client.converters import PrimitiveToClusterConverter
from neuro_config_client.models import (
    ACMEEnvironment,
    ARecord,
    BlobStorageConfig,
    BucketsConfig,
    Cluster,
    DisksConfig,
    DNSConfig,
    IdleJobConfig,
    IngressConfig,
    MetricsConfig,
    MonitoringConfig,
    OrchestratorConfig,
    RegistryConfig,
    ResourcePoolType,
    ResourcePreset,
    Resources,
    SecretsConfig,
    StorageConfig,
    TPUPreset,
    TPUResource,
    VolumeConfig,
)


class TestPrimitiveToCLusterConverter:
    @pytest.fixture
    def converter(self) -> PrimitiveToClusterConverter:
        return PrimitiveToClusterConverter()

    def test_convert_empty_cluster(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_cluster({"name": "default"})

        assert result == Cluster(name="default")

    def test_convert_cluster(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_cluster(
            {
                "name": "default",
                "orchestrator": {
                    "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
                    "job_fallback_hostname": "default.jobs-dev.neu.ro",
                    "job_schedule_timeout_s": 1,
                    "job_schedule_scale_up_timeout_s": 2,
                    "is_http_ingress_secure": False,
                    "resource_pool_types": [{"name": "node-pool"}],
                    "allow_privileged_mode": False,
                },
                "storage": {"url": "https://storage-dev.neu.ro"},
                "registry": {
                    "url": "https://registry-dev.neu.ro",
                    "email": "dev@neu.ro",
                },
                "monitoring": {"url": "https://monitoring-dev.neu.ro"},
                "secrets": {"url": "https://secrets-dev.neu.ro"},
                "metrics": {"url": "https://secrets-dev.neu.ro"},
                "disks": {
                    "url": "https://secrets-dev.neu.ro",
                    "storage_limit_per_user_gb": 1024,
                },
                "ingress": {"acme_environment": "production"},
                "dns": {
                    "name": "neu.ro",
                    "a_records": [
                        {"name": "*.jobs-dev.neu.ro.", "ips": ["192.168.0.2"]}
                    ],
                },
            }
        )

        assert result.name == "default"
        assert result.orchestrator
        assert result.storage
        assert result.registry
        assert result.monitoring
        assert result.secrets
        assert result.metrics
        assert result.disks
        assert result.ingress
        assert result.dns

    def test_convert_orchestrator(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_orchestrator(
            {
                "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
                "job_internal_hostname_template": "{job_id}.platform-jobs",
                "job_fallback_hostname": "default.jobs-dev.neu.ro",
                "job_schedule_timeout_s": 1,
                "job_schedule_scale_up_timeout_s": 2,
                "is_http_ingress_secure": False,
                "resource_pool_types": [{"name": "node-pool"}],
                "resource_presets": [
                    {
                        "name": "cpu-micro",
                        "credits_per_hour": "10",
                        "cpu": 0.1,
                        "memory_mb": 100,
                    }
                ],
                "allow_privileged_mode": False,
                "pre_pull_images": ["neuromation/base"],
                "idle_jobs": [
                    {
                        "count": 1,
                        "image": "miner",
                        "resources": {"cpu_m": 1000, "memory_mb": 1024},
                    }
                ],
            }
        )

        assert result == OrchestratorConfig(
            job_hostname_template="{job_id}.jobs-dev.neu.ro",
            job_internal_hostname_template="{job_id}.platform-jobs",
            job_fallback_hostname="default.jobs-dev.neu.ro",
            job_schedule_timeout_s=1,
            job_schedule_scale_up_timeout_s=2,
            is_http_ingress_secure=False,
            resource_pool_types=[mock.ANY],
            resource_presets=[mock.ANY],
            allow_privileged_mode=False,
            pre_pull_images=["neuromation/base"],
            idle_jobs=[
                IdleJobConfig(
                    count=1,
                    image="miner",
                    resources=Resources(cpu_m=1000, memory_mb=1024),
                )
            ],
        )

    def test_convert_orchestrator_default(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_orchestrator(
            {
                "job_hostname_template": "{job_id}.jobs-dev.neu.ro",
                "job_fallback_hostname": "default.jobs-dev.neu.ro",
                "job_schedule_timeout_s": 1,
                "job_schedule_scale_up_timeout_s": 2,
                "is_http_ingress_secure": False,
                "allow_privileged_mode": False,
            }
        )

        assert result == OrchestratorConfig(
            job_hostname_template="{job_id}.jobs-dev.neu.ro",
            job_internal_hostname_template="",
            job_fallback_hostname="default.jobs-dev.neu.ro",
            job_schedule_timeout_s=1,
            job_schedule_scale_up_timeout_s=2,
            is_http_ingress_secure=False,
            allow_privileged_mode=False,
        )

    def test_convert_resource_pool_type(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_resource_pool_type(
            {
                "name": "n1-highmem-4",
                "min_size": 1,
                "max_size": 2,
                "idle_size": 1,
                "cpu": 4.0,
                "available_cpu": 3.0,
                "memory_mb": 12 * 1024,
                "available_memory_mb": 10 * 1024,
                "disk_size_gb": 700,
                "gpu": 1,
                "gpu_model": "nvidia-tesla-k80",
                "tpu": {
                    "ipv4_cidr_block": "10.0.0.0/8",
                    "types": ["tpu"],
                    "software_versions": ["v1"],
                },
                "is_preemptible": True,
                "price": "1.0",
                "currency": "USD",
            }
        )

        assert result == ResourcePoolType(
            name="n1-highmem-4",
            min_size=1,
            max_size=2,
            idle_size=1,
            cpu=4.0,
            available_cpu=3.0,
            memory_mb=12 * 1024,
            available_memory_mb=10 * 1024,
            gpu=1,
            gpu_model="nvidia-tesla-k80",
            tpu=mock.ANY,
            is_preemptible=True,
            price=Decimal("1.0"),
            currency="USD",
        )

    def test_convert_empty_resource_pool_type(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_resource_pool_type({"name": "node-pool"})

        assert result == ResourcePoolType(name="node-pool")

    def test_convert_tpu_resource(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_tpu_resource(
            {
                "ipv4_cidr_block": "10.0.0.0/8",
                "types": ["tpu"],
                "software_versions": ["v1"],
            }
        )

        assert result == TPUResource(
            ipv4_cidr_block="10.0.0.0/8", types=["tpu"], software_versions=["v1"]
        )

    def test_convert_resource_preset(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_resource_preset(
            {
                "name": "cpu-small",
                "credits_per_hour": "10",
                "cpu": 4.0,
                "memory_mb": 1024,
            }
        )

        assert result == ResourcePreset(
            name="cpu-small", credits_per_hour=Decimal("10"), cpu=4.0, memory_mb=1024
        )

    def test_convert_resource_preset_with_memory_gpu_tpu_preemptible_affinity(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_resource_preset(
            {
                "name": "gpu-small",
                "credits_per_hour": "10",
                "cpu": 4.0,
                "memory_mb": 12288,
                "gpu": 1,
                "gpu_model": "nvidia-tesla-k80",
                "tpu": {"type": "tpu", "software_version": "v1"},
                "scheduler_enabled": True,
                "preemptible_node": True,
                "resource_affinity": ["gpu-k80"],
            }
        )

        assert result == ResourcePreset(
            name="gpu-small",
            credits_per_hour=Decimal("10"),
            cpu=4.0,
            memory_mb=12288,
            gpu=1,
            gpu_model="nvidia-tesla-k80",
            tpu=TPUPreset(type="tpu", software_version="v1"),
            scheduler_enabled=True,
            preemptible_node=True,
            resource_affinity=["gpu-k80"],
        )

    def test_convert_storage(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_storage({"url": "https://storage-dev.neu.ro"})

        assert result == StorageConfig(
            url=URL("https://storage-dev.neu.ro"), volumes=[]
        )

    def test_convert_storage_with_volumes(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_storage(
            {
                "url": "https://storage-dev.neu.ro",
                "volumes": [
                    {},
                    {"path": "/volume", "size_mb": 1024},
                ],
            }
        )

        assert result == StorageConfig(
            url=URL("https://storage-dev.neu.ro"),
            volumes=[
                VolumeConfig(),
                VolumeConfig(path="/volume", size_mb=1024),
            ],
        )

    def test_convert_blob_storage(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_blob_storage(
            {"url": "https://blob-storage-dev.neu.ro"}
        )

        assert result == BlobStorageConfig(url=URL("https://blob-storage-dev.neu.ro"))

    def test_convert_registry(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_registry({"url": "https://registry-dev.neu.ro"})

        assert result == RegistryConfig(url=URL("https://registry-dev.neu.ro"))

    def test_convert_monitoring(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_monitoring({"url": "https://monitoring-dev.neu.ro"})

        assert result == MonitoringConfig(url=URL("https://monitoring-dev.neu.ro"))

    def test_convert_secrets(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_secrets({"url": "https://secrets-dev.neu.ro"})

        assert result == SecretsConfig(url=URL("https://secrets-dev.neu.ro"))

    def test_convert_metrics(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_metrics({"url": "https://metrics-dev.neu.ro"})

        assert result == MetricsConfig(url=URL("https://metrics-dev.neu.ro"))

    def test_convert_dns(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_dns(
            {
                "name": "neu.ro",
                "a_records": [{"name": "*.jobs-dev.neu.ro.", "ips": ["192.168.0.2"]}],
            }
        )

        assert result == DNSConfig(name="neu.ro", a_records=[mock.ANY])

    def test_convert_a_record_with_ips(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_a_record(
            {"name": "*.jobs-dev.neu.ro.", "ips": ["192.168.0.2"]}
        )

        assert result == ARecord(name="*.jobs-dev.neu.ro.", ips=["192.168.0.2"])

    def test_convert_a_record_dns_name(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_a_record(
            {
                "name": "*.jobs-dev.neu.ro.",
                "dns_name": "load-balancer",
                "zone_id": "/hostedzone/1",
                "evaluate_target_health": True,
            }
        )

        assert result == ARecord(
            name="*.jobs-dev.neu.ro.",
            dns_name="load-balancer",
            zone_id="/hostedzone/1",
            evaluate_target_health=True,
        )

    def test_convert_disks(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_disks(
            {"url": "https://metrics-dev.neu.ro", "storage_limit_per_user_gb": 1024}
        )

        assert result == DisksConfig(
            url=URL("https://metrics-dev.neu.ro"), storage_limit_per_user_gb=1024
        )

    def test_convert_buckets(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_buckets(
            {"url": "https://buckets-dev.neu.ro", "disable_creation": True}
        )

        assert result == BucketsConfig(
            url=URL("https://buckets-dev.neu.ro"), disable_creation=True
        )

    def test_convert_ingress(self, converter: PrimitiveToClusterConverter) -> None:
        result = converter.convert_ingress(
            {"acme_environment": "production", "cors_origins": ["https://app.neu.ro"]}
        )

        assert result == IngressConfig(
            acme_environment=ACMEEnvironment.PRODUCTION,
            cors_origins=["https://app.neu.ro"],
        )

    def test_convert_ingress_defaults(
        self, converter: PrimitiveToClusterConverter
    ) -> None:
        result = converter.convert_ingress({"acme_environment": "production"})

        assert result == IngressConfig(acme_environment=ACMEEnvironment.PRODUCTION)
