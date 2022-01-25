"""
description: |
    this module provides constants yaml type to python
"""


class YAML_TYPE:
    COMPLEX_TYPE_TO_PYTHON = {
        "integer": "int",
        "string": "str",
        "array": "list",
        "boolean": "bool",
        "number": "float",
        "object": "object"
    }

    YAML_TYPE_VALUE = {
        "string": "\"\"",
        "boolean": "False",
        "integer": "0",
        "number": "0.0",
        "object": "None",
        "array": "[]"
    }

    SIMPLE_TYPE_TO_PYTHON = {
        "integer": "int",
        "string": "str",
        "array": "str",
        "boolean": "bool"
    }
