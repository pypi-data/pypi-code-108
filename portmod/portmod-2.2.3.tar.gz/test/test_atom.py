# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Atom parsing tests
"""

import pytest

from portmodlib.atom import Atom, InvalidAtom


def test_invalid():
    with pytest.raises(InvalidAtom):
        Atom("foo/bar baz")


def test_valid():
    Atom("foo/bar-baz-1.0.20.3-r123::foo[-a,b?,!c?,c]")


def test_complex_version():
    Atom("foo/bar-1.0a_alpha")
    Atom("foo/bar-1.0a_alpha12")
    Atom("foo/bar-1.0a_pre1")
    Atom("foo/bar-1.0a_beta2")
    Atom("foo/bar-1.0a_rc1")
    Atom("foo/bar-1.0a_p1")


def test_nodots():
    assert Atom("foo/bar-1").PV == "1"
