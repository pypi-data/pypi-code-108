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


import time
from datetime import datetime

import psutil


def return_mainscreen_onetimed_statistics(prociden):
    procobjc = psutil.Process(prociden)
    retndata = {
        "prociden": procobjc.pid,
        "procname": procobjc.name(),
        "cpu_percent": procobjc.cpu_percent(),
        "memory_percent": procobjc.memory_percent(),
        "cpu_num": procobjc.cpu_num(),
        "num_threads": procobjc.num_threads(),
        "username": procobjc.username(),
        "terminal": procobjc.terminal(),
        "nice": procobjc.nice(),
        "ionice": procobjc.ionice().value,
        "num_ctx_switches": {
            "voluntary": procobjc.num_ctx_switches().voluntary,
            "involuntary": procobjc.num_ctx_switches().involuntary,
        },
        "ppid": procobjc.ppid(),
        "status": procobjc.status().title(),
        "create_time": datetime.fromtimestamp(procobjc.create_time()).strftime(
            "%Y-%m-%d, %H:%M:%S"
        ),
        "acquired_on": datetime.fromtimestamp(time.time()).strftime(
            "%Y-%m-%d, %H:%M:%S"
        ),
    }
    return retndata
