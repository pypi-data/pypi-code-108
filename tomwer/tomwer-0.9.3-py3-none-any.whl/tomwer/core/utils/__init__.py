# coding: utf-8
# ##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
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
# ###########################################################################

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "17/05/2017"

import fabio.edfimage
import os
import psutil
import logging
import shutil
from tomwer.core import settings
from tomoscan.unitsystem import metricsystem
from urllib.request import urlopen
import fileinput
from lxml import etree

logger = logging.getLogger(__name__)

MOCK_LOW_MEM = False  # if True will simulate the case the computer run into low memory

IGNORE_LOW_MEM = False


def isLowOnMemory(path=""):
    """

    :return: True if the RAM usage is more than MAX_MEM_USED (or low memory
       is simulated)
    """
    if IGNORE_LOW_MEM is True:
        return False
    if path == settings.get_dest_path():
        if settings.MOCK_LBSRAM is True:
            return MOCK_LOW_MEM
        else:
            assert os.path.isdir(path)
            return psutil.disk_usage(path).percent > settings.MAX_MEM_USED
    else:
        return (MOCK_LOW_MEM is True) or (
            os.path.exists(path)
            and (psutil.disk_usage(path).percent > settings.MAX_MEM_USED)
        )


def ignoreLowMemory(value=True):
    """ignore the low memory information"""
    global IGNORE_LOW_MEM
    IGNORE_LOW_MEM = value


def mockLowMemory(b=True):
    """Mock the case the computer is running into low memory"""
    global MOCK_LOW_MEM
    MOCK_LOW_MEM = b
    return psutil.virtual_memory().percent > settings.MAX_MEM_USED


def _getInformation(scan, refFile, information, _type, aliases=None):
    """
    Parse files contained in the given directory to get the requested
    information

    :param scan: directory containing the acquisition. Must be an absolute path
    :param refFile: the refXXXX_YYYY which should contain information about the
                    scan.
    :return: the requested information or None if not found
    """

    def parseRefFile(filePath):
        header = fabio.open(filePath).header
        for k in aliases:
            if k in header:
                return _type(header[k])
        return None

    def parseXMLFile(filePath):
        try:
            for alias in info_aliases:
                tree = etree.parse(filePath)
                elmt = tree.find("acquisition/" + alias)
                if elmt is None:
                    continue
                else:
                    info = _type(elmt.text)
                    if info == -1:
                        return None
                    else:
                        return info
        except etree.XMLSyntaxError as e:
            logger.warning(e)
            return None

    def parseInfoFile(filePath):
        def extractInformation(text, alias):
            text = text.replace(alias, "")
            text = text.replace("\n", "")
            text = text.replace(" ", "")
            text = text.replace("=", "")
            return _type(text)

        info = None
        f = open(filePath, "r")
        line = f.readline()
        while line:
            for alias in info_aliases:
                if alias in line:
                    info = extractInformation(line, alias)
                    break
            line = f.readline()
        f.close()
        return info

    info_aliases = [information]
    if aliases is not None:
        assert type(aliases) in (tuple, list)
        [info_aliases.append(alias) for alias in aliases]

    if not os.path.isdir(scan):
        return None

    if refFile is not None and os.path.isfile(refFile):
        try:
            info = parseRefFile(refFile)
        except IOError as e:
            logger.warning(e)
        else:
            if info is not None:
                return info

    baseName = os.path.basename(scan)
    infoFiles = [os.path.join(scan, baseName + ".info")]
    infoOnDataVisitor = infoFiles[0].replace("lbsram", "", 1)
    # hack to check in lbsram, would need to be removed to add some consistency
    if os.path.isfile(infoOnDataVisitor):
        infoFiles.append(infoOnDataVisitor)
    for infoFile in infoFiles:
        if os.path.isfile(infoFile) is True:
            info = parseInfoFile(infoFile)
            if info is not None:
                return info

    xmlFiles = [os.path.join(scan, baseName + ".xml")]
    xmlOnDataVisitor = xmlFiles[0].replace("lbsram", "", 1)
    # hack to check in lbsram, would need to be removed to add some consistency
    if os.path.isfile(xmlOnDataVisitor):
        xmlFiles.append(xmlOnDataVisitor)
    for xmlFile in xmlFiles:
        if os.path.isfile(xmlFile) is True:
            info = parseXMLFile(xmlFile)
            if info is not None:
                return info

    return None


