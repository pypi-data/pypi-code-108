# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk commands.conf abstraction module"""

from . import configuration_file


class CommandsConfigurationFile(configuration_file.ConfigurationFile):
    """Represents an commands.conf file"""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
