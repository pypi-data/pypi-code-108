#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# This file is part of refidx
# License: GPLv3
# See the documentation at benvial.gitlab.io/refidx


def test_metadata(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "importlib.metadata", None)
    import refidx


def test_nometadata():
    import importlib

    import refidx

    importlib.reload(refidx.__about__)


def test_data():
    import refidx

    refidx.__about__.get_meta(None)
