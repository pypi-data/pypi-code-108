# -*- coding: utf-8 -*-
"""Helper module for generating and executing test cases
"""
# import basic stuff
import logging

# import own stuff
from tlsmate import tls
from tlsmate import msg
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate import utils

# import other stuff


class CipherSuiteTester(TlsSuiteTester):
    """A class which allows to test a specific cipher suite

    A simple test case scenario is implemented with the goal to test a
    full handshake with for a given cipher suite. The server must be an openssl-
    compatible server, as it is expected to receive the openssl-command from a
    simple http request (opensssl s_server -www ...).

    The yaml file for the recorder is named after the cipher suite (done in the
    base class). The cipher suite is specified as a class property.
    Optionally, the version, the supported groups and the signature algorithms
    may be specified as well, otherwise, defaults are used.

    Derived classes MUST define the cipher suite and the path, anything else
    is not required. The test case is recorded by calling
    CipherSuiteTester.record_testcase, and it is replayed by pytest automatically
    (via test_entry method of the TlsSuiteTester class).
    """

    # The name of the yaml file. If None, the name is taken from the
    # cipher suite name
    name = None
    path = None
    cipher_suite = None
    version = tls.Version.TLS12
    supported_groups = [
        tls.SupportedGroups.X25519,
        tls.SupportedGroups.SECP256R1,
        tls.SupportedGroups.SECP384R1,
        tls.SupportedGroups.SECP521R1,
        tls.SupportedGroups.FFDHE2048,
        tls.SupportedGroups.FFDHE4096,
    ]
    signature_algorithms = [
        tls.SignatureScheme.ECDSA_SECP256R1_SHA256,
        tls.SignatureScheme.ECDSA_SECP384R1_SHA384,
        tls.SignatureScheme.ECDSA_SECP521R1_SHA512,
        tls.SignatureScheme.RSA_PSS_RSAE_SHA256,
        tls.SignatureScheme.RSA_PSS_RSAE_SHA384,
        tls.SignatureScheme.RSA_PSS_RSAE_SHA512,
        tls.SignatureScheme.RSA_PKCS1_SHA256,
        tls.SignatureScheme.RSA_PKCS1_SHA384,
        tls.SignatureScheme.RSA_PKCS1_SHA512,
        tls.SignatureScheme.ECDSA_SHA1,
        tls.SignatureScheme.RSA_PKCS1_SHA1,
    ]

    def update_client(self, client):
        """A method which can be overwritten to update the client as needed.
        """
        pass

    def run(self, tlsmate, is_replaying=False):
        """The basic scenario to be recorded or replayed.
        """
        client = tlsmate.client
        client.init_profile()

        client.profile.versions = [self.version]
        client.profile.cipher_suites = [self.cipher_suite]
        client.profile.supported_groups = self.supported_groups
        client.profile.key_shares = self.supported_groups
        client.profile.signature_algorithms = self.signature_algorithms
        self.update_client(client)

        end_of_tc_reached = False
        with client.create_connection() as conn:
            conn.handshake()

            # Cool feature by openssl: if the server is started with the -www
            # option, an HTTP get request will return some information,
            # including the command line used to start the server. We will
            # extract this line and add it to the yaml file.
            # The command openssl_command.py can then be used to read out this
            # information.
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
        return conn

    def entry(self, is_replaying=False):
        """The entry point for the test case.

        Arguments:
            is_replaying (bool): an indication if the test case is recorded or replayed.
        """
        if not is_replaying:
            utils.set_logging_level("debug")
        name = getattr(self, "name")
        if name is not None:
            self.recorder_yaml = self.name
        else:
            self.recorder_yaml = self.cipher_suite.name
        super().entry(is_replaying)
