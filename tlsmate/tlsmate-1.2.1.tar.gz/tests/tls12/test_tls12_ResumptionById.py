# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
import logging
from tests.cipher_suite_tester import CipherSuiteTester
from tlsmate import tls
from tlsmate import msg
from tlsmate.tlssuite import TlsLibrary


class TestCase(CipherSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the CipherSuiteTester class.
    """

    name = "ResumptionById"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl1_1_1

    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    # version = tls.Version.TLS12

    def run(self, tlsmate, is_replaying=False):
        client = tlsmate.client
        client.init_profile()

        client.profile.versions = [tls.Version.TLS12]
        client.profile.cipher_suites = [
            tls.CipherSuite.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA
        ]
        client.profile.supported_groups = [
            tls.SupportedGroups.X25519,
            tls.SupportedGroups.X448,
            tls.SupportedGroups.SECT163K1,
            tls.SupportedGroups.SECT163R2,
            tls.SupportedGroups.SECT233K1,
            tls.SupportedGroups.SECT233R1,
            tls.SupportedGroups.SECT283K1,
            tls.SupportedGroups.SECT283R1,
            tls.SupportedGroups.SECT409K1,
            tls.SupportedGroups.SECT409R1,
            tls.SupportedGroups.SECT571K1,
            tls.SupportedGroups.SECT571R1,
            tls.SupportedGroups.SECP224R1,
            tls.SupportedGroups.SECP256K1,
            tls.SupportedGroups.BRAINPOOLP256R1,
            tls.SupportedGroups.BRAINPOOLP384R1,
            tls.SupportedGroups.BRAINPOOLP512R1,
            tls.SupportedGroups.SECP256R1,
            tls.SupportedGroups.SECP384R1,
            tls.SupportedGroups.SECP521R1,
            tls.SupportedGroups.FFDHE2048,
            tls.SupportedGroups.FFDHE4096,
        ]
        client.profile.signature_algorithms = [
            tls.SignatureScheme.ECDSA_SECP256R1_SHA256,
            tls.SupportedGroups.X448,
            tls.SupportedGroups.SECT163K1,
            tls.SupportedGroups.SECT163R2,
            tls.SupportedGroups.SECT233K1,
            tls.SupportedGroups.SECT233R1,
            tls.SupportedGroups.SECT283K1,
            tls.SupportedGroups.SECT283R1,
            tls.SupportedGroups.SECT409K1,
            tls.SupportedGroups.SECT409R1,
            tls.SupportedGroups.SECT571K1,
            tls.SupportedGroups.SECT571R1,
            tls.SupportedGroups.SECP224R1,
            tls.SupportedGroups.SECP256K1,
            tls.SupportedGroups.BRAINPOOLP256R1,
            tls.SupportedGroups.BRAINPOOLP384R1,
            tls.SupportedGroups.BRAINPOOLP512R1,
            tls.SupportedGroups.SECP256R1,
            tls.SupportedGroups.SECP384R1,
            tls.SupportedGroups.SECP521R1,
            tls.SupportedGroups.FFDHE2048,
            tls.SupportedGroups.FFDHE4096,
        ]
        with client.create_connection() as conn:
            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            conn.wait(msg.Certificate, optional=True)
            conn.wait(msg.ServerKeyExchange, optional=True)
            conn.wait(msg.ServerHelloDone)
            conn.send(msg.ClientKeyExchange, msg.ChangeCipherSpec, msg.Finished)
            conn.wait(msg.ChangeCipherSpec)
            conn.wait(msg.Finished)
            conn.send(msg.AppData(b"GET / HTTP/1.1\n"))
            app_data = conn.wait(msg.AppData)
            while not len(app_data.data):
                app_data = conn.wait(msg.AppData)
            for line in app_data.data.decode("utf-8").split("\n"):
                if line.startswith("s_server"):
                    logging.debug("openssl_command: " + line)
                    conn.recorder.trace(openssl_command=line)

        client.profile.support_session_id = True
        end_of_tc_reached = False
        with client.create_connection() as conn:
            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            conn.wait(msg.ChangeCipherSpec)
            conn.wait(msg.Finished)
            conn.send(msg.ChangeCipherSpec, msg.Finished)
            conn.send(msg.AppData(b"GET / HTTP/1.1\n"))
            while True:
                app_data = conn.wait(msg.AppData)
                if len(app_data.data):
                    break
            for line in app_data.data.decode("utf-8").split("\n"):
                if line.startswith("s_server"):
                    logging.debug("openssl_command: " + line)
            end_of_tc_reached = True
        assert end_of_tc_reached is True


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
