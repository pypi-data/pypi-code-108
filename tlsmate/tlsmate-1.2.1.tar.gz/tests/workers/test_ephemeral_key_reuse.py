# -*- coding: utf-8 -*-
"""Implements a class to test the grease worker.
"""
import pathlib
from tlsmate.workers.ephemeral_key_reuse import ScanEphemeralKeyReuse
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_sig_algos_openssl1_0_2"
    recorder_yaml = "recorder_ephemeral_key_reuse"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl1_0_2

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        server_profile = tlsmate.server_profile
        ScanEphemeralKeyReuse(tlsmate).run()
        profile = server_profile.make_serializable()
        ekr = profile["features"]["ephemeral_key_reuse"]
        assert ekr["tls12_dhe_reuse"] == "FALSE"
        assert ekr["tls12_ecdhe_reuse"] == "TRUE"
        assert ekr["tls13_dhe_reuse"] == "NA"
        assert ekr["tls13_ecdhe_reuse"] == "NA"


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
