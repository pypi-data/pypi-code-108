# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "31/05/2017"


# TODO: change this for enum

OBSERVATION_STATUS = {
    "not processing": 0,  # data watcher is not doing anything
    "parsing": 1,  # data watcher is parsing folders
    "none found": 2,  # data watcher haven't found anything
    "starting": 3,  # data watcher have found an acquisition starting
    "started": 4,  # data watcher have found an acquisition started
    "waiting for acquisition ending": 5,  # data watcher is waiting for all .edf file to be copied
    "acquisition ended": 6,  # data watcher have found an acquisition completed
    "acquisition canceled": 7,  # data watcher have found an acquisition canceled
    "failure": -1,  # data watcher have encountered an issue. Should be associated with an info describing it
    "aborted": -2,  # if aborted by acquisition
}

DICT_OBS_STATUS = {}
for name, value in OBSERVATION_STATUS.items():
    DICT_OBS_STATUS[value] = name

" Possible status of a data watcher observation"

DET_END_XML = "[scan].xml"
"""DET_END for detection end.
In this case we are looking for the scan.xml file. On it is here then the
acquisition is considered ended
"""

PARSE_INFO_FILE = "[scan].info"
"""
In this case we will end for the .info to be here and then parse it to know how
many .edf file we are waiting for and wait for all of them to be recorded.
"""

DET_END_USER_ENTRY = "from file pattern"
"""DET_END for detection end.
In this case the user specify the pattern we are looking for
"""

DET_END_METHODS = (DET_END_XML, PARSE_INFO_FILE, DET_END_USER_ENTRY)
"""List of option that can notice the end of the acquisition"""
