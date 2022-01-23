# -*- coding: utf-8; -*-
"""Wrapper to start protoc"""
from __future__ import absolute_import, print_function

import os
import sys


__all__ = ["PROTOC_EXE", "PROTOC_INCLUDE_DIR", "exec_protoc"]


_PROTOC_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
_PROTOC_BIN_DIR = os.path.join(_PROTOC_DATA, "bin")

PROTOC_INCLUDE_DIR = os.path.join(_PROTOC_DATA, "include")

if os.name == "nt":
    PROTOC_EXE = os.path.join(_PROTOC_BIN_DIR, "protoc.exe")
else:
    PROTOC_EXE = os.path.join(_PROTOC_BIN_DIR, "protoc")


def exec_protoc(argv=None):
    """Exec protoc with arguments *argv*"""
    if argv is None:
        argv = sys.argv
    os.execv(PROTOC_EXE, tuple(argv))
