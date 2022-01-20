# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk authorize.conf abstraction module"""

from . import configuration_file


class AuthorizeConfigurationFile(configuration_file.ConfigurationFile):
    """Represents an authorize.conf file"""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
