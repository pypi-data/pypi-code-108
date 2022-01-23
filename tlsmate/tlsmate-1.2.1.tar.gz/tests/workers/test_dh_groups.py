# -*- coding: utf-8 -*-
"""Implements a class to test the dh-groups worker.
"""
import pathlib
from tlsmate.workers.dh_params import ScanDhGroups
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary
from tlsmate.tlsmate import TLSMATE_DIR


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_sig_algos_openssl1_0_2"
    recorder_yaml = "recorder_dh_groups"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL"
    ) + f" -dhparam {str(TLSMATE_DIR)}/utils/dhparam_modp_2048.pem"
    library = TlsLibrary.openssl1_0_2

    server = "localhost"

    def check_profile(self, prof):
        group = prof["versions"][2]["dh_group"]
        assert group["name"] == "RFC3526: 2048-bit MODP Group"
        assert group["size"] == 2048
        assert group["g_value"] == 2

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        ScanDhGroups(tlsmate).run()
        self.check_profile(server_profile.make_serializable())


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
