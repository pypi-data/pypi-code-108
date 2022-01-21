# -*- coding: utf-8 -*-


"""Prototype
{
  "lintwork": [
    {
      "file": "name",
      "line": 1,
      "type": "Error",
      "details": "text"
    }
  ]
}
"""


class File:
    MESSAGE = "message"
    PATCH = "patch"


class Format:
    DETAILS = "details"
    FILE = "file"
    LINE = "line"
    TYPE = "type"


class Type:
    ERROR = "Error"
    INFO = "Info"
    WARN = "Warn"
