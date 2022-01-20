"""Principal Modulo."""
# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "@britodfbr"  # pragma: no cover


def hello(name: str = "", greater: bool = False):
    """
    Show message to name.

    name::str: Default ""
    greater::bool: Default False
    return::str: Hello <<name>>[!|.]
    """
    name = name or "Visitor"
    period = "!" if greater else "."
    return f"Hello {name}{period}"
