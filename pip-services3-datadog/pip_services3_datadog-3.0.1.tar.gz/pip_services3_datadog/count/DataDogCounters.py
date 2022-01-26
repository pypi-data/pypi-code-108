# -*- coding: utf-8 -*-
import socket
from typing import Optional, List, Any

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import IReferenceable, IReferences, Descriptor
from pip_services3_commons.run import IOpenable
from pip_services3_components.count import CachedCounters, Counter, CounterType
from pip_services3_components.info import ContextInfo
from pip_services3_components.log import CompositeLogger

from pip_services3_datadog.clients import DataDogMetric
from pip_services3_datadog.clients import DataDogMetricPoint
from pip_services3_datadog.clients import DataDogMetricType
from pip_services3_datadog.clients import DataDogMetricsClient


class DataDogCounters(CachedCounters, IReferenceable, IOpenable):
    """
    Performance counters that send their metrics to DataDog service.

    DataDog is a popular monitoring SaaS service. It collects logs, metrics, events
    from infrastructure and applications and analyze them in a single place.

    ### Configuration parameters ###
        - connection(s):
          - discovery_key:         (optional) a key to retrieve the connection from :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`
            - protocol:            (optional) connection protocol: http or https (default: https)
            - host:                (optional) host name or IP address (default: api.datadoghq.com)
            - port:                (optional) port number (default: 443)
            - uri:                 (optional) resource URI or connection string with all parameters in it
        - credential:
            - access_key:          DataDog client api key
        - options:
          - retries:               number of retries (default: 3)
          - connect_timeout:       connection timeout in milliseconds (default: 10 sec)
          - timeout:               invocation timeout in milliseconds (default: 10 sec)

    ### References ###
        - `*:logger:*:*:1.0`           (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - `*:counters:*:*:1.0`         (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
        - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection

    See: :class:`RestService <pip_services3_rpc.services.RestService.RestService>`,
    :class:`CommandableHttpService <pip_services3_rpc.services.CommandableHttpService.CommandableHttpService>`

    Example:

    .. code-block:: python

        counters = DataDogCounters()
        counters.configure(ConfigParams.from_tuples(
           "credential.access_key", "827349874395872349875493"
        ))

        counters.open('123')

        counters.increment("mycomponent.mymethod.calls")

        timing = counters.begin_timing("mycomponent.mymethod.exec_time")

        try:
            ...
        finally:
            timing.end_timing()

        counters.dump()

    """

    def __init__(self):
        """
        Creates a new instance of the performance counters.
        """
        super().__init__()

        self.__client: DataDogMetricsClient = DataDogMetricsClient()
        self.__logger = CompositeLogger()
        self.__opened: bool = False
        self.__source: str = None
        self.__instance: str = socket.gethostname()

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        super().configure(config)
        self.__client.configure(config)

        self.__source = config.get_as_string_with_default('source', self.__source)
        self.__instance = config.get_as_string_with_default('instance', self.__instance)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self.__logger.set_references(references)
        self.__client.set_references(references)

        context_info: ContextInfo = references.get_one_optional(
            Descriptor("pip-services", "context-info", "default", "*", "1.0"))

        if context_info is not None and self.__source is None:
            self.__source = context_info.name
        if context_info is not None and self.__instance is None:
            self.__instance = context_info.context_id

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self.__opened

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self.__opened:
            return

        self.__opened = True

        self.__client.open(correlation_id)

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        self.__opened = False

        self.__client.close(correlation_id)

    def __convert_counter(self, counter: Counter) -> Optional[List[DataDogMetric]]:
        if counter.type == CounterType.Increment:
            return [DataDogMetric(
                metric=counter.name,
                type=DataDogMetricType.Gauge,
                host=self.__instance,
                service=self.__source,
                points=[DataDogMetricPoint(time=counter.time, value=counter.count)]
            )]
        if counter.type == CounterType.LastValue:
            return [DataDogMetric(
                metric=counter.name,
                type=DataDogMetricType.Gauge,
                host=self.__instance,
                service=self.__source,
                points=[DataDogMetricPoint(time=counter.time, value=counter.last)]
            )]

        if counter.type in [CounterType.Interval, CounterType.Statistics]:
            return [
                DataDogMetric(
                    metric=counter.name + ".min",
                    type=DataDogMetricType.Gauge,
                    host=self.__instance,
                    service=self.__source,
                    points=[DataDogMetricPoint(time=counter.time, value=counter.min)]
                ),
                DataDogMetric(
                    metric=counter.name + ".average",
                    type=DataDogMetricType.Gauge,
                    host=self.__instance,
                    service=self.__source,
                    points=[DataDogMetricPoint(time=counter.time, value=counter.average)]
                ),
                DataDogMetric(
                    metric=counter.name + ".max",
                    type=DataDogMetricType.Gauge,
                    host=self.__instance,
                    service=self.__source,
                    points=[DataDogMetricPoint(time=counter.time, value=counter.max)]
                )
            ]

        return None

    def __convert_counters(self, counters: List[Counter]) -> List[DataDogMetric]:
        metrics = []

        for counter in counters:
            data = self.__convert_counter(counter)
            if data is not None and len(data) > 0:
                metrics.extend(data)

        return metrics

    def _save(self, counters: List[Counter]) -> Any:
        """
        Saves the current counters measurements.

        :param counters: current counters measurements to be saves.
        """
        metrics = self.__convert_counters(counters)
        if len(metrics) == 0:
            return
        try:
            return self.__client.send_metrics('datadog-counters', metrics)
        except Exception as err:
            self.__logger.error('datadog-counters', err, 'Failed to push metrics to DataDog')
