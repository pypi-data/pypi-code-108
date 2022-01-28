from prometheus_client import \
    CollectorRegistry, Counter, Gauge, Summary, \
    push_to_gateway, write_to_textfile, start_http_server, exposition
from singleton_decorator import singleton


@singleton
class Prometheus:
    registry = None  # type: CollectorRegistry
    gauge_instances = {}

    def __init__(self):
        self.registry = CollectorRegistry()

    def get_registry(self) -> CollectorRegistry:
        return self.registry

    def start_server(self, **kwargs) -> None:
        port = 4000 if not 'port' in kwargs else kwargs['port']

        start_http_server(port=port, registry=self.registry)

    def counter(self, name: str, documentation: str) -> Counter:
        return Counter(name, documentation, registry=self.registry)

    def gauge(self, **kwargs) -> Gauge:
        r"""
            :Keyword Arguments:
                * *new* (``boolean``) --
                  Return force new object
                * *name* (``str``) --
                  Name of Gauge
                * *documentation* (``str``) --
                  Documentation of Gauge
            """
        if 'new' in kwargs:
            return Gauge(kwargs['name'], kwargs['documentation'], registry=self.registry)

        if kwargs['name'] not in self.gauge_instances:
            self.gauge_instances[kwargs['name']] = Gauge(kwargs['name'], kwargs['documentation'],
                                                         registry=self.registry)

        return self.gauge_instances[kwargs['name']]

    def summary(self, name: str, documentation: str) -> Summary:
        return Summary(name, documentation, registry=self.registry)

    def push_to_gateway(self, gateway: str, job: str) -> None:
        push_to_gateway(gateway=gateway, job=job, registry=self.registry)

    def write_to_textfile(self, file: str) -> None:
        write_to_textfile(file, self.registry)

    def get_output(self) -> str:
        return exposition.generate_latest(self.get_registry())
