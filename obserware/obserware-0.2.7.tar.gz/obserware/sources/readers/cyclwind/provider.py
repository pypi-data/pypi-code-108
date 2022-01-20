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

from obserware.sources.readers import frequency

freqvalu = frequency()


def return_mainscreen_threaded_statistics():
    cpcyfreq, cpcyperc, cpcyqant = (
        psutil.cpu_freq(percpu=True),
        psutil.cpu_percent(percpu=True),
        psutil.cpu_count(),
    )
    retndata = {}
    for indx in range(cpcyqant):
        retndata[indx] = {
            "frequency": {
                "cur": freqvalu.format(cpcyfreq[indx].current),
                "min": freqvalu.format(cpcyfreq[indx].min),
                "max": freqvalu.format(cpcyfreq[indx].max),
            },
            "percent": cpcyperc[indx],
        }
    return retndata


def return_mainscreen_onetimed_statistics():
    retndata = psutil.cpu_count()
    return retndata
