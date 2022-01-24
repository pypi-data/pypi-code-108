#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the validation methods by utils
"""
import pytest
import numpy as np
from ipaddress import IPv4Address
from hvl_ccb.utils.validation import (
    validate_number,
    validate_bool,
    validate_and_resolve_host,
    validate_tcp_port,
)


def test_validate_number():
    assert validate_number("Test", 1, None, int) is None
    assert validate_number("Test", 1.1, None, float) is None
    assert validate_number("Test", [1, 2, 3]) is None
    assert validate_number("Test", np.array([1, 2, 3])) is None
    assert validate_number("Test", (1, 2, 3)) is None
    assert validate_number("Test", {"a": 1, "b": 2}) is None
    with pytest.raises(TypeError):
        validate_number("Test", [1, 2, 3.3], None, int)
    with pytest.raises(ValueError):
        validate_number("Test", -1, (0, 10), int)
    with pytest.raises(ValueError):
        validate_number("Test", [1, 2, 3.3], (1, 2))
    with pytest.raises(ValueError):
        validate_number("Test", [1, 2, 3.3], (2, 4))
    with pytest.raises(ValueError):
        validate_number("Test", [1, 2, 3.3], (2, 2.5))
    with pytest.raises(ValueError):
        validate_number("Test", [1, 2, 3.3], (None, 2.5))
    with pytest.raises(ValueError):
        validate_number("Test", [1, 2, 3.3], (2, None))
    with pytest.raises(ValueError):
        validate_number("Test", [1, 2, 3.3], (2, np.inf))
    with pytest.raises(TypeError):
        validate_number("Test", {"a": 1, "b": "c"})
    with pytest.raises(TypeError):
        validate_number("Test", "a")
    with pytest.raises(TypeError):
        validate_number("Test", 1, None, float)


def test_validate_bool():
    with pytest.raises(TypeError):
        validate_bool("Test", "True")
    assert validate_bool("Test", True) is None


def test_validate_and_resolve_host():
    assert validate_and_resolve_host("192.168.0.1") == "192.168.0.1"
    assert validate_and_resolve_host(IPv4Address("192.168.0.1")) == "192.168.0.1"
    with pytest.raises(ValueError):
        validate_and_resolve_host("192..168.0")
    with pytest.raises(ValueError):
        validate_and_resolve_host("192.168.0.1000")


def test_validate_tcp_port():
    assert validate_tcp_port(20) is None
    with pytest.raises(ValueError):
        validate_tcp_port(0)
    with pytest.raises(AttributeError):
        validate_tcp_port(None)
