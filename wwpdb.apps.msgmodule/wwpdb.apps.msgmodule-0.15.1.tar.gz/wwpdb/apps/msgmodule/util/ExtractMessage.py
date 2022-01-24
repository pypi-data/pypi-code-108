##
# File:  ExtractMessage.py
# Date:  28-Jun-2019 E. Peisach
#
# Update:
"""
Support for automatic extracting information from send messages


"""
__docformat__ = "restructuredtext en"
__author__ = "Ezra Peisach"
__email__ = "peisach@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"

import os
import sys
import datetime
import logging
import re
from mmcif.io.PdbxReader import PdbxReader
from wwpdb.io.locator.PathInfo import PathInfo

#

logger = logging.getLogger(__name__)


class ExtractMessage(object):
    def __init__(self, siteId=None, verbose=False, log=sys.stderr):
        self.__siteId = siteId
        self.__verbose = verbose
        self.__log = log
        self.__pI = PathInfo(siteId=self.__siteId, verbose=self.__verbose, log=self.__log)

    def getLastUnlocked(self, depid):
        """Returns datetime of the last time an unlocked message was sent.  This is parallel to the code in
        MessagingIo.py

        If no unlock message has been sent, will return None
        """

        msgfile = self.__pI.getFilePath(depid, contentType="messages-to-depositor", formatType="pdbx", fileSource="archive", versionId="1")

        if not os.path.exists(msgfile):
            return None

        ret = None

        myContainerList = []
        ifh = open(msgfile, "r")
        pRd = PdbxReader(ifh)
        pRd.read(myContainerList)

        if len(myContainerList) >= 1:
            c0 = myContainerList[0]
            catObj = c0.getObj("pdbx_deposition_message_info")
            if catObj is None:
                logger.debug("Deposition %s no pdbx_deposition_message_info category", depid)
                return None
            else:
                #
                # Get column name index.
                #
                itDict = {}
                itNameList = catObj.getItemNameList()
                for idxIt, itName in enumerate(itNameList):
                    itDict[str(itName).lower()] = idxIt
                    #
                idxOrdinalId = itDict["_pdbx_deposition_message_info.ordinal_id"]
                idxLastCommDate = itDict["_pdbx_deposition_message_info.timestamp"]
                idxMsgSubj = itDict["_pdbx_deposition_message_info.message_subject"]

                maxUnlockOrdId = 0
                for row in catObj.getRowList():
                    try:
                        ordinalId = int(row[idxOrdinalId])
                        msgsubj = row[idxMsgSubj]

                        if msgsubj == "System Unlocked":
                            if ordinalId > maxUnlockOrdId:
                                maxUnlockOrdId = ordinalId
                                ret = str(row[idxLastCommDate])

                    except Exception as e:
                        logger.error("Error processing %s %s", depid, str(e))

        else:
            logger.debug("Deposition %s empty message file", depid)
            return None

        return ret

    def getLastValidation(self, depid):
        """Returns (datetime, major issue)  of the last time a validation was sent as determined by
        presence of attached validation pdf and parsing message.
        """

        logger.info("Starting for deposition %s", depid)

        msgfile = self.__pI.getFilePath(depid, contentType="messages-to-depositor", formatType="pdbx", fileSource="archive", versionId="1")

        if not os.path.exists(msgfile):
            return (None, None)

        ret = None
        major = None

        myContainerList = []
        ifh = open(msgfile, "r")
        pRd = PdbxReader(ifh)
        pRd.read(myContainerList)

        if len(myContainerList) >= 1:
            c0 = myContainerList[0]

            catObj = c0.getObj("pdbx_deposition_message_file_reference")
            if catObj is None:
                logger.debug("Deposition %s no pdbx_deposition_message_file_reference category", depid)
                return (None, None)

            # Get list of msgids of validtion report
            msgids = set()

            #
            # Get column name index.
            #
            itDict = {}
            itNameList = catObj.getItemNameList()
            for idxIt, itName in enumerate(itNameList):
                itDict[str(itName).lower()] = idxIt

            idxMsgId = itDict["_pdbx_deposition_message_file_reference.message_id"]
            idxContentType = itDict["_pdbx_deposition_message_file_reference.content_type"]

            for row in catObj.getRowList():
                try:
                    msgId = row[idxMsgId]
                    cT = row[idxContentType]

                    if "validation-report-annotate" in cT:
                        msgids.add(msgId)

                except Exception as e:
                    logger.exception("Error processing %s %s", depid, str(e))

            if len(msgids) == 0:
                return (None, None)

            logger.debug("Message ids: %s", msgids)

            # Now check messages

            catObj = c0.getObj("pdbx_deposition_message_info")
            if catObj is None:
                logger.debug("Deposition %s no pdbx_deposition_message_info category", depid)
                return (None, None)

            #
            # Get column name index.
            #
            itDict = {}
            itNameList = catObj.getItemNameList()
            for idxIt, itName in enumerate(itNameList):
                itDict[str(itName).lower()] = idxIt
            #
            idxTimeStamp = itDict["_pdbx_deposition_message_info.timestamp"]
            idxMsgId = itDict["_pdbx_deposition_message_info.message_id"]
            idxMsgText = itDict["_pdbx_deposition_message_info.message_text"]
            idxSendStatus = itDict["_pdbx_deposition_message_info.send_status"]

            lastvalid = None

            for row in catObj.getRowList():
                try:
                    timeStamp = datetime.datetime.strptime(str(row[idxTimeStamp]), "%Y-%m-%d %H:%M:%S")
                    msgId = str(row[idxMsgId])
                    status = str(row[idxSendStatus])
                    msgText = str(row[idxMsgText])

                    if status == "Y" and msgId in msgids:
                        if lastvalid:
                            if timeStamp > lastvalid:
                                # logger.debug("Updating lastvalid %s %s", lastvalid, timeStamp)
                                lastvalid = timeStamp
                                major = self._majorValidation(msgText)

                        else:
                            lastvalid = timeStamp
                            major = self._majorValidation(msgText)

                except Exception as e:
                    logger.exception("Error processing %s %s", depid, str(e))

            ret = lastvalid

        else:
            logger.debug("Deposition %s empty message file", depid)
            ret = None

        logger.info("Returning (%s, %s)", ret, major)

        return (ret, major)

    def _majorValidation(self, msgText):
        """Returns true if there appears to be a major error in the validation test - otherwise False"""

        ret = False
        if re.search("Some major issues", msgText) is not None:
            ret = True

        # logger.debug("Major validation %s", ret)
        return ret

    def getLastSentMessageDate(self, depid, msgtodepositor):
        """Returns datetime  of the ast message sent.  Will return None if no messages sent.
        msgtodepositor is boolean indicating which direction message sent
        """

        logger.info("Starting for deposition %s msgtodepositor %s", depid, msgtodepositor)

        if msgtodepositor:
            msg_content = "messages-to-depositor"
        else:
            msg_content = "messages-from-depositor"

        msgfile = self.__pI.getFilePath(depid, contentType=msg_content, formatType="pdbx", fileSource="archive", versionId="1")

        if not os.path.exists(msgfile):
            return None

        ret = None

        myContainerList = []
        ifh = open(msgfile, "r")
        pRd = PdbxReader(ifh)
        pRd.read(myContainerList)

        if len(myContainerList) >= 1:
            c0 = myContainerList[0]

            # Now check messages

            catObj = c0.getObj("pdbx_deposition_message_info")
            if catObj is None:
                logger.debug("Deposition %s no pdbx_deposition_message_info category", depid)
                return None

            #
            # Get column name index.
            #
            itDict = {}
            itNameList = catObj.getItemNameList()
            for idxIt, itName in enumerate(itNameList):
                itDict[str(itName).lower()] = idxIt
            #
            idxTimeStamp = itDict["_pdbx_deposition_message_info.timestamp"]
            idxSendStatus = itDict["_pdbx_deposition_message_info.send_status"]

            lastsent = None

            for row in catObj.getRowList():
                try:
                    timeStamp = datetime.datetime.strptime(str(row[idxTimeStamp]), "%Y-%m-%d %H:%M:%S")
                    status = str(row[idxSendStatus])

                    if status == "Y":
                        if lastsent:
                            if timeStamp > lastsent:
                                # logger.debug("Updating lastvalid %s %s", lastsent, timeStamp)
                                lastsent = timeStamp
                        else:
                            lastsent = timeStamp

                except Exception as e:
                    logger.exception("Error processing %s %s", depid, str(e))

            ret = lastsent

        else:
            logger.debug("Deposition %s empty message file", depid)
            ret = None

        logger.info("Returning %s", ret)

        return ret
