#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, List


def build_warning(file: str, row: any, details: str):
    return build_warning_v2(file, "", row, details)


def build_warning_v2(file: str, sheet: str, row: any, details: str):
    if hasattr(row, "__iter__") and len(row) == 1:
        row_ = '{}'.format(row[0])
    else:
        row_ = '{}'.format(row)
    return {
        'file': file,
        'sheet': sheet,
        'row': row_,
        'details': details
    }


class Error:
    def __init__(self):
        self.msgs = []
        self.warnings = []

    def has_error(self):
        return len(self.msgs) > 0

    def append(self, msg='undefined error'):
        self.msgs.append('[Error] ' + msg)

    def clear(self):
        self.msgs = []

    def msg(self):
        return '; '.join(self.msgs)

    def has_warning(self):
        return len(self.warnings) > 0

    def append_warning(self, warning: Dict[str, str]):
        self.warnings.append(warning)

    def append_warnings(self, warnings: List[Dict[str, str]]):
        if len(warnings) > 0:
            for warning in warnings:
                self.warnings.append(warning)

    def clear_warnings(self):
        self.warnings = []
