# -*- coding: utf-8 -*-

# import basic stuff

# import own stuff
from tlsmate import tls

# import other stuff


def test_order_supported_versions(tlsmate):
    tlsmate.client.set_profile(tls.Profile.MODERN)
    tlsmate.client.profile.versions = [
        tls.Version.TLS10,
        tls.Version.SSL20,
        tls.Version.TLS13,
        tls.Version.TLS11,
    ]
    client_hello = tlsmate.client.client_hello()
    versions = client_hello.get_extension(tls.Extension.SUPPORTED_VERSIONS).versions
    assert versions == [
        tls.Version.TLS13,
        tls.Version.TLS11,
        tls.Version.TLS10,
        tls.Version.SSL20,
    ]
