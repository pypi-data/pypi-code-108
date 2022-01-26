# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Download and source related tests
"""

from portmod.pybuild import parse_arrow


def test_simple_source_parsing():
    """
    Simple source test of basic functionality
    """
    path = "http://simplesource.com/foo.zip"
    results = parse_arrow(path.split())

    assert len(results) == 1
    assert results[0].url == path
    assert results[0].name == "foo.zip"
    assert results[0].basename == "foo"


def test_arrow_source_parsing():
    """
    Tests parsing arrow notation
    """
    path = "http://simplesource.com/foo.zip"
    path2 = "http://othersource.com/foo.zip"
    results = parse_arrow(f"{path} -> bar.zip {path2}".split())

    assert len(results) == 2
    assert results[0].url == path
    assert results[0].name == "bar.zip"
    assert results[0].basename == "bar"
    assert results[1].url == path2
    assert results[1].name == "foo.zip"
    assert results[1].basename == "foo"
