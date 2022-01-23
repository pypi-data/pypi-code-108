# -*- coding: utf-8 -*-
"""Implements a class to test the test profile worker.
"""
from tlsmate.workers.server_profile import ReadProfileWorker, DumpProfileWorker
from tlsmate.config import Configuration
from tlsmate.tlsmate import TlsMate
from tlsmate.structs import ConfigItem


def test_server_profile_read_dump(server_profile, capsys):
    with open(server_profile) as fd:
        server_file = fd.read()

    config = Configuration()
    config.register(ConfigItem("write_profile"))
    config.register(ConfigItem("read_profile"))
    config.register(ConfigItem("format", type=str, default="yaml"))
    config.set("read_profile", str(server_profile))
    tlsmate = TlsMate(config)
    ReadProfileWorker(tlsmate).run()
    DumpProfileWorker(tlsmate).run()

    captured = capsys.readouterr()
    a1 = server_file.split("\n")
    a2 = captured.out.split("\n")
    for a, b in zip(a1, a2):
        assert a == b