def getClosestEnergy(scan, refFile=None):
    """
    Parse files contained in the given directory to get information about the
    incoming energy for the serie `iSerie`

    :param scan: directory containing the acquisition
    :param refFile: the refXXXX_YYYY which should contain information about the
                    energy.
    :return: the energy in keV or none if no energy found
    """
    return _getInformation(
        os.path.abspath(scan),
        refFile,
        information="Energy",
        aliases=["energy", "ENERGY"],
        _type=float,
    )


def getClosestSRCurrent(scan_dir, refFile=None):
    """
    Parse files contained in the given directory to get information about the
    incoming energy for the serie `iSerie`

    :param scan_dir: directory containing the acquisition
    :param refFile: the refXXXX_YYYY which should contain information about the
                    energy.
    :return: the energy in keV or none if no energy found
    """
    return _getInformation(
        os.path.abspath(scan_dir),
        refFile,
        information="SRCUR",
        aliases=["SrCurrent", "machineCurrentStart"],
        _type=float,
    )


def getSRCurrent(scan_dir, when):
    assert when in ("start", "end")
    xmlFiles = [
        os.path.join(os.path.abspath(scan_dir), os.path.basename(scan_dir) + ".xml")
    ]
    xmlOnDataVisitor = xmlFiles[0].replace("lbsram", "", 1)
    # hack to check in lbsram, would need to be removed to add some consistency
    if os.path.isfile(xmlOnDataVisitor):
        xmlFiles.append(xmlOnDataVisitor)
    for xmlFile in xmlFiles:
        if os.path.isfile(xmlFile):
            try:
                tree = etree.parse(xmlFile)
                key = "machineCurrentStart" if when == "start" else "machineCurrentStop"
                elmt = tree.find("acquisition/" + key)
                if elmt is None:
                    return None
                else:
                    info = float(elmt.text)
                    if info == -1:
                        return None
                    else:
                        return info
            except etree.XMLSyntaxError as e:
                logger.warning(e)
                return None
    return None


# TODO : should be moved in the scan module
def getTomo_N(scan):
    """Return the number of radio taken"""
    return _getInformation(
        os.path.abspath(scan),
        refFile=None,
        information="TOMO_N",
        _type=int,
        aliases=["tomo_N", "Tomo_N"],
    )


# TODO mv to scan module
def getScanRange(scan):
    return _getInformation(
        os.path.abspath(scan),
        refFile=None,
        information="ScanRange",
        _type=int,
        aliases=["scanRange"],
    )


# TODO: mv to scan module
def getDARK_N(scan):
    return _getInformation(
        os.path.abspath(scan),
        refFile=None,
        information="DARK_N",
        _type=int,
        aliases=["dark_N"],
    )


def getRef_N(scan):
    return _getInformation(
        os.path.abspath(scan),
        refFile=None,
        information="REF_N",
        _type=int,
        aliases=["ref_N"],
    )


def getRefOn(scan):
    return _getInformation(
        os.path.abspath(scan),
        refFile=None,
        information="REF_ON",
        _type=int,
        aliases=["ref_On"],
    )


def rebaseParFile(_file, oldfolder, newfolder):
    """Update the given .par file to replace oldfolder location by the newfolder.

    .. warning:: make the replacement in place.

    :param _file: par file to update
    :param oldfolder: previous location of the .par file
    :param newfolder: new location of the .par file
    """
    with fileinput.FileInput(_file, inplace=True, backup=".bak") as parfile:
        for line in parfile:
            line = line.rstrip().replace(oldfolder, newfolder, 1)
            print(line)


# TODO: move to scan module
def getDim1Dim2(scan):
    """

    :param scan: path to the acquisition
    :return: detector definition
    :rtype: tuple of int
    """
    d1 = _getInformation(
        scan=scan,
        refFile=None,
        information="Dim_1",
        aliases=["projectionSize/DIM_1"],
        _type=int,
    )
    d2 = _getInformation(
        scan=scan,
        refFile=None,
        information="Dim_2",
        aliases=["projectionSize/DIM_2"],
        _type=int,
    )
    return d1, d2


