# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate.workers.eval_cipher_suites import ScanCipherSuites
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary

ssl2_ck = [
    "SSL_CK_RC4_128_WITH_MD5",
    "SSL_CK_RC2_128_CBC_WITH_MD5",
    "SSL_CK_IDEA_128_CBC_WITH_MD5",
    "SSL_CK_DES_192_EDE3_CBC_WITH_MD5",
]


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_out_yaml = "profile_basic_ssl2"
    recorder_yaml = "recorder_eval_cipher_suites_ssl2"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa --no-cert-chain "
        "-- -www -cipher ALL -ssl2"
    )
    library = TlsLibrary.openssl1_0_2

    server = "localhost"

    def check_versions(self, versions):
        assert len(versions) == 6

        assert versions[0]["version"]["name"] == "SSL20"
        assert versions[0]["support"] == "TRUE"

        assert versions[1]["version"]["name"] == "SSL30"
        assert versions[1]["support"] == "FALSE"

        assert versions[2]["version"]["name"] == "TLS10"
        assert versions[2]["support"] == "FALSE"

        assert versions[3]["version"]["name"] == "TLS11"
        assert versions[3]["support"] == "FALSE"

        assert versions[4]["version"]["name"] == "TLS12"
        assert versions[4]["support"] == "FALSE"

        assert versions[5]["version"]["name"] == "TLS13"
        assert versions[5]["support"] == "FALSE"

        for a, b in zip(ssl2_ck, versions[0]["cipher_kinds"]):
            assert a == b["name"]

    def check_profile(self, profile):
        self.check_versions(profile["versions"])

    def run(self, tlsmate, is_replaying):
        for vers in ["sslv2", "sslv3", "tls10", "tls11", "tls12", "tls13"]:
            tlsmate.config.set(vers, True)
        server_profile = tlsmate.server_profile
        ScanCipherSuites(tlsmate).run()

        self.check_profile(server_profile.make_serializable())


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
