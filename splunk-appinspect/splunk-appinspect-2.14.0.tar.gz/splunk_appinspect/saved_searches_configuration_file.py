# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk savedsearches.conf abstraction module"""
from . import configuration_file


class SavedSearchesConfigurationFile(configuration_file.ConfigurationFile):
    """Represents a [savedsearches.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Savedsearchesconf) file."""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
