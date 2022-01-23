# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tests.cipher_suite_tester import CipherSuiteTester
from tlsmate import tls
from tlsmate import msg
from tlsmate.tlssuite import TlsLibrary


class TestCase(CipherSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the CipherSuiteTester class.

    Note: The openssl server must be started with "-early_data" and we cannot use
    this option in combination with "-www".
    """

    name = "EarlyData"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -cipher ALL -early_data"
    )
    library = TlsLibrary.openssl1_1_1

    # Uncomment the line below if you do not want to use the default version and
    # adapt it to your needs.
    # version = tls.Version.TLS12

    def run(self, tlsmate, is_replaying=False):
        client = tlsmate.client
        client.init_profile()

        client.profile.versions = [tls.Version.TLS13]
        client.profile.cipher_suites = [tls.CipherSuite.TLS_AES_128_GCM_SHA256]
        client.profile.supported_groups = [
            tls.SupportedGroups.SECP256R1,
            tls.SupportedGroups.SECP384R1,
            tls.SupportedGroups.SECP521R1,
            tls.SupportedGroups.X25519,
            tls.SupportedGroups.X448,
        ]
        client.profile.key_shares = self.supported_groups
        client.profile.signature_algorithms = [
            tls.SignatureScheme.ECDSA_SECP256R1_SHA256,
            tls.SignatureScheme.RSA_PKCS1_SHA256,
            tls.SignatureScheme.RSA_PSS_PSS_SHA256,
            tls.SignatureScheme.RSA_PSS_RSAE_SHA256,
        ]
        client.profile.support_psk = True
        client.profile.psk_key_exchange_modes = [tls.PskKeyExchangeMode.PSK_DHE_KE]
        end_of_tc_reached = False
        with client.create_connection() as conn:
            conn.handshake()
            conn.wait(msg.NewSessionTicket)
            end_of_tc_reached = True
        assert end_of_tc_reached is True

        client.profile.early_data = b"This is EarlyData (0-RTT)"
        end_of_tc_reached = False
        with client.create_connection() as conn:
            conn.handshake()
            end_of_tc_reached = True
        assert end_of_tc_reached is True
        assert conn.early_data_accepted is True


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
