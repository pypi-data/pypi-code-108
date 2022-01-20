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
"""Workspace test module."""
import sys
import logging
from shutil import rmtree, unpack_archive
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock
from etos_test_runner.lib.workspace import Workspace

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


class TestWorkspace(TestCase):
    """Tests for the workspace library."""

    workspace = None
    logger = logging.getLogger(__name__)

    def setUp(self):
        self.items = []

    def tearDown(self):
        """Attempt to delete all created folders and files."""
        if self.workspace is not None:
            rmtree(self.workspace.workspace, ignore_errors=True)
            Path.cwd().joinpath("workspace.tar.gz").unlink(missing_ok=True)
        for item in self.items:
            if item.is_dir():
                rmtree(item)
            elif item.is_file():
                item.unlink()
        self.workspace = None

    def test_init_does_not_create(self):
        """Test that the library does not create workspace when created normally.

        Approval criteria:
            - Workspace library shall not create the workspace main directory
              when created normally.

        Test steps::
            1. Initialize the workspace library.
            2. Verify that the workspace library did not create a workspace directory.
        """
        self.logger.info("STEP: Initialize the workspace library.")
        self.workspace = Workspace(Mock())

        self.logger.info(
            "STEP: Verify that the workspace library did not create a workspace directory."
        )
        self.assertFalse(Path.cwd().joinpath("workspace").exists())

    def test_context(self):
        """Test that the library creates a workspace when launched as context.

        Approval criteria:
            - The workspace library shall create the workspace main directory when used as context
            - The workspace library shall attempt to compress the workspace directory when closed

        Test steps::
            1. Initialize the workspace library as a context manager.
            2. Verify that the workspace library created the main workspace directory.
            3. Exit the context.
            4. Verify that the workspace library compressed the main workspace directory.
        """
        self.logger.info("STEP: Initialize the workspace library as a context manager.")
        with Workspace(Mock()) as workspace:
            self.workspace = workspace
            self.logger.info(
                "STEP: Verify that the workspace library created the main workspace directory."
            )
            self.assertTrue(workspace.workspace.exists() and workspace.workspace.is_dir())

            self.logger.info("STEP: Exit the context.")
        self.logger.info(
            "STEP: Verify that the workspace library compressed the main workspace directory."
        )
        compressed_workspace = Path.cwd().joinpath("workspace.tar.gz")
        self.assertTrue(compressed_workspace.exists() and compressed_workspace.is_file())

    def test_compress(self):
        """Test that the compression method compresses a folder and all its subdirectories.

        Approval criteria:
            - The compression method shall compress a folder with gztar.

        Test steps::
            1. Create the workspace directory to be compressed.
            2. Compress the directory.
            3. Verify that the directory was compressed using the gztar format.
        """
        self.logger.info("STEP: Create the workspace directory to be compressed.")
        workspace = Workspace(Mock)
        directory = Path.cwd().joinpath("workspace")
        directory.mkdir()
        workspace.workspace = directory

        # Create a file to verify compression.
        directory.joinpath("file.txt").touch()

        test_folder = Path.cwd().joinpath("testfolder")
        test_folder.mkdir()
        self.items.append(test_folder)

        self.logger.info("STEP: Compress the directory.")
        workspace.compress()

        self.logger.info("STEP: Verify that the directory was compressed using the gztar format.")
        self.items.append(test_folder)
        compressed_workspace = Path.cwd().joinpath("workspace.tar.gz")
        unpack_archive(compressed_workspace, test_folder, format="gztar")
        compressed_file = test_folder.joinpath("workspace/file.txt")
        self.assertTrue(compressed_file.exists() and compressed_file.is_file())

    def test_compress_error_when_no_workspace_exists(self):
        """Test that the compression method raises exception when no workspace exists.

        Approval criteria:
            - The compression method shall raise exception is the workspace directory does not
              exist

        Test steps::
            1. Attempt to compress a directory that does not exist.
            2. Verify that an exception was raised.
        """
        self.logger.info("STEP: Attempt to compress a directory that does not exist.")
        self.workspace = Workspace(Mock())
        with self.assertRaises(Exception):
            self.logger.info("STEP: Verify that an exception was raised.")
            self.workspace.compress()

    def test_test_directory(self):
        """Test that the workspace library can create a test directory as a context manager.

        Approval criteria:
            - The workspace library shall create and chdir to a test directory.

        Test steps::
            1. Initialize the workspace.
            2. Enter test directory in a context manager.
            3. Verify that directory was created and changed to.
        """
        self.logger.info("STEP: Initialize the workspace.")
        with Workspace(Mock()) as workspace:
            self.workspace = workspace

            self.logger.info("STEP: Enter test directory in a context manager.")
            with workspace.test_directory("dir") as directory:
                self.logger.info("STEP: Verify that directory was created and changed to.")
                self.assertTrue(directory.exists() and directory.is_dir())
                try:
                    self.assertEqual(Path.cwd().relative_to(directory), Path("."))
                except ValueError as exception:
                    raise AssertionError("Directory is not the cwd") from exception

    def test_test_directory_identifer_exists(self):
        """Test that the workspace does not create a directory for an identifer that already exists.

        Approval criteria:
            - The workspace library shall reuse a test directory if identifier already exists.

        Test steps::
            1. Initialize the workspace.
            2. Enter a test directory in a context manager with identifier 'dir1'.
            3. Check that test directory was created and exit the context.
            4. Enter a test directory in a context manager with the same identifer.
            5. Verify that the folder was re-used.
        """
        self.logger.info("STEP: Initialize the workspace.")
        with Workspace(Mock()) as workspace:
            self.workspace = workspace

            self.logger.info(
                "STEP: Enter a test directory in a context manager with identifier 'dir1'."
            )
            with workspace.test_directory("dir1") as directory:
                self.logger.info(
                    "STEP: Check that test directory was created and exit the context."
                )
                if not directory.exists() and directory.is_dir():
                    raise Exception("Test directory was not properly created.")
                first_stat = directory.stat()

            with workspace.test_directory("dir1") as directory:
                self.logger.info(
                    "STEP: Enter a test directory in a context manager with the same identifer."
                )
                if not directory.exists() and directory.is_dir():
                    raise Exception("Test directory was not properly created.")

                self.logger.info("STEP: Verify that the folder was re-used.")
                self.assertEqual(
                    first_stat,
                    directory.stat(),
                    "Second directory is not the same as the first directory.",
                )

    def test_test_directory_function_call(self):
        """Test that the test directory method calls a method when created if supplied.

        Approval criteria:
            - The workspace library shall call method on directory creation if supplied.
            - The workspace library shall not call method if directory was not created.

        Test steps::
            1. Initialize the workspace.
            2. Enter a test directory with a method call registered.
            3. Verify that the method was called.
            4. Enter a test directory with the same identifer and a method call registered.
            5. Verify that the method was not called.
        """
        calls = []

        def callee(calls):
            """Test function for counting calls."""
            calls.append(1)

        self.logger.info("STEP: Initialize the workspace.")
        with Workspace(Mock()) as workspace:
            self.workspace = workspace

            self.logger.info("STEP: Enter a test directory with a method call registered.")
            with workspace.test_directory("dir1", callee, calls):
                self.logger.info("STEP: Verify that the method was called.")
                self.assertEqual(len(calls), 1)

            self.logger.info(
                "STEP: Enter a test directory with the same identifer and a "
                "method call registered."
            )
            with workspace.test_directory("dir1", callee, calls):
                self.logger.info("STEP: Verify that the method was not called.")
                self.assertEqual(len(calls), 1)

    def test_test_directory_no_workspace(self):
        """Test that test directory raises exception if not workspace exist.

        Approval criteria:
            - The workspace library shall raise an exception on test directory if workspace
              does not exist.

        Test steps::
            1. Enter a test directory without a workspace.
            2. Verify that an exception was raised.
        """
        self.logger.info("STEP: Enter a test directory without a workspace.")
        self.workspace = Workspace(Mock())
        self.logger.info("STEP: Verify that an exception was raised.")
        with self.assertRaises(Exception):
            with self.workspace.test_directory("dir1"):
                pass
