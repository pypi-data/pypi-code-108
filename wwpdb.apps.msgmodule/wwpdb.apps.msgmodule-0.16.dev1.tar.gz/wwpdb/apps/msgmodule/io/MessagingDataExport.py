##
# File:    MessagingDataExport.py
# Date:    21-Sep-2010
#
# Update:
#
# 2013-09-09    RPS    Created
# 2013-09-11    RPS    Corrected handling of version number for exporting milestone file references.
#                        Accommodating creation of milestone copies on both sides of deposition <---> annotation
# 2013-09-20    RPS    Now accommodating model file in PDB format as well as cif/pdbx format for sake of milestone files.
# 2013-09-23    RPS    Correcting content format to 'pdf' for 'validation-report-annotate' file type.
# 2013-09-23    RPS    Updates to extend handling of milestone file references.
# 2013-09-24    RPS    Improved handling of milestone file references for deposit storage.
# 2013-09-27    RPS    Streamlined interface.
# 2014-07-15    RPS    Updates to support upload of more than one auxilary file in annot messaging UI.
# 2015-05-04    RPS    Improving logging in cases where file extension of aux file gives rise to exceptions
# 2018-04-23    EP     Use logging. Return current file path and current depositor file path
# 2018-04-24    EP     Add getFilePathExt() method
##

"""
Class to encapsulate data import for files requested by Messaging Module from the workflow directory hierarchy.

"""
__docformat__ = "restructuredtext en"
__author__ = "Raul Sala"
__email__ = "rsala@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"


import sys
import os
import os.path

from wwpdb.io.locator.DataReference import DataFileReference
from wwpdb.utils.config.ConfigInfo import ConfigInfo
import logging

logger = logging.getLogger(__name__)


class MessagingDataExport(object):
    """Controlling class for data import operations

    Supported file sources:
    + archive         -  WF archive storage
    + wf-instance     -  WF instance storage
    + deposit         -  WF deposit storage

    """

    def __init__(self, reqObj=None, verbose=False, log=sys.stderr):  # pylint: disable=unused-argument
        self.__verbose = verbose
        self.__reqObj = reqObj
        # self.__lfh = log
        #
        self.__sessionObj = None
        #
        if self.__verbose:
            logger.debug("starting")
        #
        self.__setup()
        #

    def __setup(self):

        try:
            self.__sessionObj = self.__reqObj.getSessionObj()
            # self.__sessionPath = self.__sessionObj.getPath()
            self.__identifier = str(self.__reqObj.getValue("identifier")).upper()
            self.__instance = str(self.__reqObj.getValue("instance")).upper()
            self.__siteId = str(self.__reqObj.getValue("WWPDB_SITE_ID"))
            self.__cI = ConfigInfo(self.__siteId)
            self.__dpstStoragePath = os.path.join(self.__cI.get("SITE_ARCHIVE_STORAGE_PATH"), "deposit", self.__identifier)
            self.__fileSource = "deposit"  # fixing value to "deposit" for now
            #
            # self.__fileSource  = str(self.__reqObj.getValue("filesource")).lower()
            # if self.__fileSource not in ['archive','wf-archive','wf-instance','wf_archive','wf_instance','deposit']:
            #     self.__fileSource = 'archive'
            #
            if self.__verbose:
                logger.debug("file source %s", self.__fileSource)
                logger.debug("identifier  %s", self.__identifier)
                logger.debug("instance    %s", self.__instance)
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("sessionId %s failed", self.__sessionObj.getId())

    def getFilePath(self, contentType, format):  # pylint: disable=redefined-builtin
        return self.__getWfFilePath(contentType=contentType, fmt=format, fileSource=self.__fileSource, version="latest")

    def getFilePathExt(self, contentType, format, fileSource="deposit", version="latest"):  # pylint: disable=redefined-builtin
        return self.__getWfFilePath(contentType=contentType, fmt=format, fileSource=fileSource, version=version)

    # ########################--Milestone File Handling--########################################################
    def getMileStoneFilePaths(self, contentType, format, partitionNum=None):  # pylint: disable=redefined-builtin
        pathDict = {}

        try:
            curFilePth = self.__getWfFilePath(contentType=contentType, fmt=format, fileSource="archive", version="latest", partitionNum=partitionNum)
            if os.path.exists(curFilePth):
                curFileNm = os.path.basename(curFilePth)
                curDpstFilePth = os.path.join(self.__dpstStoragePath, curFileNm)
                logger.debug("Found existing current path %s %s", curFilePth, curDpstFilePth)
            else:
                logger.debug("Latest file not found %s %s", contentType, format)
                curFilePth = None
                curDpstFilePth = None

            annotFilePth = self.__getWfFilePath(contentType=contentType, fmt=format, fileSource="archive", version="next", partitionNum=partitionNum)
            dpstFileNm = os.path.basename(annotFilePth)
            dpstFilePth = os.path.join(self.__dpstStoragePath, dpstFileNm)

        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("ERROR on getting milestone paths for contentType: '%s', format/file extension: '%s'", contentType, format)

        pathDict["annotPth"] = annotFilePth
        pathDict["dpstPth"] = dpstFilePth
        pathDict["curPth"] = curFilePth
        pathDict["curDpstPth"] = curDpstFilePth

        return pathDict

    ###########################################################################################################

    def __getWfFilePath(self, contentType, fmt="pdbx", fileSource="deposit", version="next", partitionNum=None):
        try:
            fPath = self.__getWfFilePathRef(contentType=contentType, fmt=fmt, fileSource=fileSource, version=version, partitionNum=partitionNum)
            logger.debug("checking %s path %s", contentType, fPath)
            if fPath is not None:
                return fPath
            else:
                return None
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("Failed to getWfFilePathRef")
            return None

    def __getWfFilePathRef(self, contentType, fmt="pdbx", fileSource="deposit", version="next", partitionNum=None):
        """Return the path to the latest version of the"""

        dfRef = DataFileReference(siteId=self.__siteId)
        logger.debug("site id is %s", dfRef.getSitePrefix())

        dfRef.setDepositionDataSetId(self.__identifier)
        if fileSource in ["archive", "wf-archive", "wf_archive"]:
            dfRef.setStorageType("archive")
        elif fileSource == "deposit":
            dfRef.setStorageType("deposit")
        elif fileSource in ["wf-instance", "wf_instance"]:
            dfRef.setWorkflowInstanceId(self.__instance)
            dfRef.setStorageType("wf-instance")
        else:
            logger.error("Bad file source for %s id %s wf id %s", contentType, self.__identifier, self.__instance)
        #
        dfRef.setContentTypeAndFormat(contentType, fmt)
        dfRef.setVersionId(version)
        #
        if partitionNum:
            dfRef.setPartitionNumber(partitionNum)
        #
        fP = None
        if dfRef.isReferenceValid():
            dP = dfRef.getDirPathReference()
            fP = dfRef.getFilePathReference()
            if self.__verbose:
                logger.debug("file directory path: %s", dP)
                logger.debug("file           path: %s", fP)
        else:
            logger.debug("bad reference for %s id %s wf id %s", contentType, self.__identifier, self.__instance)
        #
        return fP


if __name__ == "__main__":
    di = MessagingDataExport()
