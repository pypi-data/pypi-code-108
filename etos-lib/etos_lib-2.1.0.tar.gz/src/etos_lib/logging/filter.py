# Copyright 2020 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ETOS filter."""
import logging


class EtosFilter(logging.Filter):  # pylint:disable=too-few-public-methods
    """Filter for adding extra application specific data to log messages."""

    def __init__(self, application, version, environment, local):
        """Initialize with a few ETOS application fields.

        :param application: Name of application.
        :type application: str
        :param version: Version of application.
        :type version: str
        :param environment: In which environment is this executing.
        :type environment: str
        :param local: Thread-local configuration information.
        :type local: :obj:`threading.local`
        """
        self.application = application
        self.version = version
        self.environment = environment
        self.local = local
        super().__init__()

    def filter(self, record):
        """Add contextual data to log record.

        :param record: Log record to add data to.
        :type record: :obj:`logging.LogRecord`
        :return: True
        :rtype: bool
        """
        record.application = self.application
        record.version = self.version
        record.environment = self.environment

        # Add each thread-local attribute to record.
        for attr in dir(self.local):
            if attr.startswith("__") and attr.endswith("__"):
                continue
            setattr(record, attr, getattr(self.local, attr))
        if not hasattr(record, "identifier"):
            record.identifier = "Unknown"

        return True
