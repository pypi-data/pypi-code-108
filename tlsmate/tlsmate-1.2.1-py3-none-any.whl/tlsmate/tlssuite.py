# -*- coding: utf-8 -*-
"""Module defining classes for test suites
"""
# import basic stuff
import abc
import subprocess
import sys
import time
import enum
import os
import logging
import pathlib
from typing import Optional

# import own stuff
import tlsmate.config as conf
import tlsmate.structs as structs
import tlsmate.tlsmate as tm
import tlsmate.utils as utils

# import other stuff


class TlsLibrary(enum.Enum):
    """Defines enums for TLS libraries used for unit tests.

    Note, that the the libraries must be build in the directory "tlslibrary".
    E.g., the binary executable for openssl versions 3.0.0 is located in
    tlslibraries/openssl3_0_0/apps/openssl (base directory is the source directory
    for tlsmate.)

    Note, that the names of the enums are equal to the directory names under
    the tlslibraries directory, because the enum names are used to locate the
    binaries.
    """

    openssl1_0_1e = enum.auto()
    openssl1_0_1g = enum.auto()
    openssl1_0_2 = enum.auto()
    openssl1_1_1 = enum.auto()
    openssl3_0_0 = enum.auto()
    wolfssl3_12_0 = enum.auto()
    wolfssl4_8_0 = enum.auto()


class TlsSuiteTester(metaclass=abc.ABCMeta):
    """Base class to define unit tests

    Attributes:
        recorder_yaml (str): the name of the yaml file with the serialized recorder
            object
        sp_in_yaml (str): the file name of the server profile to read and deserialize
        sp_out_yaml (str): the file name of server profile to write and serialize
        path (pathlib.Path): the path of the test script
        server (str): the name of the server to use to generate the test case
        port (int): the port number to use to generate the test case
    """

    recorder_yaml = None
    sp_in_yaml: Optional[str] = None
    sp_out_yaml = None
    path = None
    server_cmd: Optional[str] = None

    @abc.abstractmethod
    def run(self, tlsmate: tm.TlsMate, is_replaying: bool) -> None:
        pass

    def _start_server(self):

        ca_cmd = tm.TLSMATE_DIR / "utils/start_ca_servers"
        logging.debug(f'starting CA servers with command "{ca_cmd}"')
        exit_code = os.system(tm.TLSMATE_DIR / "utils/start_ca_servers")
        if exit_code != 0:
            raise ValueError(f"Could not start CA servers, exit code: {exit_code}")

        cmd = (
            str(tm.TLSMATE_DIR)
            + "/"
            + self.server_cmd.format(
                library=self.library.name, server_port=self.config.get("port"),
            )
        )

        logging.debug(f'starting TLS server with command "{cmd}"')
        self.server_proc = subprocess.Popen(
            cmd.split(),
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            universal_newlines=True,
        )
        time.sleep(2)  # give the TLS server some time for a clean startup

    def server_input(self, input_str: str, timeout: Optional[int] = None) -> None:
        """Feed a string to the server process' STDIN pipe

        Arguments:
            input_str: the string to provide on the STDIN pipe
            timeout: the timeout to wait before providing the input in
                milliseconds.
        """

        if self.recorder.is_injecting():
            return

        if timeout is not None:
            self.recorder.additional_delay(timeout / 1000)
            time.sleep(timeout / 1000)

        print(input_str, file=self.server_proc.stdin, flush=True)

    def get_yaml_file(self, name: Optional[str]) -> Optional[pathlib.Path]:
        """Determine the file where an object is serialized to.

        Arguments:
            name (str): the basic name of the file, without directory and without
                the suffix

        Returns:
            :class:`pathlib.Path`: a Path object for the yaml file
        """

        if name is None:
            return None

        return (
            self.path.resolve().parent / "recordings" / (name + ".yaml")  # type: ignore
        )

    def entry(self, is_replaying: bool = False) -> None:
        """Entry point for a test case.

        Arguments:
            is_replaying (bool): an indication if the test case is replayed or recorded.
                Defaults to False.
        """

        utils.set_logging_format()

        if is_replaying:
            ini_file = None

        else:
            ini_file = tm.TLSMATE_DIR / "tests/tlsmate.ini"
            if not ini_file.is_file():
                ini_file = None

        self.config = conf.Configuration()
        self.config.register(structs.ConfigItem("pytest_recorder_file", type=str))
        self.config.register(structs.ConfigItem("pytest_recorder_replaying", type=str))

        if not is_replaying:
            self.config.init_from_external(ini_file)  # type: ignore

        self.config.set("progress", False)
        self.config.set("read_profile", self.get_yaml_file(self.sp_in_yaml))
        self.config.set("pytest_recorder_file", self.get_yaml_file(self.recorder_yaml))
        self.config.set("pytest_recorder_replaying", is_replaying)
        utils.set_logging_level(self.config.get("logging"))

        self.tlsmate = tm.TlsMate(self.config)
        self.recorder = self.tlsmate.recorder

        if not is_replaying:
            if self.server_cmd is not None:
                self._start_server()

        self.run(self.tlsmate, is_replaying)

        if not is_replaying:
            if self.recorder_yaml is not None:
                self.tlsmate.recorder.serialize(self.get_yaml_file(self.recorder_yaml))

            if self.sp_out_yaml is not None:
                utils.serialize_data(
                    self.tlsmate.server_profile.make_serializable(),
                    file_name=self.get_yaml_file(self.sp_out_yaml),
                    replace=False,
                    indent=2,
                )

    def test_entry(self):
        """Entry point for pytest.
        """

        self.entry(is_replaying=True)
