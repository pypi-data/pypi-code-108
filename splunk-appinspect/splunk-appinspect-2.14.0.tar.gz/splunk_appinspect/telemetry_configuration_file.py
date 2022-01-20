# Copyright 2020 Splunk Inc. All rights reserved.
"""Splunk telemetry.conf abstraction module"""
from . import configuration_file, splunk


class TelemetryConfigurationFile(configuration_file.ConfigurationFile):
    """Represents a [telemetry.conf](https://docs.splunk.com/Documentation/Splunk/8.0.3/Admin/Telemetryconf) file."""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
        self._whitelist = splunk.telemetry_whitelist

    def check_whitelist(self, app):
        return app.id in self._whitelist
