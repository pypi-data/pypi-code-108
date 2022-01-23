# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate.workers.robot import ScanRobot
from tlsmate.tlssuite import TlsSuiteTester, TlsLibrary


class TestCaseWeakOracle(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_basic_wolfssl3_12_0"
    recorder_yaml = "recorder_robot_weak_oracle"
    path = pathlib.Path(__file__)
    server_cmd = "utils/start_wolfssl --version {library} --port {server_port}"

    library = TlsLibrary.wolfssl3_12_0

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        tlsmate.client.alert_on_invalid_cert = False
        ScanRobot(tlsmate).run()
        profile = server_profile.make_serializable()
        assert profile["vulnerabilities"]["robot"] == "WEAK_ORACLE"


if __name__ == "__main__":
    TestCaseWeakOracle().entry(is_replaying=False)
