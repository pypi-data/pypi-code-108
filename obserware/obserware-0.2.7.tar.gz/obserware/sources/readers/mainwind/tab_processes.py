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


import psutil

statistics_columns = [
    "pid",
    "name",
    "terminal",
    "username",
    "status",
    "cpu_percent",
    "memory_percent",
    "num_threads",
]


def return_processes_list():
    proclist, procqant = [], 0
    for proc in psutil.process_iter(statistics_columns):
        proclist.append(
            (
                str(proc.info["pid"]),
                str(proc.info["name"]),
                str(proc.info["terminal"]),
                str(proc.info["username"]),
                str(proc.info["status"]),
                "%2.1f" % proc.info["cpu_percent"],
                "%2.1f" % proc.info["memory_percent"],
                str(proc.info["num_threads"]),
            )
        )
        procqant += 1
    retndata = {"process_list": proclist, "process_count": procqant}
    return retndata
