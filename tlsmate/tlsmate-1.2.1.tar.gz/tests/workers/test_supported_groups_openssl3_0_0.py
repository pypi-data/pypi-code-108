# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate.workers.supported_groups import ScanSupportedGroups
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


groups_tls12 = ["SECP256R1", "SECP384R1", "SECP521R1", "X25519", "X448"]

groups_tls13 = [
    "SECP256R1",
    "SECP384R1",
    "SECP521R1",
    "X25519",
    "X448",
    "FFDHE2048",
    "FFDHE3072",
    "FFDHE4096",
    "FFDHE6144",
    "FFDHE8192",
]


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_basic_openssl3_0_0"
    sp_out_yaml = "profile_supported_groups_openssl3_0_0"
    recorder_yaml = "recorder_supported_groups_openssl3_0_0"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl3_0_0

    server = "localhost"

    def check_tls12(self, profile):
        assert profile["extension_supported"] == "TRUE"
        assert profile["server_preference"] == "FALSE"
        assert profile["groups_advertised"] == "NA"
        assert len(profile["groups"]) == len(groups_tls12)
        for a, b in zip(groups_tls12, profile["groups"]):
            assert a == b["name"]

    def check_tls13(self, profile):
        assert profile["extension_supported"] == "TRUE"
        assert profile["server_preference"] == "FALSE"
        assert profile["groups_advertised"] == "TRUE"
        assert len(profile["groups"]) == len(groups_tls13)
        for a, b in zip(groups_tls13, profile["groups"]):
            assert a == b["name"]

    def check_profile(self, profile):
        self.check_tls12(profile["versions"][4]["supported_groups"])
        self.check_tls13(profile["versions"][5]["supported_groups"])

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        client = tlsmate.client
        client.init_profile()
        ScanSupportedGroups(tlsmate).run()

        self.check_profile(server_profile.make_serializable())


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
