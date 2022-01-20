# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk workflow_action.conf abstraction module"""
from . import configuration_file


class WorkflowActionsConfigurationFile(configuration_file.ConfigurationFile):
    """Represents a [workflow_action.conf](https://docs.splunk.com/Documentation/Splunk/8.0.0/Admin/Workflow_actionsconf) file."""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
