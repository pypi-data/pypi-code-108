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

    path = pathlib.Path(__file__)

    cipher_suite = tls.CipherSuite.TLS_AES_128_CCM_SHA256
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL "
        "-ciphersuites TLS_AES_128_CCM_SHA256:TLS_AES_128_CCM_8_SHA256"
    )
    library = TlsLibrary.openssl1_1_1

    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    # version = tls.Version.TLS12

    def run(self, tlsmate, is_replaying=False):
        client = tlsmate.client
        client.init_profile()

        client.profile.versions = [tls.Version.TLS13]
        client.profile.cipher_suites = [tls.CipherSuite.TLS_AES_128_CCM_SHA256]
        client.profile.supported_groups = [tls.SupportedGroups.SECP256R1]
        client.profile.key_shares = [tls.SupportedGroups.SECP256R1]
        client.profile.signature_algorithms = [
            tls.SignatureScheme.RSA_PKCS1_SHA1,
            tls.SignatureScheme.ECDSA_SHA1,
            tls.SignatureScheme.RSA_PKCS1_SHA256,
            tls.SignatureScheme.ECDSA_SECP256R1_SHA256,
            tls.SignatureScheme.RSA_PKCS1_SHA384,
            tls.SignatureScheme.ECDSA_SECP384R1_SHA384,
            tls.SignatureScheme.RSA_PKCS1_SHA512,
            tls.SignatureScheme.ECDSA_SECP521R1_SHA512,
            tls.SignatureScheme.ED25519,
            tls.SignatureScheme.ED448,
            tls.SignatureScheme.RSA_PSS_PSS_SHA256,
            tls.SignatureScheme.RSA_PSS_PSS_SHA384,
            tls.SignatureScheme.RSA_PSS_PSS_SHA512,
        ]

        client.profile.support_session_ticket = True
        end_of_tc_reached = False
        with client.create_connection() as conn:

            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            conn.wait(msg.ChangeCipherSpec, optional=True)
            conn.wait(msg.EncryptedExtensions)
            conn.wait(msg.Certificate, optional=True)
            conn.wait(msg.CertificateVerify, optional=True)
            conn.wait(msg.Finished)
            conn.send(msg.Finished)
            conn.wait(msg.NewSessionTicket)
            conn.wait(msg.NewSessionTicket)

            conn.send(msg.AppData(b"GET / HTTP/1.1\n"))
            app_data = conn.wait(msg.AppData)
            while not len(app_data.data):
                app_data = conn.wait(msg.AppData)
            for line in app_data.data.decode("utf-8").split("\n"):
                if line.startswith("s_server"):
                    logging.debug("openssl_command: " + line)
                    conn.recorder.trace(openssl_command=line)
            end_of_tc_reached = True

        assert end_of_tc_reached is True


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
