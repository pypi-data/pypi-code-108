# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk inputs.conf abstraction module"""

# Custom Library
from . import configuration_file


class InputsConfigurationFile(configuration_file.ConfigurationFile):
    """Represents an `inputs.conf` file from `default/inputs.conf`."""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
