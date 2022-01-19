from typing import Any, Callable, Dict, Iterator, List, Optional, Type, cast

import blacksmith
from blacksmith import (
    SyncClient,
    SyncClientFactory,
    SyncConsulDiscovery,
    SyncHTTPMiddleware,
    SyncRouterDiscovery,
    SyncStaticDiscovery,
)
from blacksmith.domain.model.http import HTTPTimeout
from blacksmith.domain.model.params import CollectionParser
from blacksmith.sd._sync.base import SyncAbstractServiceDiscovery
from blacksmith.service._sync.base import SyncAbstractTransport
from blacksmith.typing import Proxies, Service, Url
from pyramid.config import Configurator   # type: ignore
from pyramid.exceptions import ConfigurationError  # type: ignore
from pyramid.request import Request  # type: ignore
from pyramid.settings import asbool, aslist  # type: ignore

from pyramid_blacksmith.middleware_factory import AbstractMiddlewareFactoryBuilder

from .typing import Settings
from .utils import list_to_dict, resolve_entrypoint


class BlacksmithClientSettingsBuilder:
    def __init__(self, settings: Settings, prefix: str = "client"):
        self.settings = settings
        self.prefix = f"blacksmith.{prefix}"

    def build(self) -> SyncClientFactory[Any, Any]:
        sd = self.build_sd_strategy()
        timeout = self.get_timeout()
        proxies = self.get_proxies()
        verify = self.get_verify_certificate()
        transport = self.build_transport()
        collection_parser = self.build_collection_parser()
        ret: SyncClientFactory[Any, Any] = SyncClientFactory(
            sd,
            timeout=timeout,
            proxies=proxies,
            verify_certificate=verify,
            transport=transport,
            collection_parser=collection_parser,
        )
        for mw in self.build_middlewares():
            ret.add_middleware(mw)
        return ret

    def build_sd_static(self) -> SyncStaticDiscovery:
        key = f"{self.prefix}.static_sd_config"
        services_endpoints = list_to_dict(self.settings, key)
        services: Dict[Service, Url] = {}
        for api_v, url in services_endpoints.items():
            api, version = api_v.split("/", 1) if "/" in api_v else (api_v, None)
            services[(api or "", version)] = url
        return SyncStaticDiscovery(services)

    def build_sd_consul(self) -> SyncConsulDiscovery:
        key = f"{self.prefix}.consul_sd_config"
        kwargs = list_to_dict(self.settings, key)
        return SyncConsulDiscovery(**kwargs)  # type: ignore

    def build_sd_router(self) -> SyncRouterDiscovery:
        key = f"{self.prefix}.router_sd_config"
        kwargs = list_to_dict(self.settings, key)
        return SyncRouterDiscovery(**kwargs)

    def build_sd_strategy(self) -> SyncAbstractServiceDiscovery:
        sd_classes: Dict[str, Callable[[], SyncAbstractServiceDiscovery]] = {
            "static": self.build_sd_static,
            "consul": self.build_sd_consul,
            "router": self.build_sd_router,
        }
        key = f"{self.prefix}.service_discovery"
        sd_name = self.settings.get(key)
        if not sd_name:
            raise ConfigurationError(f"Missing setting {key}")

        if sd_name not in sd_classes:
            raise ConfigurationError(
                f"Invalid value {sd_name} for {key}: "
                f"not in {', '.join(sd_classes.keys())}"
            )

        return sd_classes[sd_name]()

    def get_timeout(self) -> HTTPTimeout:
        kwargs = {}
        for key in (
            (f"{self.prefix}.timeout", "timeout"),
            (f"{self.prefix}.connect_timeout", "connect"),
        ):
            if key[0] in self.settings:
                kwargs[key[1]] = int(self.settings[key[0]])
        return HTTPTimeout(**kwargs)

    def get_proxies(self) -> Optional[Proxies]:
        key = f"{self.prefix}.proxies"
        if key in self.settings:
            return cast(Proxies, list_to_dict(self.settings, key)) or None
        return None

    def get_verify_certificate(self) -> bool:
        return asbool(self.settings.get(f"{self.prefix}.verify_certificate", True))

    def build_transport(self) -> Optional[SyncAbstractTransport]:
        value = self.settings.get(f"{self.prefix}.transport")
        if not value:
            return None
        if isinstance(value, SyncAbstractTransport):
            return value
        cls = resolve_entrypoint(value)
        return cls()

    def build_collection_parser(self) -> Type[CollectionParser]:
        value = self.settings.get(f"{self.prefix}.collection_parser")
        if not value:
            return CollectionParser
        if isinstance(value, type) and issubclass(value, CollectionParser):
            return value  # type: ignore
        cls = resolve_entrypoint(value)
        return cls  # type: ignore

    def build_middlewares(self) -> Iterator[SyncHTTPMiddleware]:
        value = aslist(
            self.settings.get(f"{self.prefix}.middlewares", []), flatten=False
        )

        classes = {
            "prometheus": "pyramid_blacksmith.middleware:PrometheusMetricsBuilder",
            "circuitbreaker": "pyramid_blacksmith.middleware:CircuitBreakerBuilder",
            "httpcaching": "pyramid_blacksmith.middleware:HTTPCachingBuilder",
        }
        middlewares: Dict[str, SyncHTTPMiddleware] = {}
        for middleware in value:
            try:
                middleware, cls = middleware.split(maxsplit=1)
            except ValueError:
                cls = classes.get(middleware, middleware)
            cls = resolve_entrypoint(cls)
            instance = cls(
                self.settings,
                f"{self.prefix}.middleware.{middleware}",
                middlewares,
            ).build()
            yield instance
            middlewares[middleware] = instance


