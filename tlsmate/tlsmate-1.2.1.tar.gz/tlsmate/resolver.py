# -*- coding: utf-8 -*-
"""Module for host name handling
"""
# import basic stuff
import socket
import logging
from typing import Optional, Tuple, List

# import own stuff
import tlsmate.structs as structs
import tlsmate.tls as tls
import tlsmate.utils as utils

# import other stuff
import dns.resolver
import dns.exception

_DOH_SERVER = [
    "https://dns.google/dns-query",
    "https://cloudflare-dns.com/dns-query",
    "https://dns.quad9.net/dns-query",
    "https://dns.digitale-gesellschaft.ch/dns-query",
]


def determine_l4_addr(host: str, port: int) -> structs.TransportEndpoint:
    """Determine type of the host

    Arguments:
        host: the given host. This might be an IP address or a hostname.
        port: the given port.

    Returns:
        The structure representing a transport protocol endpoint.
    """

    try:
        socket.inet_pton(socket.AF_INET, host)
        host_type = tls.HostType.IPV4

    except OSError:
        try:
            socket.inet_pton(socket.AF_INET6, host)
            host_type = tls.HostType.IPV6

        except OSError:
            host_type = tls.HostType.HOST

    return structs.TransportEndpoint(host=host, port=port, host_type=host_type)


_resolved = {}


def _resolve_directly(host_name: str) -> Tuple[List[str], List[str]]:
    try:
        ips = socket.getaddrinfo(host_name, None, type=socket.SOCK_STREAM)

    except socket.gaierror:
        utils.exit_with_error(f"Cannot resolve domain name {host_name}")

    ipv4_addresses = [item[4][0] for item in ips if item[0] is socket.AF_INET]
    ipv6_addresses = [item[4][0] for item in ips if item[0] is socket.AF_INET6]
    return ipv4_addresses, ipv6_addresses


def _resolve_rdtype_via_proxy(
    host_name: str, resolver: dns.resolver.Resolver, rd_type: str
) -> List[str]:
    try:
        answer = resolver.resolve(host_name, rd_type)
        return [rr.address for rr in answer]

    except dns.resolver.NoAnswer:
        return []

    except dns.exception.Timeout:
        return []


def _resolve_via_proxy(host_name: str, proxy: str) -> Tuple[List[str], List[str]]:
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = _DOH_SERVER
    ipv4_addresses = _resolve_rdtype_via_proxy(host_name, resolver, "A")
    ipv6_addresses = _resolve_rdtype_via_proxy(host_name, resolver, "AAAA")
    return ipv4_addresses, ipv6_addresses


def resolve_hostname(
    host_name: str, proxy: Optional[str] = None
) -> structs.ResolvedHost:
    """Resolve a hostname into sets of IPv4 and IPv6 addresses

    Arguments:
        host_name: the host name to resolve. May not be an IP address.
        proxy: the http proxy to use for resolving the hostname

    Returns:
        the structure for a resolved host name.
    """

    if host_name not in _resolved:
        logging.debug(f"Performing DNS lookup for {host_name}")
        if proxy:
            ipv4_addresses, ipv6_addresses = _resolve_via_proxy(host_name, proxy)

        else:
            ipv4_addresses, ipv6_addresses = _resolve_directly(host_name)

        _resolved[host_name] = structs.ResolvedHost(
            ipv4_addresses=ipv4_addresses, ipv6_addresses=ipv6_addresses
        )
        for ipv4 in ipv4_addresses:
            logging.debug(f"IPv4 address: {ipv4}")

        for ipv6 in ipv6_addresses:
            logging.debug(f"IPv6 address: {ipv6}")

    return _resolved[host_name]


def get_ip_endpoint(
    l4_addr: structs.TransportEndpoint,
    proxy: Optional[str] = None,
    ipv6_preference: bool = False,
) -> structs.TransportEndpoint:
    """Resolve the hostname, if applicable.

    Arguments:
        l4_addr: the l4_addr to resolve
        proxy: the http proxy to use for resolving the hostname

    Returns:
        the l4_addr, either with an IPv4 or IPv6 address.
    """

    if l4_addr.host_type is not tls.HostType.HOST:
        return l4_addr

    ips = resolve_hostname(l4_addr.host, proxy)

    ipv4_present = bool(ips.ipv4_addresses)
    ipv6_present = bool(ips.ipv6_addresses)
    if not ipv4_present and not ipv6_present:
        raise tls.ScanError(f"No IP address available for {l4_addr.host}")

    if ipv4_present and ipv6_present:
        host_type = tls.HostType.IPV6 if ipv6_preference else tls.HostType.IPV4

    else:
        host_type = tls.HostType.IPV4 if ipv4_present else tls.HostType.IPV6

    host = (
        ips.ipv4_addresses[0]
        if host_type is tls.HostType.IPV4
        else ips.ipv6_addresses[0]
    )

    return structs.TransportEndpoint(host=host, port=l4_addr.port, host_type=host_type)
