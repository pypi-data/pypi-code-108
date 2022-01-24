# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk restmap.conf abstraction module"""

from . import configuration_file


class RestMapConfigurationFile(configuration_file.ConfigurationFile):
    """Represents a [restmap.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Restmapconf) file."""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
