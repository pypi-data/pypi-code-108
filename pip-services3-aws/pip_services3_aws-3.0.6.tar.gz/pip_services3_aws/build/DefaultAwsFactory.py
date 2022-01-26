# -*- coding: utf-8 -*-
from pip_services3_commons.refer import Descriptor
from pip_services3_components.build import Factory

from pip_services3_aws.count import CloudWatchCounters
from pip_services3_aws.log import CloudWatchLogger


class DefaultAwsFactory(Factory):
    """
    Creates AWS components by their descriptors.

    See :class:`CloudWatchLogger <pip_services3_aws.log.CloudWatchLogger.CloudWatchLogger>`,
    :class:`CloudWatchCounters <pip_services3_aws.count.CloudWatchCounters.CloudWatchCounters>`
    """

    DescriptorFactory = Descriptor("pip-services", "factory", "aws", "default", "1.0")
    CloudWatchLoggerDescriptor = Descriptor("pip-services", "logger", "cloudwatch", "*", "1.0")
    CloudWatchCountersDescriptor = Descriptor("pip-services", "counters", "cloudwatch", "*", "1.0")

    def __init__(self):
        super().__init__()

        self.register_as_type(DefaultAwsFactory.CloudWatchLoggerDescriptor, CloudWatchLogger)
        self.register_as_type(DefaultAwsFactory.CloudWatchCountersDescriptor, CloudWatchCounters)
