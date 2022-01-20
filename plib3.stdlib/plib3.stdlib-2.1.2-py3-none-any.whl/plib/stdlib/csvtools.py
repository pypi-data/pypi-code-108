#!/usr/bin/env python3
"""
Module CSVTOOLS -- PLIB3 CSV File Utilities
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains utilities that build on the
standard library ``csv`` module.
"""

import csv
from codecs import BOM_UTF8, BOM_UTF16, BOM_UTF16_BE, BOM_UTF16_LE
from io import StringIO


def _csv_iter(f, has_header):
    rd = iter(csv.reader(f))
    hdr = next(rd) if has_header else []
    return hdr, rd


def rows_from_csv(filename, encoding='utf-8', has_header=True, return_header=False):
    with open(filename, 'r', newline='', encoding=encoding) as f:
        hdr, rd = _csv_iter(f, has_header)
        rows = list(rd)
        return (hdr, rows) if has_header and return_header else rows


def dict_from_csv(filename, encoding='utf-8', multi=False, has_header=True, return_header=False):
    # Assumes each row in CSV has only two fields unless multi is True
    with open(filename, 'r', newline='', encoding=encoding) as f:
        hdr, rd = _csv_iter(f, has_header)
        if multi:
            result = dict((row[0], row[1:]) for row in rd)
        else:
            result = dict(rd)
        return (hdr, result) if has_header and return_header else result


BOM_MAP = {
    'utf-8': BOM_UTF8,
    'utf-16': BOM_UTF16,
    'utf-16-be': BOM_UTF16_BE,
    'utf-16-le': BOM_UTF16_LE
}


def write_csv(rows, filename, encoding='utf-8', write_bom=False, write_bom_by_char=False,
              bom_map=BOM_MAP, replacements=None):
    
    with StringIO(newline='') as f:
        wr = csv.writer(f)
        for row in rows:
            wr.writerow(row)
        s = f.getvalue()
    b = s.encode(encoding)
    
    bom = bom_map.get(encoding)
    if bom:
        if write_bom:
            b = bom + b
        if write_bom_by_char and replacements:
            for rb in replacements[encoding]:
                b = b.replace(rb, bom + rb)
    
    with open(filename, 'wb') as f:
        f.write(b)
