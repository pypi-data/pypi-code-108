# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk distsearch.conf abstraction module"""
import logging
import os
import re

from . import configuration_file

logger = logging.getLogger(__name__)


class DistsearchConfigurationFile(configuration_file.ConfigurationFile):
    """Represents an [distsearch.conf](https://docs.splunk.com/Documentation/Splunk/7.2.0/Admin/Distsearchconf)
    file.
    """

    def __init__(self, app):
        self.app = app
        configuration_file.ConfigurationFile.__init__(self)

    def get_replication_blacklist_files(self):
        blacklist_files = set()
        if not self.has_section("replicationBlacklist"):
            return list(blacklist_files)

        regexes = []
        section = self.get_section("replicationBlacklist")
        for _, regex in section.options.items():
            regexes.append(regex.value)

        for directory, filename, _ in self.app.iterate_files():
            file_path = os.path.join(directory, filename)
            regex_file_path = os.path.join(
                "apps", self.app.package.origin_package_name, file_path
            )

            for regex in regexes:
                try:
                    if re.match(rf"{regex}", regex_file_path):
                        blacklist_files.add(file_path)
                except re.error as ex:
                    logger.warning(f"error={ex}")
                    continue

        return list(blacklist_files)
