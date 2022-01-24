##
# File:  AutoMessage.py
# Date:  28-Jun-2019 E. Peisach
#
# Update:
"""
Support for automatic scripts to send template drive email messages and archive in normal message stream/notes


"""
__docformat__ = "restructuredtext en"
__author__ = "Ezra Peisach"
__email__ = "peisach@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"

import sys
import logging
from wwpdb.utils.config.ConfigInfo import ConfigInfo, getSiteId
from wwpdb.apps.msgmodule.io.MessagingIo import MessagingIo
from wwpdb.utils.session.WebRequest import InputRequest
from mmcif.io.IoAdapterCore import IoAdapterCore
from wwpdb.io.locator.PathInfo import PathInfo

#

logger = logging.getLogger(__name__)


class AutoMessage(object):
    def __init__(self, siteId=None, topSessionDir=None, verbose=False, log=sys.stderr):
        if siteId:
            self.__siteId = siteId
        else:
            self.__siteId = getSiteId()
        logger.debug("Site id is %s", self.__siteId)
        self.__cI = ConfigInfo(self.__siteId)
        self.__verbose = verbose
        self.__log = log

        if topSessionDir:
            self.__topSessionDir = topSessionDir
        else:
            self.__topSessionDir = self.__cI.get("SITE_WEB_APPS_TOP_SESSIONS_PATH")

    def __getmsgio(self):
        paramdict = {"TopSessionPath": [self.__topSessionDir]}
        reqobj = InputRequest(paramdict, verbose=True)
        reqobj.setValue("WWPDB_SITE_ID", self.__siteId)
        # Session dir

        mio = MessagingIo(reqobj, verbose=self.__verbose, log=self.__log)
        return mio

    def sendRemindUnlocked(self, depidlist):
        self._sendReminderBulk(depidlist, p_tmplt="remind-unlocked")

    def sendImplicitApproved(self, depidlist):
        self._sendReminderBulk(depidlist, p_tmplt="implicit-approved")

    def _sendReminderBulk(self, depidlist, p_tmplt):
        """Sends the bulk messages - handling setting EM flag"""

        (pdbents, emdents) = self._splitents(depidlist)

        mio = self.__getmsgio()
        if pdbents:
            mio.autoMsg(pdbents, p_tmpltType=p_tmplt)
        if emdents:
            mio.autoMsg(emdents, p_tmpltType=p_tmplt, p_isEmdbEntry=True)

    def _getExptl(self, depid):
        ctrgs = ["exptl"]

        ret = []
        try:
            pi = PathInfo(siteId=self.__siteId)
            modelpath = pi.getModelPdbxFilePath(dataSetId=depid, fileSource="archive")
            pr = IoAdapterCore()
            containerl = pr.readFile(inputFilePath=modelpath, selectList=ctrgs)
            if len(containerl) > 0:
                block0 = containerl[0]
                cobj = block0.getObj("exptl")
                if cobj and cobj.hasAttribute("method"):
                    for row in range(cobj.getRowCount()):
                        ret.append(cobj.getValue("method", row))
        except Exception as _e:  # noqa: F841
            logger.exception("Failed to parse model file")

        return ret

    def _splitents(self, depidlist):
        ements = []
        pdbents = []
        for depid in depidlist:
            expmeths = self._getExptl(depid)
            if "ELECTRON MICROSCOPY" in expmeths:
                ements.append(depid)
            else:
                pdbents.append(depid)
        return (pdbents, ements)
