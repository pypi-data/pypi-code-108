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
"""ETOS Library exceptions."""


class ETOSException(Exception):
    """Base ETOS library exception."""


class SubscriberConfigurationMissing(ETOSException):
    """Exception for when SubscriberConfiguration is missing."""

    def __init__(self):
        """Initialize with base exception message."""
        super().__init__("Missing rabbitmq_subscriber in ETOS config.")


class PublisherConfigurationMissing(ETOSException):
    """Exception for when PublisherConfiguration is missing."""

    def __init__(self):
        """Initialize with base exception message."""
        super().__init__("Missing rabbitmq_publisher in ETOS config.")


class PublisherNotStarted(ETOSException):
    """Exception for when Publisher has not started yet."""

    def __init__(self):
        """Initialize with base exception message."""
        super().__init__("RabbitMQ publisher is not started.")


class SubscriberNotStarted(ETOSException):
    """Exception for when Subscriber has not started yet."""

    def __init__(self):
        """Initialize with base exception message."""
        super().__init__("RabbitMQ subscriber is not started.")


class PublisherDied(ETOSException):
    """Published has died."""

    def __init__(self):
        """Initialize with base exception message."""
        super().__init__("RabbitMQ publisher has died.")


class SubscriberDied(ETOSException):
    """Subscriber has died."""

    def __init__(self):
        """Initialize with base exception message."""
        super().__init__("RabbitMQ subscriber has died.")


class AliveMessageMissing(ETOSException):
    """Exception for when Alive mssage is missing."""

    def __init__(self):
        """Initialize with base exception message."""
        super().__init__("Alive message cannot be None if 'with_announcement' is True")
