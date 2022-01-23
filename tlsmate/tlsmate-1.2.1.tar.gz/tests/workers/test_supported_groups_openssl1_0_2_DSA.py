# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate.workers.supported_groups import ScanSupportedGroups
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_basic_openssl1_0_2_DSA"
    sp_out_yaml = "profile_supported_groups_openssl1_0_2_DSA"
    recorder_yaml = "recorder_supported_groups_openssl1_0_2_DSA"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-dsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl1_0_2

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        ScanSupportedGroups(tlsmate).run()

        profile = server_profile.make_serializable()

        assert "supported_groups" not in profile["versions"][0]
        assert len(profile["versions"][1]["supported_groups"]) == 0
        assert len(profile["versions"][2]["supported_groups"]) == 0
        assert len(profile["versions"][3]["supported_groups"]) == 0
        assert len(profile["versions"][4]["supported_groups"]) == 0
        assert "supported_groups" not in profile["versions"][5]


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
