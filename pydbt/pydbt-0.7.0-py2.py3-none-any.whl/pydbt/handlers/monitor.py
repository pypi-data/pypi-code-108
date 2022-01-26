from ..logger import GLOBAL_LOGGER as log
from .monitors.ddatadog import DatadogMonitor
from .monitors.prometheus import PrometheusMonitor
from .monitors.dummy import DummyMonitor
from ..config import DATADOG_HOST, DATADOG_PORT, PUSHGATEWAY_HOST, PUSHGATEWAY_PORT

# Monitor factory


def init(**kwargs):
    if DATADOG_HOST and DATADOG_PORT:
        log.info('Using datadog monitor.')
        monitor = DatadogMonitor(
            host=DATADOG_HOST,
            port=DATADOG_PORT,
            **kwargs
        )
        monitor.initialize()
        return monitor
    elif PUSHGATEWAY_PORT and PUSHGATEWAY_HOST:
        log.info('Using prometheus monitor.')
        monitor = PrometheusMonitor(
            host=PUSHGATEWAY_HOST,
            port=PUSHGATEWAY_PORT,
            **kwargs
        )
        monitor.initialize()
        return monitor
    else:
        log.info('Instrumentation is not enabled.')
        return DummyMonitor()
