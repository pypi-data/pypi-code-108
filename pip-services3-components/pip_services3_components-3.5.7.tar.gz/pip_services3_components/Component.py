# -*- coding: utf-8 -*-
"""
    pip_services3_components.Component
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Component implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.refer import DependencyResolver, IReferences
from pip_services3_commons.refer import IReferenceable

from .count.CompositeCounters import CompositeCounters
from .log.CompositeLogger import CompositeLogger
from .trace.CompositeTracer import CompositeTracer


class Component(IConfigurable, IReferenceable):
    """
    Component class implementation.
    Abstract component that supportes configurable dependencies,
    logging and performance counters.

    ### Configuration parameters ###
        - dependencies:
            - [dependency name 1]: Dependency 1 locator (descriptor)
            - ...
            - [dependency name N]: Dependency N locator (descriptor)

    ### References ###
        - `*:counters:*:*:1.0`     (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
        - `*:logger:*:*:1.0`       (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - `\*:tracer:\*:\*:1.0`       (optional) :class:`ITracer <pip_services3_components.trace.ITracer.ITracer>` components to record traces
        - `...`                                    References must match configured dependencies.
    """

    def __init__(self):
        self._logger: CompositeLogger = CompositeLogger()
        self._counters: CompositeCounters = CompositeCounters()
        self._dependency_resolver: DependencyResolver = DependencyResolver()
        self._tracer: CompositeTracer = CompositeTracer()

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._dependency_resolver.configure(config)
        self._logger.configure(config)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._dependency_resolver.set_references(references)
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._tracer.set_references(references)
