# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk transforms.conf abstraction module"""
import logging
import os

from . import configuration_file

logger = logging.getLogger(__name__)


class TransformsConfigurationFile(configuration_file.ConfigurationFile):
    """Represents a [transforms.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Transformsconf) file."""

    def __init__(self, app):
        configuration_file.ConfigurationFile.__init__(self)
        self.app = app

    @property
    def exists_configuration_file(self):
        return self.app.file_exists("default", "transforms.conf")

    def get_external_commands(self):
        external_commands = set()
        for section in self.sections():
            if section.has_option("external_cmd"):
                external_commands.add(section.get_option("external_cmd").value)
        return list(external_commands)

    def get_external_executable_file_name(self):
        executable_files = []
        for external_command in self.get_external_commands():
            executable_files.append(external_command.strip().split(" ")[0])
        return executable_files

    def get_external_executable_file_path_list(self):
        # The first argument is expected to be a python script (or executable file)
        # located in $SPLUNK_HOME/etc/apps/<app_name>/bin (or ../etc/searchscripts).
        files = []
        for file_name in self.get_external_executable_file_name():
            relative_path = os.path.join("bin", file_name)
            if self.app.file_exists(relative_path):
                files.append(relative_path)

            relative_path = os.path.join("etc/searchscripts", file_name)
            if self.app.file_exists(relative_path):
                files.append(relative_path)

        return files
