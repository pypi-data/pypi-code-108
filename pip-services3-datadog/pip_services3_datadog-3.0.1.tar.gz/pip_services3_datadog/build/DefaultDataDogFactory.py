# -*- coding: utf-8 -*-
from pip_services3_commons.refer import Descriptor
from pip_services3_components.build import Factory

from pip_services3_datadog.count.DataDogCounters import DataDogCounters
from pip_services3_datadog.log.DataDogLogger import DataDogLogger


class DefaultDataDogFactory(Factory):
    """
    Creates DataDog components by their descriptors.
    """

    __DataDogLoggerDescriptor = Descriptor("pip-services", "logger", "datadog", "*", "1.0")
    __DataDogCountersDescriptor = Descriptor("pip-services", "counters", "datadog", "*", "1.0")

    def __init__(self):
        """
        Create a new instance of the factory.
        """
        super().__init__()

        self.register_as_type(self.__DataDogLoggerDescriptor, DataDogLogger)
        self.register_as_type(self.__DataDogCountersDescriptor, DataDogCounters)
