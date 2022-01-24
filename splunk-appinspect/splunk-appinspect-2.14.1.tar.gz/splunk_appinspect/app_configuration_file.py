# Copyright 2019 Splunk Inc. All rights reserved.

"""Splunk app.conf abstraction module"""

from . import configuration_file


class AppConfigurationFile(configuration_file.ConfigurationFile):
    """Represents an [app.conf](http://docs.splunk.com/Documentation/Splunk/6.4.2/admin/Appconf)
    file.
    """

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
