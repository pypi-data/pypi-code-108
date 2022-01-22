#! /usr/bin/env python3
"""
Module _NAMES -- Tuple/sequence name/argument validation
Sub-Package STDLIB.COLL of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from itertools import chain
from keyword import iskeyword

from plib.stdlib.builtins import type_from_name
from plib.stdlib.iters import group_into


def _rename_names(names):
    seen = set()
    for index, name in enumerate(names):
        if (not all(c.isalnum() or c=='_' for c in name)
            or iskeyword(name)
            or not name
            or name[0].isdigit()
            or name.startswith('_')
            or name in seen):
            names[index] = '_{:d}'.format(index)
        seen.add(name)


def _validate_names(names):
    for name in names:
        if not all(c.isalnum() or c=='_' for c in name):
            raise ValueError("Type names and field names can only contain alphanumeric characters and underscores: {!r}".format(name))
        if iskeyword(name):
            raise ValueError("Type names and field names cannot be a keyword: {!r}".format(name))
        if name[0].isdigit():
            raise ValueError("Type names and field names cannot start with a number: {!r}".format(name))


def _check_names(names, rename):
    seen = set()
    for name in names:
        if name.startswith('_') and not rename:
            raise ValueError("Field names cannot start with an underscore: {!r}".format(name))
        if name in seen:
            raise ValueError("Encountered duplicate field name: {!r}".format(name))
        seen.add(name)


def _check_type(obj):
    if isinstance(obj, str):
        return type_from_name(obj)
    return obj


def _make_doc(typename, arg_list):
    return '{typename}({arg_list})'.format(**locals())


def process_names(typename, field_names, rename):
    if isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split() # names separated by whitespace and/or commas
    field_names = list(map(str, field_names))
    if rename:
        _rename_names(field_names)
    _validate_names([typename] + field_names)
    _check_names(field_names, rename)
    
    arg_list = repr(tuple(field_names)).replace("'", "")[1:-1]
    return field_names, _make_doc(typename, arg_list)


def process_specs(typename, fieldspecs, rename):
    if isinstance(fieldspecs, str):
        # Names and types separated by whitespace and/or commas
        fieldspecs = fieldspecs.replace(',', ' ').split()
    if not isinstance(fieldspecs[0], tuple):
        # Format name, type pairs into tuples
        if ' ' in fieldspecs[0]:
            # It's a list of '<name> <type>' strings
            fieldspecs = list(chain(fieldspec.split(' ', 1) for fieldspec in fieldspecs))
        else:
            # It's a list <name>, <type>, <name>, <type>, ...
            fieldspecs = list(group_into(2, fieldspecs))
    field_names = list(map(str, [spec[0] for spec in fieldspecs]))
    if rename:
        _rename_names(field_names)
    field_types = list(map(_check_type, [spec[1] for spec in fieldspecs]))
    field_specs = list(zip(field_names, field_types))
    _validate_names([typename] + field_names)
    _check_names(field_names, rename)
    
    arg_list = repr([
        '{} <{}>'.format(fieldname, fieldtype.__name__) for fieldname, fieldtype in field_specs
    ]).replace("'", "")[1:-1]
    return fieldspecs, field_names, field_types, field_specs, _make_doc(typename, arg_list)
