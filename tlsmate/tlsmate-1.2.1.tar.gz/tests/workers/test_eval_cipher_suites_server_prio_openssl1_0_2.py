# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate.workers.eval_cipher_suites import ScanCipherSuites
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


tls10_cs = [
    "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
    "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
    "TLS_DHE_RSA_WITH_AES_256_CBC_SHA",
    "TLS_DHE_RSA_WITH_CAMELLIA_256_CBC_SHA",
    "TLS_ECDH_ANON_WITH_AES_256_CBC_SHA",
    "TLS_DH_ANON_WITH_AES_256_CBC_SHA",
    "TLS_DH_ANON_WITH_CAMELLIA_256_CBC_SHA",
    "TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA",
    "TLS_RSA_WITH_AES_256_CBC_SHA",
    "TLS_RSA_WITH_CAMELLIA_256_CBC_SHA",
    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
    "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
    "TLS_DHE_RSA_WITH_AES_128_CBC_SHA",
    "TLS_DHE_RSA_WITH_SEED_CBC_SHA",
    "TLS_DHE_RSA_WITH_CAMELLIA_128_CBC_SHA",
    "TLS_ECDH_ANON_WITH_AES_128_CBC_SHA",
    "TLS_DH_ANON_WITH_AES_128_CBC_SHA",
    "TLS_DH_ANON_WITH_SEED_CBC_SHA",
    "TLS_DH_ANON_WITH_CAMELLIA_128_CBC_SHA",
    "TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA",
    "TLS_RSA_WITH_AES_128_CBC_SHA",
    "TLS_RSA_WITH_SEED_CBC_SHA",
    "TLS_RSA_WITH_CAMELLIA_128_CBC_SHA",
    "TLS_RSA_WITH_IDEA_CBC_SHA",
    "TLS_ECDHE_RSA_WITH_RC4_128_SHA",
    "TLS_ECDHE_ECDSA_WITH_RC4_128_SHA",
    "TLS_ECDH_ANON_WITH_RC4_128_SHA",
    "TLS_DH_ANON_WITH_RC4_128_MD5",
    "TLS_ECDH_ECDSA_WITH_RC4_128_SHA",
    "TLS_RSA_WITH_RC4_128_SHA",
    "TLS_RSA_WITH_RC4_128_MD5",
    "TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA",
    "TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA",
    "TLS_DHE_RSA_WITH_3DES_EDE_CBC_SHA",
    "TLS_ECDH_ANON_WITH_3DES_EDE_CBC_SHA",
    "TLS_DH_ANON_WITH_3DES_EDE_CBC_SHA",
    "TLS_ECDH_ECDSA_WITH_3DES_EDE_CBC_SHA",
    "TLS_RSA_WITH_3DES_EDE_CBC_SHA",
]


