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

import psutil

from obserware.sources.readers import memory

mmrysize = memory()


def return_global_network_rate():
    pvntiocf = psutil.net_io_counters(pernic=False)
    time.sleep(1)
    nxntiocf = psutil.net_io_counters(pernic=False)
    retndata = {
        "bytes": {
            "recv": "%s/s" % mmrysize.format(nxntiocf.bytes_recv - pvntiocf.bytes_recv),
            "sent": "%s/s" % mmrysize.format(nxntiocf.bytes_sent - pvntiocf.bytes_sent),
        },
        "packets": {
            "recv": "%dPk/s" % (nxntiocf.packets_recv - pvntiocf.packets_recv),
            "sent": "%dPk/s" % (nxntiocf.packets_sent - pvntiocf.packets_sent),
        },
    }
    return retndata


def return_pernic_threaded_statistics():
    pvntioct = psutil.net_io_counters(pernic=True)
    time.sleep(1)
    nxntioct = psutil.net_io_counters(pernic=True)
    retndata, netifsat = (
        [],
        psutil.net_if_stats(),
    )
    for indx in nxntioct.keys():
        retndata.append(
            (
                indx,
                netifsat[indx].isup,
                "%s/s"
                % mmrysize.format(
                    nxntioct[indx].bytes_recv - pvntioct[indx].bytes_recv
                ),
                "%s/s"
                % mmrysize.format(
                    nxntioct[indx].bytes_sent - pvntioct[indx].bytes_sent
                ),
                "%dPk/s"
                % int(nxntioct[indx].packets_recv - pvntioct[indx].packets_recv),
                "%dPk/s"
                % int(nxntioct[indx].packets_sent - pvntioct[indx].packets_sent),
                "%s" % mmrysize.format(nxntioct[indx].bytes_recv),
                "%s" % mmrysize.format(nxntioct[indx].bytes_sent),
                "%ldPk(s)" % nxntioct[indx].packets_recv,
                "%ldPk(s)" % nxntioct[indx].packets_sent,
                "%ld error(s)" % nxntioct[indx].errin,
                "%ld error(s)" % nxntioct[indx].errout,
                "%ldPk(s)" % nxntioct[indx].dropin,
                "%ldPk(s)" % nxntioct[indx].dropout,
            )
        )
    return retndata


def return_mainscreen_threaded_statistics():
    netiocnf = psutil.net_io_counters(pernic=False)
    retndata = {
        "bytes": {
            "recv": "%s" % mmrysize.format(netiocnf.bytes_recv),
            "sent": "%s" % mmrysize.format(netiocnf.bytes_sent),
        },
        "packets": {
            "recv": "%ldPk(s)" % netiocnf.packets_recv,
            "sent": "%ldPk(s)" % netiocnf.packets_sent,
        },
        "errors": {
            "recv": "%ld error(s)" % netiocnf.errin,
            "sent": "%ld error(s)" % netiocnf.errout,
        },
        "dropped": {
            "recv": "%ldPk(s)" % netiocnf.dropin,
            "sent": "%ldPk(s)" % netiocnf.dropout,
        },
    }
    return retndata
