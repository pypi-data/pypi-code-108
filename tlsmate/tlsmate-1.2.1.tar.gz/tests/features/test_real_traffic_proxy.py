# -*- coding: utf-8 -*-
"""Test connection to external server via a proxy.
"""
import tlsmate.tls as tls


def test_main(tlsmate, proxy):
    tlsmate.config.set("proxy", proxy)
    tlsmate.client.set_profile(tls.Profile.INTEROPERABILITY)
    with tlsmate.client.create_connection("mozilla-modern.badssl.com") as conn:
        conn.handshake()

    assert conn.handshake_completed
