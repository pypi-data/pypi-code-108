# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk visualizations.conf abstraction module"""
from . import configuration_file


class VisualizationsConfigurationFile(configuration_file.ConfigurationFile):
    """Represents a visualizations.conf file"""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