class BlacksmithMiddlewareFactoryBuilder:
    """
    Parse the settings like:

    ::

        blacksmith.client.middleware_factories =
            forward_header

        blacksmith.client.middleware_factory.forward_header =
            Authorization

    """

    def __init__(self, settings: Settings, prefix: str = "client"):
        self.settings = settings
        self.prefix = f"blacksmith.{prefix}"

    def build(self) -> Iterator[AbstractMiddlewareFactoryBuilder]:
        classes = {
            "forward_header": (
                "pyramid_blacksmith.middleware_factory:ForwardHeaderFactoryBuilder"
            ),
        }
        value = aslist(
            self.settings.get(f"{self.prefix}.middleware_factories", []), flatten=False
        )
        for middleware in value:
            try:
                middleware, cls = middleware.split(maxsplit=1)
            except ValueError:
                cls = classes.get(middleware, middleware)

            key = f"{self.prefix}.middleware_factory.{middleware}"
            kwargs = list_to_dict(self.settings, key, with_flag=True)
            cls = resolve_entrypoint(cls)
            yield cls(**kwargs)


class PyramidBlacksmith:
    """
    Type of the `request.blacksmith` property.

    This can be used to create a ``Protocol`` of the pyramid ``Request``
    in final application for typing purpose.

    Example:

    .. code-block::

        from pyramid_blacksmith import PyramidBlacksmith

        class RequestProtocol(Protocol):
            blacksmith: PyramidBlacksmith


        def my_view(request: RequestProtocol):
            ...

    """

    def __init__(
        self,
        request: Request,
        clients: Dict[str, SyncClientFactory[Any, Any]],
        middleware_factories: Dict[str, List[AbstractMiddlewareFactoryBuilder]],
    ):
        self.request = request
        self.clients = clients
        self.middleware_factories = middleware_factories

    def __getattr__(self, name: str) -> Callable[[str], SyncClient[Any, Any]]:
        """
        Return the blacksmith client factory named in the configuration.
        """

        def get_client(client_name: str) -> SyncClient[Any, Any]:
            try:
                client_factory = self.clients[name]
            except KeyError as k:
                raise AttributeError(f"Client {k} is not registered")

            cli = client_factory(client_name)
            for middleware_factory in self.middleware_factories.get(name, []):
                cli.add_middleware(middleware_factory(self.request))
            return cli

        return get_client


def blacksmith_binding_factory(
    config: Configurator,
) -> Callable[[Request], PyramidBlacksmith]:

    settings: Settings = config.registry.settings
    clients_key = aslist(settings.get("blacksmith.clients", ["client"]))
    clients_dict = {
        key: BlacksmithClientSettingsBuilder(settings, key).build()
        for key in clients_key
    }

    middleware_factories = {
        key: list(BlacksmithMiddlewareFactoryBuilder(settings, key).build())
        for key in clients_key
    }

    def blacksmith_binding(request: Request) -> PyramidBlacksmith:
        return PyramidBlacksmith(request, clients_dict, middleware_factories)

    return blacksmith_binding


def includeme(config: Configurator):
    """
    Expose the method consume by the Configurator while using:

    ::

        config.include('pyramid_blacksmith')


    This will inject the request property ``request.blacksmith`` like
    the pyramid view below:

    ::

        def my_view(request):

            api = request.blacksmith.client("api")
            ...

    """
    resources = aslist(config.registry.settings.get("blacksmith.scan", []))
    blacksmith.scan(*resources)

    config.add_request_method(
        callable=blacksmith_binding_factory(config),
        name="blacksmith",
        property=True,
        reify=False,
    )