# TODO: move to scan module
def getStartEndVoxels(scan):
    _info_file = os.path.join(scan, os.path.basename(scan) + ".info")
    sv_1 = _getInformation(
        scan=scan,
        refFile=_info_file,
        information="START_VOXEL_1",
        aliases=["projectionSize/ROW_BEG"],
    )
    ev_1 = _getInformation(
        scan=scan,
        refFile=_info_file,
        information="END_VOXEL_1",
        aliases=["projectionSize/ROW_END"],
    )

    sv_2 = _getInformation(
        scan=scan,
        refFile=_info_file,
        information="START_VOXEL_2",
        aliases=["projectionSize/COL_BEG"],
    )
    ev_2 = _getInformation(
        scan=scan,
        refFile=_info_file,
        information="END_VOXEL_2",
        aliases=["projectionSize/COL_END"],
    )

    sv_3 = _getInformation(scan=scan, refFile=_info_file, information="START_VOXEL_3")
    ev_3 = _getInformation(scan=scan, refFile=_info_file, information="END_VOXEL_3")

    dim_1, dim_2 = getDim1Dim2(scan=scan)
    sv_1 = sv_1 or 0
    sv_2 = sv_2 or 0
    sv_3 = sv_3 or 0

    ev_1 = ev_1 or dim_1 - 1
    ev_2 = ev_2 or dim_1 - 1
    ev_3 = ev_3 or dim_2 - 1

    return (sv_1, ev_1, sv_2, ev_2, sv_3, ev_3)


# TODO: move to scan module
def getParametersFromParOrInfo(_file):
    """
    Create a dictionary from the file with the information name as keys and
    their values as values
    """
    assert os.path.exists(_file) and os.path.isfile(_file)
    ddict = {}
    f = open(_file, "r")
    lines = f.readlines()
    for line in lines:
        if "=" not in line:
            continue
        line_str = line.replace(" ", "")
        line_str = line_str.rstrip("\n")
        # remove on the line comments
        if "#" in line_str:
            line_str = line_str.split("#")[0]
        if line_str == "":
            continue
        try:
            key, value = line_str.split("=")
        except ValueError:
            logger.error('fail to extract information from "%s"' % line_str)
        else:
            ddict[key.lower()] = value
    return ddict


# TODO: move to scan module
def getFirstProjFile(scan):
    """Return the first .edf containing a projection"""
    if os.path.isdir(scan) is False:
        return None
    files = sorted(os.listdir(scan))

    while (
        len(files) > 0
        and (files[0].startswith(os.path.basename(scan)) and files[0].endswith(".edf"))
        is False
    ):
        files.remove(files[0])

    if len(files) > 0:
        return os.path.join(scan, files[0])
    else:
        return None


def getPixelSize(scan):
    """
    Try to retrieve the pixel size from the set of files.

    :return: the pixel size in meter or None
    :rtype: None or float
    """
    if os.path.isdir(scan) is False:
        return None
    value = _getInformation(
        scan=scan,
        refFile=None,
        information="PixelSize",
        _type=float,
        aliases=["pixelSize"],
    )
    if value is None:
        parFile = os.path.join(scan, os.path.basename(scan) + ".par")
        if os.path.exists(parFile):
            ddict = getParametersFromParOrInfo(parFile)
            if "IMAGE_PIXEL_SIZE_1".lower() in ddict:
                value = float(ddict["IMAGE_PIXEL_SIZE_1".lower()])
    # for now pixel size are stored in microns. We want to return them in meter
    if value is not None:
        return value * metricsystem.micrometer.value
    else:
        return None


url_base = "http://www.edna-site.org/pub/tomwer/"
# url_base = 'http://ftp.edna-site.org/tomwer/'


def DownloadDataset(dataset, output_folder, timeout, unpack=False):
    # create if needed path scan
    url = url_base + dataset

    logger.info("Trying to download scan %s, timeout set to %ss", dataset, timeout)
    logger.info("wget %s" % url)

    data = urlopen(url, data=None, timeout=timeout).read()
    logger.info("Image %s successfully downloaded." % dataset)

    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    try:
        archive_folder = os.path.join(output_folder, os.path.basename(dataset))
        with open(archive_folder, "wb") as outfile:
            outfile.write(data)
    except IOError:
        raise IOError(
            "unable to write downloaded \
                        data to disk at %s"
            % archive_folder
        )

    if unpack is True:
        shutil.unpack_archive(archive_folder, extract_dir=output_folder, format="bztar")
        os.remove(archive_folder)
