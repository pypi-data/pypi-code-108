##########################################################################
#
# Copyright (C) 2019
# Associated Universities, Inc. Washington DC, USA.
#
# This script is free software; you can redistribute it and/or modify it
# under the terms of the GNU Library General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Library General Public
# License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 675 Massachusetts Ave, Cambridge, MA 02139, USA.
#
# Correspondence concerning AIPS++ should be adressed as follows:
#        Internet email: aips2-request@nrao.edu.
#        Postal address: AIPS++ Project Office
#                        National Radio Astronomy Observatory
#                        520 Edgemont Road
#                        Charlottesville, VA 22903-2475 USA
###########################################################################

import subprocess
import argparse
import os

from .casalogger import casalogger

from casatasks import casalog

print("Starting casalogger\n")

parser = argparse.ArgumentParser(description='Casalogger input parameter parser.')

logger_file_stem = casalog.logfile()

parser.add_argument('logfile',
                    type=str,
                    nargs='?',
                    default=logger_file_stem,
                    metavar='LOGFILE',
                    help='Defines custom casalogger logfile.')

_args = parser.parse_args()


casalogger(logfile=_args.logfile, terminal=True)
