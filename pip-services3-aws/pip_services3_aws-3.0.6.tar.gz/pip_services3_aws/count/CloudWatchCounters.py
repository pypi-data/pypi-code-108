# -*- coding: utf-8 -*-
import datetime
from typing import Any, Optional, List

from boto3 import client
from botocore.config import Config
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import IReferenceable, IReferences, Descriptor
from pip_services3_commons.run import IOpenable
from pip_services3_components.count import CachedCounters, Counter, CounterType
from pip_services3_components.info import ContextInfo
from pip_services3_components.log import CompositeLogger

from pip_services3_aws.connect import AwsConnectionParams
from pip_services3_aws.connect import AwsConnectionResolver
from .CloudWatchUnit import CloudWatchUnit


class CloudWatchCounters(CachedCounters, IReferenceable, IOpenable):
    """
    Performance counters that periodically dumps counters to AWS Cloud Watch Metrics.

    ### Configuration parameters ###

        - connections:
            - discovery_key:               (optional) a key to retrieve the connection from :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`
            - region:                      (optional) AWS region
        - credentials:
            - store_key:                   (optional) a key to retrieve the credentials from :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>`
            - access_id:             AWS access/client id
            - access_key:            AWS access/client id
        - options:
            - interval:              interval in milliseconds to save current counters measurements (default: 5 mins)
            - reset_timeout:         timeout in milliseconds to reset the counters. 0 disables the reset (default: 0)

    ### References ###
        - `*:context-info:*:*:1.0`      (optional) :class:`ContextInfo <pip_services3_components.info.ContextInfo.ContextInfo>` to detect the context id and specify counters source
        - `*:discovery:*:*:1.0`         (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection
        - `*:credential-store:*:*:1.0`  (optional) Credential stores to resolve credentials

    See :class:`Counter <pip_services3_components.count.Counter.Counter>`,
    :class:`CachedCounters <pip_services3_components.count.CachedCounters.CachedCounters>`,
    :class:`CompositeLogger <pip_services3_components.log.CompositeLogger.CompositeLogger>`

    Example:

    .. code-block:: python

        counters = CloudWatchCounters()
        counters.config(ConfigParams.from_tuples(
            "connection.region", "us-east-1",
            "connection.access_id", "XXXXXXXXXXX",
            "connection.access_key", "XXXXXXXXXXX"
        ))
        
        counters.set_references(References.from_tuples(
            Descriptor("pip-services", "logger", "console", "default", "1.0"),
            ConsoleLogger()
        ))

        counters.open("123")

        counters.increment("mycomponent.mymethod.calls")
        timing = counters.begin_timing("mycomponent.mymethod.exec_time")

        try:
            ...
        except Exception as e
            timing.end_timing(e)


        counters.dump();
    """

    def __init__(self):
        """
        Creates a new instance of this counters.
        """
        super().__init__()

        self.__logger: CompositeLogger = CompositeLogger()
        self.__connection_resolver: AwsConnectionResolver = AwsConnectionResolver()
        self.__connection: AwsConnectionParams = None
        self.__connect_timeout: int = 30000
        self.__client: Any = None

        self.__source: str = None
        self.__instance: str = None
        self.__opened: bool = False

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        super().configure(config)
        self.__connection_resolver.configure(config)

        self.__source = config.get_as_integer_with_default('source', self.__source)
        self.__instance = config.get_as_integer_with_default('instance', self.__instance)
        self.__connect_timeout = config.get_as_integer_with_default('options.connect_timeout', self.__connect_timeout)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.

        See :class:`IReferences <pip_services3_commons.refer.IReferences.IReferences>`
        """
        self.__logger.set_references(references)
        self.__connection_resolver.set_references(references)

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
        self.__connection = self.__connection_resolver.resolve(correlation_id)

        config = Config(connect_timeout=round(self.__connect_timeout / 1000))
        self.__client = client('cloudwatch',  # 's3'
                               aws_access_key_id=self.__connection.get_access_id(),
                               aws_secret_access_key=self.__connection.get_access_key(),
                               region_name=self.__connection.get_region(),
                               api_version='2010-08-01',
                               config=config)

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        self.__opened = False
        self.__client = None

    def __get_counter_data(self, counter: Counter, now: datetime.datetime, dimensions: List[Any]) -> Any:
        value = {
            'MetricName': counter.name,
            'Dimensions': dimensions,
            'Unit': CloudWatchUnit.Nothing,
        }

        if counter.time:
            value['Timestamp'] = counter.time

        if counter.type == CounterType.Increment:
            value['Value'] = counter.count
            value['Unit'] = CloudWatchUnit.Count
        elif counter.type == CounterType.Interval:
            value['Unit'] = CloudWatchUnit.Milliseconds
            value['StatisticValues'] = {
                'SampleCount': counter.count,
                'Maximum': counter.max,
                'Minimum': counter.min,
                'Sum': counter.count * counter.average
            }
        elif counter.type == CounterType.Statistics:
            value['StatisticValues'] = {
                'SampleCount': counter.count,
                'Maximum': counter.max,
                'Minimum': counter.min,
                'Sum': counter.count * counter.average
            }
        elif counter.type == CounterType.LastValue:
            value['Value'] = counter.last
        elif counter.type == CounterType.Timestamp:
            value['Value'] = round(counter.time.timestamp() * 1000.0)

        return value

    def _save(self, counters: List[Counter]):
        """
        Saves the current counters measurements.

        :param counters: current counters measurements to be saves.
        """
        if self.__client is None:
            return

        dimensions = [{
            'Name': "InstanceID",
            'Value': self.__instance
        }]

        now = datetime.datetime.now()

        data = []

        for counter in counters:
            data.append(self.__get_counter_data(counter, now, dimensions))
            if len(data) >= 20:
                self.__put_metrics_data({
                    'MetricData': data,
                    'Namespace': self.__source
                })
                data = []

        if len(data) > 0:
            self.__put_metrics_data({
                'MetricData': data,
                'Namespace': self.__source
            })

    def __put_metrics_data(self, params: dict):
        try:
            self.__client.put_metric_data(**params)
        except Exception as e:
            if self.__logger:
                self.__logger.error("cloudwatch_counters", e, "putMetricData error")
            raise e
