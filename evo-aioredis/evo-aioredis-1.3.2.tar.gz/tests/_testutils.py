import socket

import pytest

__all__ = [
    'redis_version',
    'get_binded_addresses',
]


def redis_version(*version, reason):
    assert 1 < len(version) <= 3, version
    assert all(isinstance(v, int) for v in version), version
    return pytest.mark.redis_version(version=version, reason=reason)


def get_binded_addresses(host, port):
    all_addresses = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    ip_port_pairs = set(
        (sockaddr[0], sockaddr[1]) for (_, _, _, _, sockaddr) in all_addresses
    )
    return list(ip_port_pairs)
