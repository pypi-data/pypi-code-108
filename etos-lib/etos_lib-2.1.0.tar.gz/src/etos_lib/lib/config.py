# Copyright 2020-2021 Axis Communications AB.
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
"""ETOS Library config."""
from pprint import pprint
import os


class Config:
    """ETOS configuration storage."""

    config = {
        "proxies": {
            "http": os.getenv("HTTP_PROXY_OVERRIDE"),
            "https": os.getenv("HTTPS_PROXY_OVERRIDE"),
        },
        "rabbitmq": {},
        "rabbitmq_publisher": {},
        "rabbitmq_subscriber": {},
    }

    def reset(self):
        """Reset configuration back to default."""
        self.config.clear()
        self.config["proxies"] = {
            "http": os.getenv("HTTP_PROXY_OVERRIDE"),
            "https": os.getenv("HTTPS_PROXY_OVERRIDE"),
        }
        self.config["rabbitmq"] = {}
        self.config["rabbitmq_publisher"] = {}
        self.config["rabbitmq_subscriber"] = {}

    def get(self, key):
        """Get from Config."""
        return self.config.get(key)

    def get_config_or_env(self, key):
        """Get from Config or environment. Config is prioritized.

        Note that if taken from environment, it will be stored in config
        for future use.
        """
        value = self.config.get(key)
        if value is None:
            value = os.getenv(key)
            if value is not None:
                self.config[key] = value
        return self.config.get(key)

    def set(self, key, value):
        """Set a key in configuration."""
        self.config[key] = value

    @classmethod
    def dump(cls):
        """Dump the values of the configuration."""
        pprint(cls.config)

    @property
    def rabbitmq_publisher(self):
        """Rabbitmq Publisher data."""
        return self.config.get("rabbitmq_publisher")

    @property
    def rabbitmq_subscriber(self):
        """Rabbitmq Subscriber data."""
        return self.config.get("rabbitmq_subscriber")

    def rabbitmq_from_environment(self):
        """Load RabbitMQ data from environment variables."""
        ssl = os.getenv("RABBITMQ_SSL", "true") == "true"
        data = {
            "host": os.getenv("RABBITMQ_HOST", "127.0.0.1"),
            "exchange": os.getenv("RABBITMQ_EXCHANGE", "eiffel"),
            "username": os.getenv("RABBITMQ_USERNAME", None),
            "password": os.getenv("RABBITMQ_PASSWORD", None),
            "port": int(os.getenv("RABBITMQ_PORT", "5672")),
            "vhost": os.getenv("RABBITMQ_VHOST", None),
            "ssl": ssl,
        }
        self.set("rabbitmq", data)

    def rabbitmq_subscriber_from_environment(self):
        """Load RabbitMQ subscriber data from environment variables and set in config."""
        if not self.get("rabbitmq"):
            self.rabbitmq_from_environment()
        data = {
            "queue": os.getenv("RABBITMQ_QUEUE", None),
            "routing_key": os.getenv("RABBITMQ_ROUTING_KEY", "#"),
        }
        data.update(**self.get("rabbitmq").copy())
        self.set("rabbitmq_subscriber", data)

    def rabbitmq_publisher_from_environment(self):
        """Load RabbitMQ publisher data from environment variables and set in config.

        Eiffel source is loaded from configuration file.
        """
        if not self.get("rabbitmq"):
            self.rabbitmq_from_environment()
        data = {
            "source": self.get("source"),
        }
        data.update(**self.get("rabbitmq").copy())
        self.set("rabbitmq_publisher", data)
