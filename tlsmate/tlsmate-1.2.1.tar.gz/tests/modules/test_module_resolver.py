# -*- coding: utf-8 -*-
"""Implement unit tests for the module recorder.
"""
import pytest
import dns.exception
import dns.resolver
import tlsmate.tls as tls
import tlsmate.structs as structs
import tlsmate.resolver as resolver


@pytest.fixture(autouse=True)
def clear_cache():
    resolver._resolved = {}


def test_determine_l4_addr():
    l4_endpoint = resolver.determine_l4_addr("google.com", 443)
    assert l4_endpoint.host == "google.com"
    assert l4_endpoint.port == 443
    assert l4_endpoint.host_type is tls.HostType.HOST

    l4_endpoint = resolver.determine_l4_addr("123.0.1.12", 443)
    assert l4_endpoint.host == "123.0.1.12"
    assert l4_endpoint.port == 443
    assert l4_endpoint.host_type is tls.HostType.IPV4

    l4_endpoint = resolver.determine_l4_addr("fe08::23", 443)
    assert l4_endpoint.host == "fe08::23"
    assert l4_endpoint.port == 443
    assert l4_endpoint.host_type is tls.HostType.IPV6


def test_resolve_hostname():
    resolved = resolver.resolve_hostname("example.com")
    assert resolved.ipv4_addresses == ["93.184.216.34"]
    assert resolved.ipv6_addresses == ["2606:2800:220:1:248:1893:25c8:1946"]


def test_resolve_hostname_proxy(proxy):
    resolved = resolver.resolve_hostname("example.com", proxy=proxy)
    assert resolved.ipv4_addresses == ["93.184.216.34"]
    assert resolved.ipv6_addresses == ["2606:2800:220:1:248:1893:25c8:1946"]


def test_resolve_hostname_proxy_timeout(monkeypatch):
    def resolve(self, host_name, rd_type):
        raise dns.exception.Timeout

    monkeypatch.setattr(dns.resolver.Resolver, "resolve", resolve)

    resolved = resolver.resolve_hostname("example.com", proxy="http://localhost:8889")
    assert resolved.ipv4_addresses == []
    assert resolved.ipv6_addresses == []


def test_resolve_hostname_proxy_no_answer(monkeypatch):
    def resolve(self, host_name, rd_type):
        raise dns.resolver.NoAnswer

    monkeypatch.setattr(dns.resolver.Resolver, "resolve", resolve)

    resolved = resolver.resolve_hostname("example.com", proxy="http://localhost:8889")
    assert resolved.ipv4_addresses == []
    assert resolved.ipv6_addresses == []


def test_get_ip_endpoint_resolved():
    endpoint = structs.TransportEndpoint(
        host="123.123.123", port=443, host_type=tls.HostType.IPV4
    )
    resolved = resolver.get_ip_endpoint(endpoint)
    assert endpoint is resolved


def test_get_ip_endpoint_host_ipv4():
    endpoint = structs.TransportEndpoint(
        host="example.com", port=443, host_type=tls.HostType.HOST
    )
    resolved = resolver.get_ip_endpoint(endpoint)
    assert resolved.host == "93.184.216.34"
    assert resolved.port == 443
    assert resolved.host_type is tls.HostType.IPV4


def test_get_ip_endpoint_host_ipv6():
    endpoint = structs.TransportEndpoint(
        host="ipv6.test-ipv6.com", port=443, host_type=tls.HostType.HOST
    )
    resolved = resolver.get_ip_endpoint(endpoint)
    assert resolved.host == "2001:470:1:18::115"
    assert resolved.port == 443
    assert resolved.host_type is tls.HostType.IPV6


def test_get_ip_endpoint_ipv6_preference():
    endpoint = structs.TransportEndpoint(
        host="example.com", port=443, host_type=tls.HostType.HOST
    )
    resolved = resolver.get_ip_endpoint(endpoint, ipv6_preference=True)
    assert resolved.host == "2606:2800:220:1:248:1893:25c8:1946"
    assert resolved.port == 443
    assert resolved.host_type is tls.HostType.IPV6
