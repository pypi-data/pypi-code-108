# Copyright 2020 Splunk Inc. All rights reserved.
"""Splunk connections.conf abstraction module"""

from . import configuration_file


class CollectionsConfigurationFile(configuration_file.ConfigurationFile):
    """Represents a [collections.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Collectionsconf) file."""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
