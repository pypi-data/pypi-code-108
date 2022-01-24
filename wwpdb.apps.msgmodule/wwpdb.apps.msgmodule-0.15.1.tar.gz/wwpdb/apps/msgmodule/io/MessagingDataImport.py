##
# File:    MessagingDataImport.py
# Date:    21-Sep-2010
#
# Update:
#
# 2013-09-09    RPS    Ported here from EditorDataImport
# 2013-09-20    RPS    Now method for accommodating model file in PDB format as well as cif/pdbx format.
# 2013-09-23    RPS    Updates to extend handling of milestone file references. Added "deposit" as valid file source.
# 2013-09-27    RPS    Streamlined interface.
# 2013-10-30    RPS    Support for "Notes" UI
# 2014-07-15    RPS    Updates to support upload of more than one auxilary file in annot messaging UI
# 2014-09-17    RPS    Addressed bug regarding failure to provide path to file for contentTypes where "createAsNeeded" in play
# 2016-09-14    ZF     Added support for group deposition message files
# 2018-04-23    EP     Add logging
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

import logging

logger = logging.getLogger(__name__)


class MessagingDataImport(object):
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
        logger.debug("Starting")
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
            self.__fileSource = "archive"  # fixing value to "archive" for now
            # """
            # self.__fileSource  = str(self.__reqObj.getValue("filesource")).lower()
            # if self.__fileSource not in ['archive','wf-archive','wf-instance','wf_archive','wf_instance']:
            #     self.__fileSource = 'archive'
            # """
            #
            # Added by ZF
            #
            self.__groupId = str(self.__reqObj.getValue("groupid")).upper()
            if (not self.__groupId) and len(self.__instance) == 9 and self.__instance[0:2] == "G_":
                self.__groupId = self.__instance
                self.__fileSource = "autogroup"
            #
            if self.__verbose:
                logger.debug("file source %s", self.__fileSource)
                logger.debug("identifier  %s", self.__identifier)
                logger.debug("instance    %s", self.__instance)
        except:  # noqa: E722  pylint: disable=bare-except
            logger.exception("sessionId %s failed", self.__sessionObj.getId())

    def getFilePath(self, contentType, format):  # pylint: disable=redefined-builtin
        createAsNeeded = True if (contentType in ["messages-from-depositor", "messages-to-depositor", "notes-from-annotator"]) else False
        return self.__getWfFilePath(contentType=contentType, fmt=format, fileSource=self.__fileSource, version="latest", createAsNeeded=createAsNeeded)

    # ########################--Milestone File Handling--########################################################
    def getMileStoneFilePaths(self, contentType, format, version="latest", partitionNum=None):  # pylint: disable=redefined-builtin
        pathDict = {}
        pathDict["dpstPth"] = self.__getWfFilePath(contentType=contentType, fmt=format, fileSource="deposit", version=version)
        pathDict["annotPth"] = self.__getWfFilePath(
            contentType=contentType, fmt=format, fileSource=self.__fileSource, version=version, createAsNeeded=False, partitionNum=partitionNum
        )
        return pathDict

    ###########################################################################################################

    def __getWfFilePath(self, contentType, fmt="pdbx", fileSource="archive", version="latest", createAsNeeded=False, partitionNum=None):
        try:
            fPath = self.__getWfFilePathRef(contentType=contentType, fmt=fmt, fileSource=fileSource, version=version, partitionNum=partitionNum)
            logger.debug("checking %s path %s", contentType, fPath)
            if fPath:
                if os.access(fPath, os.R_OK):
                    return fPath
                else:
                    if createAsNeeded:
                        try:
                            f = open(fPath, "w")
                            if os.access(fPath, os.R_OK):
                                f.close()
                                return fPath
                        except IOError:
                            logger.exception("Unable to create '%s' file for id [%s]", contentType, self.__identifier)
                    else:
                        return None
            else:
                return None
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("Failed to getWfFilePath")
            return None

    def __getWfFilePathRef(self, contentType, fmt="pdbx", fileSource="archive", version="latest", partitionNum=None):
        """Return the path to the latest version of the contentType"""

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
        # Added by ZF
        #
        if self.__groupId and contentType in ["messages-from-depositor", "messages-to-depositor", "notes-from-annotator"]:
            dfRef.setDepositionDataSetId(self.__groupId)
            dfRef.setStorageType("autogroup")
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
    di = MessagingDataImport()
