# -*- coding: utf-8 -*-
"""Implement unit tests for the module pdu.
"""
import tlsmate.tls as tls
from tlsmate import pdu
import pytest


def test_pack_uint8_overflow():
    val = 0xFF
    assert pdu.pack_uint8(val) == bytes.fromhex("ff")
    with pytest.raises(ValueError, match=f"Cannot pack {val + 1} into 1 byte"):
        pdu.pack_uint8(val + 1)


def test_pack_uint16_overflow():
    val = 0xFFFF
    assert pdu.pack_uint16(val) == bytes.fromhex("ff ff")
    with pytest.raises(ValueError, match=f"Cannot pack {val +1 } into 2 bytes"):
        pdu.pack_uint16(val + 1)


def test_pack_uint24_overflow():
    val = 0xFFFFFF
    assert pdu.pack_uint24(val) == bytes.fromhex("ff ff ff")
    with pytest.raises(ValueError, match=f"Cannot pack {val +1 } into 3 bytes"):
        pdu.pack_uint24(val + 1)


def test_pack_uint32_overflow():
    val = 0xFFFFFFFF
    assert pdu.pack_uint32(val) == bytes.fromhex("ff ff ff ff")
    with pytest.raises(ValueError, match=f"Cannot pack {val +1 } into 4 bytes"):
        pdu.pack_uint32(val + 1)


def test_pack_uint64_overflow():
    val = 0xFFFFFFFFFFFFFFFF
    assert pdu.pack_uint64(val) == bytes.fromhex("ff ff ff ff ff ff ff ff")
    with pytest.raises(ValueError, match=f"Cannot pack {val +1 } into 8 bytes"):
        pdu.pack_uint64(val + 1)


def test_unpack_uint8():
    data = bytes.fromhex("88 77 66 55 44 33 22 11")
    val, offset = pdu.unpack_uint8(data, len(data) - 1)
    assert val == 0x11
    with pytest.raises(
        tls.ServerMalfunction, match="message length error when unpacking parameter"
    ):
        val, offset = pdu.unpack_uint8(data, len(data))


def test_unpack_uint16():
    data = bytes.fromhex("88 77 66 55 44 33 22 11")
    val, offset = pdu.unpack_uint16(data, len(data) - 2)
    assert val == 0x2211
    with pytest.raises(
        tls.ServerMalfunction, match="message length error when unpacking parameter"
    ):
        val, offset = pdu.unpack_uint16(data, len(data) - 1)


def test_unpack_uint24():
    data = bytes.fromhex("88 77 66 55 44 33 22 11")
    val, offset = pdu.unpack_uint24(data, len(data) - 3)
    assert val == 0x332211
    with pytest.raises(
        tls.ServerMalfunction, match="message length error when unpacking parameter"
    ):
        val, offset = pdu.unpack_uint24(data, len(data) - 2)


def test_unpack_uint32():
    data = bytes.fromhex("88 77 66 55 44 33 22 11")
    val, offset = pdu.unpack_uint32(data, len(data) - 4)
    assert val == 0x44332211
    with pytest.raises(
        tls.ServerMalfunction, match="message length error when unpacking parameter"
    ):
        val, offset = pdu.unpack_uint32(data, len(data) - 3)


def test_unpack_bytes():
    data = bytes.fromhex("88 77 66 55 44 33 22 11")
    val, offset = pdu.unpack_bytes(data, 0, len(data))
    assert val == data
    with pytest.raises(
        tls.ServerMalfunction, match="message length error when unpacking parameter"
    ):
        val, offset = pdu.unpack_bytes(data, 0, len(data) + 1)
