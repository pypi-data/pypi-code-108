"""
Obserware
Copyright (C) 2021 Akashdeep Dhar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


class memory:
    def __init__(self):
        """
        In order of bytes
        """
        self.petabyte = 1024 ** 5
        self.terabyte = 1024 ** 4
        self.gigabyte = 1024 ** 3
        self.megabyte = 1024 ** 2
        self.kilobyte = 1024

    def format(self, value):
        if value > self.petabyte:
            return "%.2fPB" % (value / self.petabyte)
        elif value > self.terabyte:
            return "%.2fTB" % (value / self.terabyte)
        elif value > self.gigabyte:
            return "%.2fGB" % (value / self.gigabyte)
        elif value > self.megabyte:
            return "%.2fMB" % (value / self.megabyte)
        elif value > self.kilobyte:
            return "%.2fKB" % (value / self.kilobyte)
        else:
            return "%.2fB" % (value)


class frequency:
    def __init__(self):
        """
        In order of megahertz
        """
        self.petahertz = 1000 ** 3
        self.terahertz = 1000 ** 2
        self.gigahertz = 1000

    def format(self, value):
        if value > self.petahertz:
            return "%.2fPHz" % (value / self.petahertz)
        elif value > self.terahertz:
            return "%.2fTHz" % (value / self.terahertz)
        elif value > self.gigahertz:
            return "%.2fGHz" % (value / self.gigahertz)
        else:
            return "%.2fMHz" % (value)


class time:
    def __init__(self):
        """
        In order of seconds
        """
        self.minute = 60
        self.hour = 60 * self.minute
        self.day = 24 * self.hour
        self.week = 7 * self.day
        self.month = 4 * self.week
        self.year = 12 * self.month

    def format(self, value):
        if value > self.year:
            return "%.2f years" % (value / self.year)
        elif value > self.month:
            return "%.2f months" % (value / self.month)
        elif value > self.week:
            return "%.2f weeks" % (value / self.week)
        elif value > self.day:
            return "%.2f days" % (value / self.day)
        elif value > self.hour:
            return "%.2f hours" % (value / self.hour)
        elif value > self.minute:
            return "%.2f mins" % (value / self.minute)
        else:
            return "%.2f secs" % (value)
