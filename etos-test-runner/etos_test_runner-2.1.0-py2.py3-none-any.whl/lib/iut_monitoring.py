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
"""IUT monitoring module."""
import sys
import os
import stat
import logging
from threading import Thread
from signal import SIGINT
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
from etos_lib.lib.config import Config


ON_POSIX = "posix" in sys.builtin_module_names


class IutMonitoring:
    """Helper class for monitoring IuT health statistics."""

    logger = logging.getLogger("IUT Monitoring")
    interrupt_timeout = 60  # Seconds
    terminate_timeout = 30  # Seconds
    kill_timeout = 30  # Seconds
    monitoring = False

    def __init__(self, iut):
        """Initialize monitoring.

        :param iut: IUT object to monitor.
        :type iut: :obj:`etr.lib.iut.Iut`
        """
        self.iut = iut
        self.processes = []
        self.config = Config()

    def _read_from_process(self, output):
        """Non-blocking read from a process output.

        :param output: Output to read from.
        :type output: filedescriptor
        """
        self.logger.info("Reading output from %r", output)
        for line in iter(output.readline, b""):
            self.logger.info(line.decode("utf-8"))
        output.close()

    def start_monitoring(self):
        """Start monitoring IUT."""
        if self.monitoring is True:
            self.logger.info("Monitoring is already started.")
            return
        scripts = self.config.get("scripts") or []
        for script in scripts:
            self.logger.info(
                "Starting script %r with parameters %r.",
                script.get("name"),
                script.get("parameters"),
            )

            # Make file executable.
            filestat = os.stat(script.get("name"))
            os.chmod(script.get("name"), filestat.st_mode | stat.S_IEXEC)

            # These processes are closed elsewhere. pylint:disable=consider-using-with
            process = Popen(
                [script.get("name"), *script.get("parameters", [])],
                stdout=PIPE,
                stderr=STDOUT,
                close_fds=ON_POSIX,
            )
            self.processes.append(process)
            Thread(target=self._read_from_process, daemon=True, args=(process.stdout,)).start()
        self.monitoring = True

    def stop_monitoring(self):
        """Stop monitoring IUT."""
        if self.monitoring is False:
            self.logger.info("Monitoring is already stopped.")
            return
        self.monitoring = False
        for process in self.processes:
            self.logger.info(
                "Interrupting process: %r (%rs timeout)",
                self.interrupt_timeout,
                process,
            )
            process.send_signal(SIGINT)
            try:
                try:
                    process.communicate(timeout=self.interrupt_timeout)
                except TimeoutExpired:
                    self.logger.error(
                        "Unable to stop with SIGINT, terminating with SIGTERM (%rs timeout)",
                        self.terminate_timeout,
                    )
                    process.terminate()
                    try:
                        process.communicate(timeout=self.terminate_timeout)
                    except TimeoutExpired:
                        self.logger.error(
                            "Unable to stop with SIGTERM, killing with SIGKILL (%rs timeout).",
                            self.kill_timeout,
                        )
                        process.kill()
                        try:
                            process.communicate(timeout=self.kill_timeout)
                        except TimeoutExpired:
                            self.logger.error(
                                "Still unable to kill it. Return and have python clean up."
                            )
            except OSError as exception:
                self.logger.error("OS Error %r. Exiting.", exception)
