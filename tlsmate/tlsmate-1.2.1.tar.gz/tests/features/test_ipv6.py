# -*- coding: utf-8 -*-
"""Test connection to external server.
"""
import os
import pytest
import subprocess
import sys
import tlsmate.msg as msg
import tlsmate.tls as tls


@pytest.fixture
def openssl_ipv6_port(server_rsa_key_file, server_rsa_cert_file, server_rsa_chain_file):
    port = os.environ.get("TLSMATE_TEST_PORT", 44550)
    cmd = (
        f"openssl s_server -key {server_rsa_key_file} -cert {server_rsa_cert_file} "
        f"-cert_chain {server_rsa_chain_file} -accept {port} -6"
    )
    proc = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE, stdout=sys.stdout,)
    try:
        proc.wait(5)

    except subprocess.TimeoutExpired:
        pass

    else:
        raise ChildProcessError("openssl did not startup cleanly")

    yield port
    proc.kill()


def test_main(tlsmate, openssl_ipv6_port):
    tlsmate.client.set_profile(tls.Profile.INTEROPERABILITY)
    connection_completed = False
    with tlsmate.client.create_connection(
        host="::1", port=openssl_ipv6_port, sni="localhost"
    ) as conn:
        conn.send(msg.ClientHello)
        conn.wait(msg.ServerHello)
        connection_completed = True

    assert connection_completed
