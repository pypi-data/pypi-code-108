import abc
from typing import Any, Dict

from blacksmith import (
    SyncCircuitBreaker,
    SyncHTTPCachingMiddleware,
    SyncPrometheusMetrics,
)
from blacksmith.middleware._sync.base import SyncHTTPMiddleware
from pyramid.exceptions import ConfigurationError  # type: ignore
from pyramid.settings import aslist  # type: ignore

from pyramid_blacksmith.typing import Settings

from .utils import list_to_dict, resolve_entrypoint


class AbstractMiddlewareBuilder(abc.ABC):
    def __init__(
        self,
        settings: Settings,
        prefix: str,
        middlewares: Dict[str, SyncHTTPMiddleware],
    ):
        self.settings = settings
        self.prefix = prefix
        self.middlewares = middlewares

    @abc.abstractmethod
    def build(self) -> SyncHTTPMiddleware:
        """Build the Middleware"""


class PrometheusMetricsBuilder(AbstractMiddlewareBuilder):
    def build(self) -> SyncPrometheusMetrics:
        buckets = None
        settings = list_to_dict(self.settings, self.prefix)
        buckets_val = settings.get("buckets")
        if buckets_val:
            buckets = [float(val) for val in aslist(buckets_val)]

        registry_instance = settings.get("registry", "prometheus_client:REGISTRY")
        registry = resolve_entrypoint(registry_instance)
        return SyncPrometheusMetrics(buckets, registry=registry)  # type: ignore


class CircuitBreakerBuilder(AbstractMiddlewareBuilder):
    def build(self) -> SyncCircuitBreaker:
        settings = list_to_dict(self.settings, self.prefix)
        kwargs: Dict[str, Any] = {}
        for key in ("threshold", "ttl"):
            if key in settings:
                kwargs[key] = int(settings[key])

        uow = settings.get("uow", "purgatory:SyncInMemoryUnitOfWork")
        uow_cls = resolve_entrypoint(uow)
        uow_kwargs = list_to_dict(self.settings, f"{self.prefix}.uow")
        kwargs["uow"] = uow_cls(**uow_kwargs)
        if "prometheus" in self.middlewares:
            kwargs["prometheus_metrics"] = self.middlewares["prometheus"]
        return SyncCircuitBreaker(**kwargs)  # type: ignore


class HTTPCachingBuilder(AbstractMiddlewareBuilder):
    def build(self) -> SyncHTTPCachingMiddleware:
        import redis  # noqa

        settings = list_to_dict(self.settings, self.prefix)
        kwargs = {}

        mod = "blacksmith.middleware._sync.http_caching"
        redis_url = settings.get("redis")
        if not redis_url:
            raise ConfigurationError(f"Missing sub-key redis in setting {self.prefix}")
        kwargs["cache"] = redis.from_url(redis_url)

        policy_key = settings.get("policy", f"{mod}:CacheControlPolicy")
        policy_params = list_to_dict(self.settings, f"{self.prefix}.policy")
        policy_cls = resolve_entrypoint(policy_key)
        kwargs["policy"] = policy_cls(**policy_params)  # type: ignore

        srlz_key = settings.get("serializer", "json")
        kwargs["serializer"] = resolve_entrypoint(srlz_key)  # type: ignore
        return SyncHTTPCachingMiddleware(**kwargs)  # type: ignore
