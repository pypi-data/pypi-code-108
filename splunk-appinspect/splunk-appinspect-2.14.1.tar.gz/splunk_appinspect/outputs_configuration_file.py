# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk outputs.conf abstraction module"""

# Custom Library
from . import configuration_file


class OutputsConfigurationFile(configuration_file.ConfigurationFile):
    """Represents an `outputs.conf` file."""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
