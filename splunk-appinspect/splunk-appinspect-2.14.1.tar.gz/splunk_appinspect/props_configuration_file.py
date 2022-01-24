# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk props.conf abstraction module"""

from . import configuration_file


class PropsConfigurationFile(configuration_file.ConfigurationFile):
    """Represents a [props.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Propsconf) file."""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
