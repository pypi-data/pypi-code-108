# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2017-2022)
#
# This file is part of GWDataFind.
#
# GWDataFind is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWDataFind is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWDataFind.  If not, see <http://www.gnu.org/licenses/>.

"""The client library for the LIGO Data Replicator (LDR) service.

The DataFind service allows users to query for the location of
Gravitational-Wave Frame (GWF) files containing data from the current
gravitational-wave detectors.

This package provides the :class:`~HTTPConnection` and
:class:`~HTTPSConnection` class objects, for connecting to an LDR server
in open and authenticated access modes respectively.
The authenticated :class:`~HTTPSConnection` requires users have a valid X509
certificate that is registered with the server in question.

-----------
Quick-start
-----------

The following convenience functions are provided to perform single queries
without a persistent question:


.. currentmodule:: gwdatafind

.. autosummary::
    :nosignatures:

    ping
    find_observatories
    find_types
    find_times
    find_url
    find_urls
    find_latest

For example:

>>> from gwdatafind import find_urls
>>> urls = find_urls("L", "L1_GWOSC_O2_4KHZ_R1", 1187008880, 1187008884,
...                  host="datafind.ligo.org:443")
>>> print(urls)
['file://localhost/cvmfs/gwosc.osgstorage.org/gwdata/O2/strain.4k/frame.v1/L1/1186988032/L-L1_GWOSC_O2_4KHZ_R1-1187008512-4096.gwf']

Additionally, one can manually open a connection using the
:func:`connect` function, and then perform multiple queries.
The :func:`connect` function will automatically select the correct protocol
based on the host given, and will attempt to access any required X509
credentials.

For example:

>>> from gwdatafind import connect
>>> conn = connect(host="datafind.ligo.org", port=443)
>>> obs = conn.find_observatories()
>>> print(obs)
['H', 'V', 'L']
>>> urls = {}
>>> for ifo in obs:
...     urls[ifo] = conn.find_urls(ifo, "{}1_GWOSC_O2_4KHZ_R1".format(ifo),
...                                1187008880, 1187008884)
>>> print(urls)
{'H': ['file://localhost/cvmfs/gwosc.osgstorage.org/gwdata/O2/strain.4k/frame.v1/H1/1186988032/H-H1_GWOSC_O2_4KHZ_R1-1187008512-4096.gwf'],
 'V': ['file://localhost/cvmfs/gwosc.osgstorage.org/gwdata/O2/strain.4k/frame.v1/V1/1186988032/V-V1_GWOSC_O2_4KHZ_R1-1187008512-4096.gwf'],
 'L': ['file://localhost/cvmfs/gwosc.osgstorage.org/gwdata/O2/strain.4k/frame.v1/L1/1186988032/L-L1_GWOSC_O2_4KHZ_R1-1187008512-4096.gwf']}
"""  # noqa: E501

from .http import *
from .ui import *

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'
__credits__ = 'Scott Koranda <scott.koranda@ligo.org>'
__version__ = '1.0.5'
