# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017 European Synchrotron Radiation Facility
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
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "20/01/2017"

import logging
import operator
import os
import shutil
from silx.io.octaveh5 import Octaveh5

logger = logging.getLogger(__name__)


def get_vol_file_shape(file_path):
    ddict = {}
    f = open(file_path, "r")
    lines = f.readlines()
    for line in lines:
        if "=" not in line:
            continue
        line_str = line.rstrip().replace(" ", "")
        line_str = line_str.split("#")[0]
        key, value = line_str.split("=")
        ddict[key.lower()] = value

    dimX = None
    dimY = None
    dimZ = None

    if "num_z" in ddict:
        dimZ = int(ddict["num_z"])
    if "num_y" in ddict:
        dimY = int(ddict["num_y"])
    if "num_x" in ddict:
        dimX = int(ddict["num_x"])

    return (dimZ, dimY, dimX)


def orderFileByLastLastModification(folder, fileList):
    """Return the list of files sorted by time of last modification.
    From the oldest to the newest modify"""
    res = {}
    for f in fileList:
        res[os.path.getmtime(os.path.join(folder, f))] = f

    return sorted(res.items(), key=operator.itemgetter(0))


def generateDefaultH5File(path):
    """Write a h5 file for reconstruction with the default parameters values"""
    from tomwer.core.process.reconstruction.ftseries.params.fastsetupdefineglobals import (
        FastSetupAll,
    )  # avoid cyclic import

    ft = FastSetupAll()
    ft.writeAll(path, 3.8)


def getOrCreateH5File(scanID):
    """Try to get the h5 file containing reconstruction parameters.
    If not existing create it from a set of rule.

    :param str scanID: path to the folder containing the reconstruction to run
    :param defaultOctave: If no file found then create one from our own default
        setting. This require a call to OctaveH5 and t define the targetted
        octave version
    """
    # TODO : create a setting file ?
    f = getThH5FilePath(scanID)
    if os.path.isfile(f):
        return f
    else:
        default = os.path.expanduser("~") + "/.octave/mytomodefaults.h5"
        if default and os.path.isfile(default):
            shutil.copyfile(default, f)
            assert os.path.isfile(f)
            return f
        else:
            generateDefaultH5File(f)
            assert os.path.isfile(f)
            return f


def getThH5FilePath(scanID):
    """Return the theoretical path for the h5 file used for reconstruction for
    the given folder (scan)

    :param str scanID: the path of the folder
    """
    octave_h5_param = "octave_FT_params.h5"
    assert os.path.isdir(scanID)
    return os.path.join(scanID, octave_h5_param)


def tryToFindH5File(folder, politic):
    """Return a file in the given folder if any, if more than one, follows
    defined politic.

    :param folder: the folder to explore
    :param str politic: return the newest or oldest file if more than one file
    """
    assert os.path.isdir(folder)
    assert type(politic) is str
    assert politic.lower() in ("newest", "oldest")

    result = None
    age = None
    for f in os.listdir(folder):
        # if this is the master file in a .h5 acquisition
        if f.endswith(".h5"):
            # skip master files
            if f == (os.path.basename(folder) + ".h5"):
                continue
            # skip silx process files
            if f.endswith("tomwer_processes.h5"):
                continue

            fPath = os.path.join(folder, f)
            if age is None:
                age = os.path.getmtime(fPath)
                result = fPath
            else:
                currentFileAge = os.path.getmtime(fPath)
                if currentFileAge > age and politic == "oldest":
                    age = currentFileAge
                    result = f
                if currentFileAge < age and politic == "newest":
                    age = currentFileAge
                    result = f

    return result


def saveH5File(structs, h5File, displayInfo=True):
    """Function to write the reconstruction parameters into the h5 file

    :param dict structs: the reconstruction parameters
    :param str h5File: the path to the file to create
    :param bool displayInfo: add information in the log ?
    """

    if not h5File.lower().endswith(".h5"):
        h5File = h5File + ".h5"

    # check that the file exists
    if displayInfo is True:
        mess = "try to save .h5 file ()%s ..." % h5File
        logger.info(mess)

    writer = Octaveh5(3.8)
    try:
        writer.open(h5File, "w")

        for structID in structs:
            if structs[structID] is not None:
                writer.write(structID, structs[structID])

    finally:
        writer.close()
