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
"""ETOS Library utilities."""
import os
import sys
import time
import signal
import logging
import subprocess
import traceback
from contextlib import contextmanager
from .debug import Debug

# pylint:disable=redefined-outer-name


class SubprocessReadTimeout(Exception):
    """Timeout on reading from subprocess."""


class Utils:
    """ETOS utility methods."""

    logger = logging.getLogger("Utils")

    def __init__(self):
        """Initialize debug instance."""
        self.debug = Debug()

    def wait(self, method, timeout=None, interval=5, **kwargs):
        """Iterate over result from method call.

        :param method: Method to call.
        :type method: :meth:
        :param timeout: How long, in seconds, to iterate.
        :type timeout: int or None
        :param interval: How long, in seconds, to wait between method calls.
        :type interval: int
        :param kwargs: Keyword arguments to pass to method call.
        :type kwargs: dict
        """
        if timeout is None:
            timeout = self.debug.default_wait_timeout
        end = time.time() + timeout
        while time.time() < end:
            try:
                yield method(**kwargs)
            except Exception as exception:  # pylint:disable=broad-except
                if isinstance(exception, GeneratorExit):
                    break
                traceback.print_exc()
                self.logger.info("Retrying..")
            time.sleep(interval)

    def search(self, dictionary, *keys):
        """Recursively search for keys in a nested dictionary.

        :param dictionary: Dictionary to search in.
        :type dictionary: dict
        :param keys: Keys to search for.
        :type keys: list
        :return: key and value matching the search.
        :rtype: tuple
        """
        for key, value in dictionary.items():
            if key in keys:
                yield key, value
            if isinstance(value, dict):
                for key, value in self.search(value, *keys):
                    yield key, value
            elif isinstance(value, (list, tuple)):
                for item in value:
                    if isinstance(item, dict):
                        for key, value in self.search(item, *keys):
                            yield key, value

    def search_and_replace(self, dictionary, replace_with, *keys):
        """Recursively search for keys in a nested dictionary and replace them.

        :param dictionary: Dictionary to search in.
        :type dictionary: dict
        :param replace_with: Value to replace key with.
        :type replace_with: *
        :param keys: Keys to search for.
        :type keys: list
        """
        for key, value in dictionary.items():
            if key in keys:
                dictionary[key] = replace_with
            if isinstance(value, dict):
                self.search_and_replace(value, replace_with, *keys)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    if isinstance(item, dict):
                        self.search_and_replace(item, replace_with, *keys)

    @contextmanager
    def chdir(self, path):
        """Change directory to path. Create path if it does not exist.

        Moves back to the previous path after exiting the context.

        Example:
            >>> with chdir("/home/test"):
            >>>     print(os.getcwd())
            /home/test

        :param path: Which path to change dir to.
        :type path: str
        """
        old_path = os.getcwd()

        self.logger.debug("Moving to directory: %s", path)

        if not os.path.isdir(path):
            self.logger.debug("Directory does not exist. Creating.")
            os.makedirs(path)

        os.chdir(path)
        yield

        self.logger.debug("Returning to: %s", old_path)
        os.chdir(old_path)

    @contextmanager
    def no_proxy(self, env=None):
        """Remove proxy from environment and reset it after.

        Example:
            >>> with no_proxy():
            >>>     print(os.environ.get("http_proxy"))
            >>>     print(os.environ.get("https_proxy"))
            >>>     print(os.environ.get("HTTP_PROXY"))
            >>>     print(os.environ.get("HTTPS_PROXY"))
            >>> print(os.environ.get("http_proxy"))
            None
            None
            None
            None
            http://proxy:1234

        Example:
            >>> my_env = os.environ.copy()
            >>> with no_proxy(my_env):
            >>>     print(os.environ.get("http_proxy"))
            >>>     print(my_env.get("http_proxy"))
            http://proxy:1234
            None

        :param env: Environment dict to remove proxy from. Optional.
        :type env: dict or None
        """
        if env is None:
            env = os.environ
        self.logger.debug("Disabling proxy")
        old_proxies = {
            "https_proxy": env.get("https_proxy"),
            "http_proxy": env.get("http_proxy"),
            "HTTPS_PROXY": env.get("HTTPS_PROXY"),
            "HTTP_PROXY": env.get("HTTP_PROXY"),
        }
        self.logger.debug("Old proxies: %s", old_proxies)
        for key, _ in old_proxies.items():
            try:
                env.pop(key)
            except KeyError:
                pass
        yield
        self.logger.debug("Restoring proxy")
        for key, value in old_proxies.items():
            if value is not None:
                env[key] = value

    @staticmethod
    def eiffel_link(event, link_type):
        """Get a LINK from an event based on type.

        Example:
            eiffel_link(tercc, "CAUSE")
        Note:
            Only returns the very first link.
            If there are multiple links you might not get the one you expect.

        :param event: Event to search in.
        :type event: :obj:`eiffel.events.BaseEiffelEvent`
        :param link_type: Type of link to search.
        :type link_type: str
        :return: The target in the link found.
        :rtype: str
        """
        for link in event.links.links:
            if link.get("type") == link_type:
                return link.get("target")
        return None

    @staticmethod
    def subprocess_signal_handler(signum, frame):  # pylint:disable=unused-argument
        """Raise subprocess read timeout."""
        raise SubprocessReadTimeout("Timeout while reading subprocess stdout.")

    def call(
        self, cmd, shell=False, env=None, executable=None, output=None, wait_output=True
    ):  # pylint:disable=too-many-arguments
        """Call a system command.

        :param cmd: Command to run.
        :type cmd: list
        :param env: Override subprocess environment.
        :type env: dict
        :param executable: Override subprocess executable.
        :type executable: str
        :param output: Path to a file to write stdout to.
        :type output: str
        :param wait_output: Whether or not to wait for output.
                            Some commands can fail in a non-interactive
                            shell due to waiting for 'readline' forever.
                            Set this to False on commands that we're
                            not in control of.
        :type wait_output: boolean
        :return: Result and output from command.
        :rtype: tuple
        """
        out = []
        for _, line in self.iterable_call(
            cmd, shell, env, executable, output, wait_output
        ):
            if isinstance(line, str):
                out.append(line)
            else:
                success = line
                break
        return success, out

    def iterable_call(
        self, cmd, shell=False, env=None, executable=None, output=None, wait_output=True
    ):  # pylint:disable=too-many-arguments
        """Call a system command and yield the output.

        :param cmd: Command to run.
        :type cmd: list
        :param env: Override subprocess environment.
        :type env: dict
        :param executable: Override subprocess executable.
        :type executable: str
        :param output: Path to a file to write stdout to.
        :type output: str
        :param wait_output: Whether or not to wait for output.
                            Some commands can fail in a non-interactive
                            shell due to waiting for 'readline' forever.
                            Set this to False on commands that we're
                            not in control of.
        :type wait_output: boolean
        :return: Result and output from command.
        :rtype: tuple
        """
        self.logger.debug("Running command: %s", " ".join(cmd))
        if shell:
            cmd = " ".join(cmd)
        proc = subprocess.Popen(  # pylint:disable=consider-using-with
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=shell,
            env=env,
            executable=executable,
        )

        signal.signal(signal.SIGALRM, self.subprocess_signal_handler)
        output_file = None
        try:
            if output:
                # pylint:disable=consider-using-with
                output_file = open(output, "w", encoding="utf-8")
            # Make sure you can read all output with 'docker logs'
            for line in iter(proc.stdout.readline, b""):
                yield proc, line.decode("utf-8").strip()
                sys.stdout.write(line.decode("utf-8"))
                signal.alarm(0)

                sys.stdout.flush()
                if output_file:
                    output_file.write(line.decode("utf-8"))

                if not wait_output:
                    signal.alarm(5)
        except SubprocessReadTimeout:
            pass
        finally:
            if output_file:
                output_file.close()

        _, err = proc.communicate()
        if err is not None:
            self.logger.debug(err.decode("utf-8"))
        self.logger.debug("Return code: %s (0=Good >0=Bad)", proc.returncode)

        # Unix return code 0 = success >0 = failure.
        # Python int 0 = failure >0 = success.
        # Converting unix return code to python bool.
        success = not proc.returncode

        yield proc, success
