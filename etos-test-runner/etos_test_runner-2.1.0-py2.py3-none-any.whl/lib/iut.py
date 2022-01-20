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
"""IUT data structure module."""
import os
import logging
from pathlib import Path
from collections import OrderedDict
from packageurl import PackageURL
from jsontas.jsontas import JsonTas
from etos_lib.lib.config import Config


class Iut:  # pylint: disable=too-few-public-methods
    """Data object for IUTs."""

    logger = logging.getLogger(__name__)

    def __init__(self, product):
        """Initialize.

        :param product: Dictionary to set attributes from.
                        Should be the response from pool plugin list.
        :type product: dict
        """
        self.test_runner = {}
        self.config = Config()
        self.config.set("scripts", [])
        self.steps = {"environment": self.load_environment, "commands": self.commands}

        product["identity"] = PackageURL.from_string(product["identity"])
        for key, value in product.items():
            setattr(self, key, value)
        self._product_dict = product
        self.jsontas = JsonTas()
        self.jsontas.dataset.add("iut", self._product_dict)
        self.prepare()

    def prepare(self):
        """Prepare IUT for testing."""
        self.logger.info("Preparing IUT %r", self)
        for step, definition in self.test_runner.get("steps", {}).items():
            step_method = self.steps.get(step)
            if step_method is None:
                self.logger.error("Step %r does not exist. Available %r", step, self.steps)
                continue
            self.logger.info("Executing step %r", step)
            self.logger.info("Definition: %r", definition)
            if isinstance(definition, list):
                for sub_definition in definition:
                    sub_definition = OrderedDict(**sub_definition)
                    step_result = self.jsontas.run(json_data=sub_definition)
                    step_method(step_result)
            else:
                definition = OrderedDict(**definition)
                step_result = self.jsontas.run(json_data=definition)
                step_method(step_result)

    @staticmethod
    def load_environment(environment):
        """Load and set environment variables from IUT definition.

        :param environment: Environment variables to set.
        :type environment: dict
        """
        for key, value in environment.items():
            os.environ[key] = value

    def commands(self, command):
        """Create scripts from commands and add them to IUT monitoring.

        :param command: A command dictionary to prepare.
        :type command: dict
        """
        script_name = str(Path.cwd().joinpath(command.get("name")))
        parameters = command.get("parameters", [])
        with open(script_name, "w", encoding="utf-8") as script:
            for line in command.get("script"):
                script.write(f"{line}\n")
        self.config.get("scripts").append({"name": script_name, "parameters": parameters})

    @property
    def as_dict(self):
        """Return IUT as a dictionary."""
        return self._product_dict

    def __repr__(self):
        """Represent IUT as string."""
        try:
            return self._product_dict.get("identity").to_string()
        except:  # noqa pylint:disable=bare-except
            return "Unknown"
