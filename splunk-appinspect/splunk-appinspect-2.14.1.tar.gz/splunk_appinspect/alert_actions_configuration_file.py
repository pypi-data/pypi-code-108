# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk alert_actions.conf abstraction module"""

from . import configuration_file


class AlertActionsConfigurationFile(configuration_file.ConfigurationFile):
    """Represents an alert_actions.conf file"""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
