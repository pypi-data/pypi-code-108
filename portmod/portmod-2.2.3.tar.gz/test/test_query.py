# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests the mod selection system
"""

import io
import sys
from contextlib import redirect_stdout
from io import StringIO

import pytest

from portmod._cli.main import main
from portmod.query import display_search_results, query, query_depends
from portmodlib.atom import Atom, atom_sat

from .env import setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup_repo():
    """
    Sets up test repo for querying
    """
    yield setup_env("test")
    tear_down_env()


def test_query():
    """
    Tests that we can query for exact matches in metadata fields
    """
    results = query("license:eula")
    assert any(pkg.cpn == "test/test-eula" for pkg in results)


def test_insensitive_squelch():
    """
    Tests that we can query for case insensitive matches where there are separators
    in between keywords
    """
    results = query('desc:"desc foo"')
    assert any(pkg.cpn == "test/test" for pkg in results)


def test_depends():
    """
    Tests that we can query for mods that depend on a particular atom
    """
    results = query_depends(Atom("test/test"), all_mods=True)
    assert any(atom_sat(atom, Atom("test/test2-1.0")) for atom, _ in results)


def test_display_results():
    """
    Tests that display_search_results doesn't cause any exceptions
    and that all mods are included in the result
    """
    results = query("test")
    assert results
    strfile = io.StringIO()
    display_search_results(results, file=strfile)
    string = strfile.getvalue()
    for package in results:
        assert package.cpn in string


def test_main_depends():
    """Tests that the cli depends query interface functions sanely"""
    output = StringIO()
    with redirect_stdout(output):
        sys.argv = ["portmod", "test", "query", "-a", "depends", "test/test5"]
        main()
        assert "test/test7" in output.getvalue()


def test_main_has():
    """Tests that the cli has query interface functions sanely"""
    output = StringIO()
    with redirect_stdout(output):
        sys.argv = ["portmod", "test", "query", "-a", "has", "DATA_OVERRIDES"]
        main()
        assert "test/test6" in output.getvalue()


def test_main_hasuse():
    """Tests that the cli hasuse query interface functions sanely"""
    output = StringIO()
    with redirect_stdout(output):
        sys.argv = ["portmod", "test", "query", "-a", "hasuse", "baf"]
        main()
        assert "test/test4" in output.getvalue()


def test_main_uses():
    """Tests that the cli uses query interface functions sanely"""
    output = StringIO()
    with redirect_stdout(output):
        sys.argv = ["portmod", "test", "query", "uses", "test/test7"]
        main()
        string = output.getvalue()
        assert "foo" in string
        assert "test flag" in string


def test_main_meta():
    """Tests that the cli has query interface functions sanely"""
    output = StringIO()
    with redirect_stdout(output):
        sys.argv = ["portmod", "test", "query", "meta", "test/test"]
        main()
        assert "someone <someone@example.org>" in output.getvalue()


def test_main_list():
    """Tests that the cli has query interface functions sanely"""
    output = StringIO()
    with redirect_stdout(output):
        sys.argv = ["portmod", "test", "query", "list", "test", "--remote"]
        main()
    assert "test/test-1.0" in output.getvalue()
