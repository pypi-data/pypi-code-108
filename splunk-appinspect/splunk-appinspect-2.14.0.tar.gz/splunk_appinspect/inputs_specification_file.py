# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk input.conf.spec abstraction module"""

# Custom Library
from . import configuration_file


class InputsSpecification(configuration_file.ConfigurationFile):
    """Represents an input.conf.spec file from Readme/input.conf.spec."""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
