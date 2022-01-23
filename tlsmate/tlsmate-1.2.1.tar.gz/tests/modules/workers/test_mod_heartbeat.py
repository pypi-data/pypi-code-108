# -*- coding: utf-8 -*-
"""Implement unit tests for the module utils.
"""
from tlsmate import tls
from tlsmate import msg
from tlsmate import ext
from tlsmate.socket import Socket
from tlsmate.connection import TlsConnection
from tlsmate.workers.heartbeat import ScanHeartbeat
from tlsmate.server_profile import ServerProfile
from tlsmate.client import Client


class Object(object):
    pass


def get_profile_values(self, filter_versions, full_hs=False):
    prof = Object()
    prof.versions = [True]
    return prof


def init_profile(self, **kwargs):
    pass


def open_socket(self, addr):
    pass


def heartbeat_response_ok(self, timeout=5):
    return bytes.fromhex(
        "18 03 03 00 2e 02 00 0b 61 62 72 61 63 61 64 61 62 72 61 "
        "00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f"
    )


def handshake_ok(self):
    self.handshake_completed = True
    server_hello = msg.ServerHello()
    hb = ext.ExtHeartbeat(heartbeat_mode=tls.HeartbeatMode.PEER_ALLOWED_TO_SEND)
    server_hello.extensions.append(hb)
    self.msg.server_hello = server_hello


def test_heartbeat_ok(monkeypatch, tlsmate):
    monkeypatch.setattr(ServerProfile, "get_profile_values", get_profile_values)
    monkeypatch.setattr(Client, "init_profile", init_profile)
    monkeypatch.setattr(Socket, "open_socket", open_socket)
    monkeypatch.setattr(Socket, "recv_data", heartbeat_response_ok)
    monkeypatch.setattr(TlsConnection, "handshake", handshake_ok)
    ScanHeartbeat(tlsmate).run()
    assert tlsmate.server_profile.features.heartbeat is tls.HeartbeatState.TRUE


def heartbeat_response_wrong_resp(self, timeout=5):
    return bytes.fromhex(
        "18 03 03 00 2e 02 00 0b 62 62 72 61 63 61 64 61 62 72 61 "
        "00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f"
    )


def test_heartbeat_wrong_resp(monkeypatch, tlsmate):
    monkeypatch.setattr(ServerProfile, "get_profile_values", get_profile_values)
    monkeypatch.setattr(Client, "init_profile", init_profile)
    monkeypatch.setattr(Socket, "open_socket", open_socket)
    monkeypatch.setattr(Socket, "recv_data", heartbeat_response_wrong_resp)
    monkeypatch.setattr(TlsConnection, "handshake", handshake_ok)
    ScanHeartbeat(tlsmate).run()
    assert (
        tlsmate.server_profile.features.heartbeat is tls.HeartbeatState.WRONG_RESPONSE
    )


def heartbeat_response_wrong_msg(self, timeout=5):
    return bytes.fromhex("15 03 03 00 02 01 00")


def test_heartbeat_wrong_msg(monkeypatch, tlsmate):
    monkeypatch.setattr(ServerProfile, "get_profile_values", get_profile_values)
    monkeypatch.setattr(Client, "init_profile", init_profile)
    monkeypatch.setattr(Socket, "open_socket", open_socket)
    monkeypatch.setattr(Socket, "recv_data", heartbeat_response_wrong_msg)
    monkeypatch.setattr(TlsConnection, "handshake", handshake_ok)
    ScanHeartbeat(tlsmate).run()
    assert (
        tlsmate.server_profile.features.heartbeat
        is tls.HeartbeatState.UNEXPECTED_MESSAGE
    )


def handshake_hb_not_allowed(self):
    self.handshake_completed = True
    server_hello = msg.ServerHello()
    hb = ext.ExtHeartbeat(heartbeat_mode=tls.HeartbeatMode.PEER_NOT_ALLOWED_TO_SEND)
    server_hello.extensions.append(hb)
    self.msg.server_hello = server_hello


def test_heartbeat_not_allowed(monkeypatch, tlsmate):
    monkeypatch.setattr(ServerProfile, "get_profile_values", get_profile_values)
    monkeypatch.setattr(Client, "init_profile", init_profile)
    monkeypatch.setattr(Socket, "open_socket", open_socket)
    monkeypatch.setattr(TlsConnection, "handshake", handshake_hb_not_allowed)
    ScanHeartbeat(tlsmate).run()
    assert tlsmate.server_profile.features.heartbeat is tls.HeartbeatState.FALSE


def handshake_no_ext(self):
    self.handshake_completed = True
    self.msg.server_hello = msg.ServerHello()


def test_heartbeat_no_ext(monkeypatch, tlsmate):
    monkeypatch.setattr(ServerProfile, "get_profile_values", get_profile_values)
    monkeypatch.setattr(Client, "init_profile", init_profile)
    monkeypatch.setattr(Socket, "open_socket", open_socket)
    monkeypatch.setattr(TlsConnection, "handshake", handshake_no_ext)
    ScanHeartbeat(tlsmate).run()
    assert tlsmate.server_profile.features.heartbeat is tls.HeartbeatState.FALSE


def get_profile_values_no_versions(self, filter_versions, full_hs=False):
    prof = Object()
    prof.versions = []
    return prof


def test_no_versions(monkeypatch, tlsmate):
    monkeypatch.setattr(
        ServerProfile, "get_profile_values", get_profile_values_no_versions
    )
    ScanHeartbeat(tlsmate).run()
    assert tlsmate.server_profile.features.heartbeat is tls.HeartbeatState.NA


def heartbeat_no_response(self, timeout=5):
    raise tls.TlsMsgTimeoutError


def test_heartbeat_no_resonse(monkeypatch, tlsmate):
    monkeypatch.setattr(ServerProfile, "get_profile_values", get_profile_values)
    monkeypatch.setattr(Client, "init_profile", init_profile)
    monkeypatch.setattr(Socket, "open_socket", open_socket)
    monkeypatch.setattr(Socket, "recv_data", heartbeat_no_response)
    monkeypatch.setattr(TlsConnection, "handshake", handshake_ok)
    ScanHeartbeat(tlsmate).run()
    assert tlsmate.server_profile.features.heartbeat is tls.HeartbeatState.NOT_REPONDING
