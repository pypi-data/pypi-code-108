#!/usr/bin/env python
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
# -*- coding: utf-8 -*-
"""ETOS test runner module."""
import argparse
import sys
import logging
import os
import signal
from pprint import pprint

from etos_lib import ETOS

from etos_test_runner import __version__
from etos_test_runner.lib.testrunner import TestRunner
from etos_test_runner.lib.iut import Iut


# Remove spam from pika.
logging.getLogger("pika").setLevel(logging.WARNING)

_LOGGER = logging.getLogger(__name__)
LOGFORMAT = "[%(asctime)s] %(levelname)s:%(message)s"
logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format=LOGFORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def parse_args(args):
    """Parse command line parameters.

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`airgparse.Namespace`
    """
    parser = argparse.ArgumentParser(description="ETOS test runner")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"etos_test_runner {__version__}",
    )
    return parser.parse_args(args)


class ETR:
    """ETOS Test Runner."""

    context = None

    def __init__(self):
        """Initialize ETOS library and start eiffel publisher."""
        self.etos = ETOS("ETOS Test Runner", os.getenv("HOSTNAME"), "ETOS Test Runner")
        self.etos.config.rabbitmq_publisher_from_environment()
        # ETR will print the entire environment just before executing.
        # Hide the password.
        os.environ["RABBITMQ_PASSWORD"] = "*********"

        self.etos.start_publisher()
        self.tests_url = os.getenv("SUB_SUITE_URL")

        signal.signal(signal.SIGTERM, self.graceful_shutdown)

    @staticmethod
    def graceful_shutdown(*args):
        """Catch sigterm."""
        raise Exception("ETR has been terminated.")

    def download_and_load(self):
        """Download and load test json."""
        generator = self.etos.http.wait_for_request(self.tests_url)
        for response in generator:
            json_config = response
            break
        self.etos.config.set("test_config", json_config)
        self.etos.config.set("context", json_config.get("context"))
        self.etos.config.set("artifact", json_config.get("artifact"))

    def _run_tests(self):
        """Run tests in ETOS test runner.

        :return: Results of test runner execution.
        :rtype: bool
        """
        iut = Iut(self.etos.config.get("test_config").get("iut"))
        test_runner = TestRunner(iut, self.etos)
        return test_runner.execute()

    def run_etr(self):
        """Send activity events and run ETR.

        :return: Result of testrunner execution.
        :rtype: bool
        """
        _LOGGER.info("Starting ETR.")
        self.download_and_load()
        try:
            activity_name = self.etos.config.get("test_config").get("name")
            triggered = self.etos.events.send_activity_triggered(activity_name)
            self.etos.events.send_activity_started(triggered)
            result = self._run_tests()
        except Exception as exc:  # pylint:disable=broad-except
            self.etos.events.send_activity_finished(
                triggered, {"conclusion": "FAILED", "description": str(exc)}
            )
            raise
        self.etos.events.send_activity_finished(triggered, {"conclusion": "SUCCESSFUL"})
        _LOGGER.info("ETR finished.")
        return result


def main(args):
    """Start ETR."""
    args = parse_args(args)

    etr = ETR()
    result = etr.run_etr()
    if isinstance(result, dict):
        pprint(result)
    _LOGGER.info("Done. Exiting")
    _LOGGER.info(result)
    sys.exit(result)


def run():
    """Entry point to ETR."""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
