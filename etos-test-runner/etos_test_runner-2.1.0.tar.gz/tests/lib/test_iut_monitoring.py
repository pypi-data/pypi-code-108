# Copyright 2021 Axis Communications AB.
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
"""IUT monitoring test module."""
import os
import sys
import logging
import time
from pathlib import Path
from unittest import TestCase
from etos_lib.lib.config import Config
from etos_test_runner.lib.iut_monitoring import IutMonitoring

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


class TestIutMonitoring(TestCase):
    """Tests for the IUT monitoring library."""

    logger = logging.getLogger(__name__)
    script = Path.cwd().joinpath("script.sh")

    def setUp(self):
        """Create a script file."""
        script = ["#!/bin/bash", "echo Hello $1 > $(pwd)/output"]
        with open(self.script, "w", encoding="utf-8") as scriptfile:
            for line in script:
                scriptfile.write(f"{line}\n")
        self.config = Config()
        self.files = [self.script, Path.cwd().joinpath("output")]

    def tearDown(self):
        """Remove script file."""
        for script in self.files:
            self.logger.debug("Removing %r", script)
            try:
                script.unlink()
            except FileNotFoundError:
                pass
        self.config.set("scripts", [])

    def _wait_for_file(self, filename, timeout=5):
        """Wait for a file to exist.

        :param filename: Absolute path to file.
        :type filename: str
        :param timeout: Maximum time to wait for file to exist. In seconds.
        :type timeout: int
        :return: True if the file exists, False if it does not.
        :rtype: bool
        """
        end = time.time() + timeout
        while time.time() < end:
            # Sleep is done before checking if the file exists.
            # This adds 1 second to all tests that utilize this method, but
            # it will assist with race conditions when the script writes to
            # file. I.e. the file can exist, but no data in it yet.
            time.sleep(1)
            if os.path.exists(filename):
                return True
        self.logger.warning("File did not exist after %r seconds.", timeout)
        return False

    def test_start_monitoring_single_script(self):
        """Verify that the start monitoring method can execute a single script.

        Approval criteria:
            - Start monitoring shall execute a script to completion.

        Test steps::
            1. Initialize IUT monitoring.
            2. Load a script to the config.
            3. Start monitoring.
            4. Verify that the script executed.
        """
        self.logger.info("STEP: Initialize IUT monitoring.")
        iut_monitoring = IutMonitoring(None)
        iut_monitoring.interrupt_timeout = 5
        iut_monitoring.terminate_timeout = 5
        iut_monitoring.kill_timeout = 5

        self.logger.info("STEP: Load script to the config.")
        self.config.set("scripts", [{"name": str(self.script), "parameters": ["world"]}])

        self.logger.info("STEP: Start monitoring.")
        iut_monitoring.start_monitoring()

        self.logger.info("STEP: Verify that the script executed.")
        self._wait_for_file(Path.cwd().joinpath("output"))
        with open(Path.cwd().joinpath("output"), encoding="utf-8") as output:
            hello_world = output.read().strip()
            self.logger.info(hello_world)
        self.assertEqual(hello_world, "Hello world")

    def test_start_monitoring_multiple_scripts(self):
        """Verify that the start monitoring method can execute multiple scripts.

        Approval criteria:
            - Start monitoring shall execute multiple scripts to completion.

        Test steps::
            1. Initialize IUT monitoring.
            2. Load the scripts to the config.
            3. Start monitoring.
            4. Verify that the scripts executed.
        """
        self.logger.info("STEP: Initialize IUT monitoring.")
        iut_monitoring = IutMonitoring(None)
        iut_monitoring.interrupt_timeout = 5
        iut_monitoring.terminate_timeout = 5
        iut_monitoring.kill_timeout = 5

        self.logger.info("STEP: Load the scripts to the config.")
        script = ["#!/bin/bash", "echo Goodbye $1 > $(pwd)/output2"]
        second_script = Path.cwd().joinpath("second.sh")
        self.files.append(second_script)
        self.files.append(Path.cwd().joinpath("output2"))
        with open(second_script, "w", encoding="utf-8") as scriptfile:
            for line in script:
                scriptfile.write(f"{line}\n")
        self.config.set(
            "scripts",
            [
                {"name": str(self.script), "parameters": ["world"]},
                {"name": str(second_script), "parameters": ["world"]},
            ],
        )

        self.logger.info("STEP: Start monitoring.")
        iut_monitoring.start_monitoring()

        self.logger.info("STEP: Verify that the scripts executed.")
        self._wait_for_file(Path.cwd().joinpath("output"))
        with open(Path.cwd().joinpath("output"), encoding="utf-8") as output:
            hello_world = output.read().strip()
            self.logger.info(hello_world)
        self._wait_for_file(Path.cwd().joinpath("output2"))
        with open(Path.cwd().joinpath("output2"), encoding="utf-8") as output:
            goodbye_world = output.read().strip()
            self.logger.info(goodbye_world)
        self.assertEqual(hello_world, "Hello world")
        self.assertEqual(goodbye_world, "Goodbye world")

    def test_stop_monitoring_single_script(self):
        """Verify that stop monitoring a single script interrupt it.

        Approval criteria:
            - stop monitoring shall send SIGINT to process.

        Test steps::
            1. Initialize IUT monitoring.
            2. Create and add a script with an infinite loop.
            3. Start monitoring.
            4. Stop monitoring.
            5. Verify that the script was interrupted with SIGINT.
        """
        self.logger.info("STEP: Initialize IUT monitoring.")
        iut_monitoring = IutMonitoring(None)
        iut_monitoring.interrupt_timeout = 5
        iut_monitoring.terminate_timeout = 5
        iut_monitoring.kill_timeout = 5

        self.logger.info("STEP: Create and add a script with an infinite loop.")
        script = [
            "#!/bin/bash",
            "int_handler() {",
            "   echo interrupted! > $(pwd)/output",
            "   exit 0",
            "}",
            "trap int_handler INT",
            "while :",
            "do",
            "   sleep 1",
            "done",
        ]
        interrupt_script = Path.cwd().joinpath("interrupt.sh")
        self.files.append(interrupt_script)
        self.files.append(Path.cwd().joinpath("output"))
        with open(interrupt_script, "w", encoding="utf-8") as scriptfile:
            for line in script:
                scriptfile.write(f"{line}\n")
        self.config.set(
            "scripts",
            [
                {"name": str(interrupt_script)},
            ],
        )

        self.logger.info("STEP: Start monitoring.")
        iut_monitoring.start_monitoring()
        time.sleep(1)

        self.logger.info("STEP: Stop monitoring.")
        iut_monitoring.stop_monitoring()

        self.logger.info("STEP: Verify that the script was interrupted with SIGINT.")
        self.assertTrue(self._wait_for_file(Path.cwd().joinpath("output")))
        with open(Path.cwd().joinpath("output"), encoding="utf-8") as output:
            text = output.read().strip()
        self.assertEqual(text, "interrupted!")

    def test_stop_monitoring_multiple_scripts(self):
        """Verify that stop monitoring multiple scripts interrupts them.

        Approval criteria:
            - stop monitoring shall send SIGINT to all processes.

        Test steps::
            1. Initialize IUT monitoring.
            2. Create and add multiple scripts with an infinite loop.
            3. Start monitoring.
            4. Stop monitoring.
            5. Verify that the scripts were interrupted with SIGINT.
        """
        self.logger.info("STEP: Initialize IUT monitoring.")
        iut_monitoring = IutMonitoring(None)
        iut_monitoring.interrupt_timeout = 5
        iut_monitoring.terminate_timeout = 5
        iut_monitoring.kill_timeout = 5

        self.logger.info("STEP: Create and add multiple scripts with an infinite loop.")
        script = [
            "#!/bin/bash",
            "int_handler() {",
            "   echo interrupted! > $(pwd)/output",
            "   exit 0",
            "}",
            "trap int_handler INT",
            "while :",
            "do",
            "   sleep 1",
            "done",
        ]
        first_interrupt_script = Path.cwd().joinpath("first_interrupt.sh")
        self.files.append(first_interrupt_script)
        self.files.append(Path.cwd().joinpath("output"))
        with open(first_interrupt_script, "w", encoding="utf-8") as scriptfile:
            for line in script:
                scriptfile.write(f"{line}\n")
        script = [
            "#!/bin/bash",
            "int_handler() {",
            "   echo interrupted! > $(pwd)/output2",
            "   exit 0",
            "}",
            "trap int_handler INT",
            "while :",
            "do",
            "   sleep 1",
            "done",
        ]
        second_interrupt_script = Path.cwd().joinpath("second_interrupt.sh")
        self.files.append(second_interrupt_script)
        self.files.append(Path.cwd().joinpath("output2"))
        with open(second_interrupt_script, "w", encoding="utf-8") as scriptfile:
            for line in script:
                scriptfile.write(f"{line}\n")
        self.config.set(
            "scripts",
            [
                {"name": str(first_interrupt_script)},
                {"name": str(second_interrupt_script)},
            ],
        )

        self.logger.info("STEP: Start monitoring.")
        iut_monitoring.start_monitoring()
        time.sleep(1)

        self.logger.info("STEP: Stop monitoring.")
        iut_monitoring.stop_monitoring()

        self.logger.info("STEP: Verify that the scripts were interrupted with SIGINT.")
        self.assertTrue(self._wait_for_file(Path.cwd().joinpath("output")))
        self.assertTrue(self._wait_for_file(Path.cwd().joinpath("output2")))
        with open(Path.cwd().joinpath("output"), encoding="utf-8") as output:
            text = output.read().strip()
        self.assertEqual(text, "interrupted!")
        with open(Path.cwd().joinpath("output2"), encoding="utf-8") as output:
            text = output.read().strip()
        self.assertEqual(text, "interrupted!")

    def test_stop_monitoring_terminate(self):
        """Verify that stop monitoring will attempt to terminate script that does not interrupt.

        Approval criteria:
            - stop monitoring shall send SEGTERM to process if SIGINT fails.

        Test steps::
            1. Initialize IUT monitoring.
            2. Create and add a script catching SIGINT.
            3. Start monitoring.
            4. Stop monitoring.
            5. Verify that the script was interrupted with SIGTERM.
        """
        self.logger.info("STEP: Initialize IUT monitoring.")
        iut_monitoring = IutMonitoring(None)
        iut_monitoring.interrupt_timeout = 5
        iut_monitoring.terminate_timeout = 5
        iut_monitoring.kill_timeout = 5

        self.logger.info("STEP: Create and add a script catching SIGINT.")
        script = [
            "#!/bin/bash",
            "int_handler() {",
            "   echo interrupted! > $(pwd)/output",
            "}",
            "term_handler() {",
            "   echo terminated! >> $(pwd)/output",
            "   exit 0",
            "}",
            "trap int_handler INT",
            "trap term_handler TERM",
            "while :",
            "do",
            "   sleep 1",
            "done",
        ]
        interrupt_script = Path.cwd().joinpath("terminate.sh")
        self.files.append(interrupt_script)
        self.files.append(Path.cwd().joinpath("output"))
        with open(interrupt_script, "w", encoding="utf-8") as scriptfile:
            for line in script:
                scriptfile.write(f"{line}\n")
        self.config.set(
            "scripts",
            [
                {"name": str(interrupt_script)},
            ],
        )

        self.logger.info("STEP: Start monitoring.")
        iut_monitoring.start_monitoring()
        time.sleep(1)

        self.logger.info("STEP: Stop monitoring.")
        iut_monitoring.stop_monitoring()

        self.logger.info("STEP: Verify that the script was interrupted with SIGINT.")
        self.assertTrue(self._wait_for_file(Path.cwd().joinpath("output")))
        with open(Path.cwd().joinpath("output"), encoding="utf-8") as output:
            lines = output.readlines()
        interrupt = lines.pop(0).strip()
        self.assertEqual(interrupt, "interrupted!")
        terminate = lines.pop(0).strip()
        self.assertEqual(terminate, "terminated!")

    def test_stop_monitoring_kill(self):
        """Verify that stop monitoring will attempt to kill script that does not terminate.

        Approval criteria:
            - stop monitoring shall send SIGKILL to process if SIGTERM fails.

        Test steps::
            1. Initialize IUT monitoring.
            2. Create and add a script catching SIGINT and SIGTERM.
            3. Start monitoring.
            4. Stop monitoring.
            5. Verify that the script was killed.
        """
        self.logger.info("STEP: Initialize IUT monitoring.")
        iut_monitoring = IutMonitoring(None)
        iut_monitoring.interrupt_timeout = 5
        iut_monitoring.terminate_timeout = 5
        iut_monitoring.kill_timeout = 5

        self.logger.info("STEP: Create and add a script catching SIGINT and SIGTERM.")
        script = [
            "#!/bin/bash",
            "int_handler() {",
            "   echo interrupted! > $(pwd)/output",
            "}",
            "term_handler() {",
            "   echo terminated! >> $(pwd)/output",
            "}",
            "trap int_handler INT",
            "trap term_handler TERM",
            "while :",
            "do",
            "   sleep 1",
            "done",
        ]
        interrupt_script = Path.cwd().joinpath("kill.sh")
        self.files.append(interrupt_script)
        self.files.append(Path.cwd().joinpath("output"))
        with open(interrupt_script, "w", encoding="utf-8") as scriptfile:
            for line in script:
                scriptfile.write(f"{line}\n")
        self.config.set(
            "scripts",
            [
                {"name": str(interrupt_script)},
            ],
        )

        self.logger.info("STEP: Start monitoring.")
        iut_monitoring.start_monitoring()
        time.sleep(1)

        self.logger.info("STEP: Stop monitoring.")
        iut_monitoring.stop_monitoring()

        self.logger.info("STEP: Verify that the script was killed.")
        self.assertTrue(self._wait_for_file(Path.cwd().joinpath("output")))
        with open(Path.cwd().joinpath("output"), encoding="utf-8") as output:
            lines = output.readlines()
        interrupt = lines.pop(0).strip()
        self.assertEqual(interrupt, "interrupted!")
        terminate = lines.pop(0).strip()
        self.assertEqual(terminate, "terminated!")