tls12_cs = [
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384",
    "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
    "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
    "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_DHE_RSA_WITH_AES_256_CBC_SHA256",
    "TLS_DHE_RSA_WITH_AES_256_CBC_SHA",
    "TLS_DHE_RSA_WITH_CAMELLIA_256_CBC_SHA",
    "TLS_ECDH_ANON_WITH_AES_256_CBC_SHA",
    "TLS_DH_ANON_WITH_AES_256_GCM_SHA384",
    "TLS_DH_ANON_WITH_AES_256_CBC_SHA256",
    "TLS_DH_ANON_WITH_AES_256_CBC_SHA",
    "TLS_DH_ANON_WITH_CAMELLIA_256_CBC_SHA",
    "TLS_ECDH_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA384",
    "TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA",
    "TLS_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_RSA_WITH_AES_256_CBC_SHA256",
    "TLS_RSA_WITH_AES_256_CBC_SHA",
    "TLS_RSA_WITH_CAMELLIA_256_CBC_SHA",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
    "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
    "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_DHE_RSA_WITH_AES_128_CBC_SHA256",
    "TLS_DHE_RSA_WITH_AES_128_CBC_SHA",
    "TLS_DHE_RSA_WITH_SEED_CBC_SHA",
    "TLS_DHE_RSA_WITH_CAMELLIA_128_CBC_SHA",
    "TLS_ECDH_ANON_WITH_AES_128_CBC_SHA",
    "TLS_DH_ANON_WITH_AES_128_GCM_SHA256",
    "TLS_DH_ANON_WITH_AES_128_CBC_SHA256",
    "TLS_DH_ANON_WITH_AES_128_CBC_SHA",
    "TLS_DH_ANON_WITH_SEED_CBC_SHA",
    "TLS_DH_ANON_WITH_CAMELLIA_128_CBC_SHA",
    "TLS_ECDH_ECDSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA256",
    "TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA",
    "TLS_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_RSA_WITH_AES_128_CBC_SHA256",
    "TLS_RSA_WITH_AES_128_CBC_SHA",
    "TLS_RSA_WITH_SEED_CBC_SHA",
    "TLS_RSA_WITH_CAMELLIA_128_CBC_SHA",
    "TLS_RSA_WITH_IDEA_CBC_SHA",
    "TLS_ECDHE_RSA_WITH_RC4_128_SHA",
    "TLS_ECDHE_ECDSA_WITH_RC4_128_SHA",
    "TLS_ECDH_ANON_WITH_RC4_128_SHA",
    "TLS_DH_ANON_WITH_RC4_128_MD5",
    "TLS_ECDH_ECDSA_WITH_RC4_128_SHA",
    "TLS_RSA_WITH_RC4_128_SHA",
    "TLS_RSA_WITH_RC4_128_MD5",
    "TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA",
    "TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA",
    "TLS_DHE_RSA_WITH_3DES_EDE_CBC_SHA",
    "TLS_ECDH_ANON_WITH_3DES_EDE_CBC_SHA",
    "TLS_DH_ANON_WITH_3DES_EDE_CBC_SHA",
    "TLS_ECDH_ECDSA_WITH_3DES_EDE_CBC_SHA",
    "TLS_RSA_WITH_3DES_EDE_CBC_SHA",
]


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_out_yaml = "profile_basic_server_prio_openssl1_0_2"
    recorder_yaml = "recorder_eval_cipher_suites_server_prio_openssl1_0_2"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL -serverpref"
    )
    library = TlsLibrary.openssl1_0_2

    server = "localhost"

    def check_cert_chain(self, cert_chain):
        assert len(cert_chain) == 2
        assert cert_chain[0]["id"] == 1
        assert cert_chain[1]["id"] == 2
        assert len(cert_chain[0]["cert_chain"]) == 2
        assert len(cert_chain[1]["cert_chain"]) == 2

    def check_versions(self, versions):
        assert len(versions) == 6

        assert versions[0]["version"]["name"] == "SSL20"
        assert versions[0]["support"] == "FALSE"

        assert versions[1]["version"]["name"] == "SSL30"
        assert versions[1]["support"] == "TRUE"
        assert versions[1]["ciphers"]["server_preference"] == "TRUE"

        assert versions[2]["version"]["name"] == "TLS10"
        assert versions[2]["support"] == "TRUE"
        assert versions[2]["ciphers"]["server_preference"] == "TRUE"

        assert versions[3]["version"]["name"] == "TLS11"
        assert versions[3]["support"] == "TRUE"
        assert versions[3]["ciphers"]["server_preference"] == "TRUE"

        assert versions[4]["version"]["name"] == "TLS12"
        assert versions[4]["support"] == "TRUE"
        assert versions[4]["ciphers"]["server_preference"] == "TRUE"

        assert versions[5]["version"]["name"] == "TLS13"
        assert versions[5]["support"] == "FALSE"

        for a, b in zip(tls10_cs, versions[1]["ciphers"]["cipher_suites"]):
            assert a == b["name"]
        for a, b in zip(tls10_cs, versions[2]["ciphers"]["cipher_suites"]):
            assert a == b["name"]
        for a, b in zip(tls10_cs, versions[3]["ciphers"]["cipher_suites"]):
            assert a == b["name"]
        for a, b in zip(tls12_cs, versions[4]["ciphers"]["cipher_suites"]):
            assert a == b["name"]

    def check_profile(self, profile):
        self.check_cert_chain(profile["cert_chains"])
        self.check_versions(profile["versions"])

    def run(self, tlsmate, is_replaying):
        for vers in ["sslv2", "sslv3", "tls10", "tls11", "tls12", "tls13"]:
            tlsmate.config.set(vers, True)
        server_profile = tlsmate.server_profile
        ScanCipherSuites(tlsmate).run()

        self.check_profile(server_profile.make_serializable())


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
