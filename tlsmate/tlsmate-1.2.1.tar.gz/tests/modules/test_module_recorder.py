# -*- coding: utf-8 -*-
"""Implement unit tests for the module recorder.
"""
import datetime
import time
from tlsmate.recorder import SocketEvent
import pytest
import requests


class Response(object):
    pass


def test_inject_basic(tlsmate):

    recorder = tlsmate.recorder
    recorder.trace(ec_seed=1)
    assert recorder.is_injecting() is False
    assert recorder.is_recording() is False

    recorder.record()
    assert recorder.is_injecting() is False
    assert recorder.is_recording() is True

    data = bytes.fromhex("00 11 22 33 44 55 66 77 88 99 aa bb cc")
    assert recorder.inject(verify_data_finished_sent=data) == data
    assert recorder.inject(ec_seed=5) == 5
    assert recorder.inject(openssl_command="hello world")
    assert recorder.inject(timestamp=15.9)
    assert recorder.inject(client_auth=True)

    recorder.replay()
    assert recorder.is_injecting() is True
    assert recorder.is_recording() is False

    assert recorder.inject(verify_data_finished_sent=b"deadbeef") == data
    assert recorder.inject(ec_seed=10) == 5
    assert recorder.inject(openssl_command="baeh!") == "hello world"
    assert recorder.inject(timestamp=15000.9) == 15.9
    assert recorder.inject(client_auth=False) is True

    recorder.deactivate()
    assert recorder.is_injecting() is False
    assert recorder.is_recording() is False


def test_client_auth(tlsmate):
    recorder = tlsmate.recorder
    recorder.record()
    recorder.trace_client_auth(("hello", "world"))

    recorder.replay()
    assert recorder.get_client_auth() == [("hello", "world")]


def test_socket_recv(tlsmate):
    recorder = tlsmate.recorder
    recorder.record()
    assert recorder.inject_socket_recv() is None
    data = bytes.fromhex("00 11 22 33 44 55 66 77 88 99 aa bb cc")
    recorder.additional_delay(0.500)
    recorder.additional_delay(0.200)
    recorder.trace_socket_recv(0.050, SocketEvent.DATA, data)

    recorder.replay()
    start = datetime.datetime.now()
    assert recorder.inject_socket_recv() == data
    duration = datetime.datetime.now() - start
    assert 700 <= duration.microseconds / 1000 <= 800


def test_reponse(tlsmate):
    recorder = tlsmate.recorder
    recorder.record()
    data = bytes.fromhex("00 11 22 33 44 55 66 77 88 99 aa bb cc")
    resp = Response()
    resp.ok = True
    resp.content = data
    resp.status_code = 200
    recorder.trace_response(0.050, SocketEvent.DATA, resp)

    recorder.replay()
    resp = recorder.inject_response()
    assert resp.ok is True
    assert resp.content == data
    assert resp.status_code == 200


def test_timestamp(tlsmate):
    recorder = tlsmate.recorder
    recorder.record()
    timestamp1 = recorder.get_timestamp()
    time.sleep(0.1)
    recorder.replay()
    timestamp2 = recorder.get_timestamp()
    assert timestamp1 == timestamp2


def test_send_all(tlsmate):
    recorder = tlsmate.recorder
    recorder.record()
    data = bytes.fromhex("00 11 22 33 44 55 66 77 88 99 aa bb cc")
    assert recorder.trace_socket_sendall(data) is True


def test_inject_resonse_closure(tlsmate):
    recorder = tlsmate.recorder
    recorder.record()
    recorder.trace_response(0.010, SocketEvent.CLOSURE)
    recorder.replay()
    with pytest.raises(Exception):
        recorder.inject_response()


def test_inject_resonse_timeout(tlsmate):
    recorder = tlsmate.recorder
    recorder.record()
    assert recorder.inject_response() is None
    recorder.trace_response(0.010, SocketEvent.TIMEOUT)
    recorder.replay()
    with pytest.raises(requests.Timeout):
        recorder.inject_response()
