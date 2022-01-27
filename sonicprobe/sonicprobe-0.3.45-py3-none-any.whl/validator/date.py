# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 Adrien Delle Cave
# SPDX-License-Identifier: GPL-3.0-or-later
"""sonicprobe.validator.date"""

from datetime import datetime

class SPValidatorDate(object): # pylint: disable=useless-object-inheritance
    def __init__(self, xformat = None):
        self.xformat = xformat

    def validate(self, value, xformat = None):
        if not xformat:
            if self.xformat:
                xformat = self.xformat
            else:
                xformat = "%Y-%m-%d"

        try:
            datetime.strptime(value, xformat)
            return True
        except ValueError:
            return False

class SPValidatorDateTime(object): # pylint: disable=useless-object-inheritance
    def __init__(self, xformat = None):
        self.xformat = xformat

    def validate(self, value, xformat = None):
        if not xformat:
            if self.xformat:
                xformat = self.xformat
            else:
                xformat = "%Y-%m-%d %H:%M:%S"

        try:
            datetime.strptime(value, xformat)
            return True
        except ValueError:
            return False
