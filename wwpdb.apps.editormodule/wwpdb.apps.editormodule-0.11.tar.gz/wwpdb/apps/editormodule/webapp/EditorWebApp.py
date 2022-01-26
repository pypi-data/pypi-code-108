##
# File:  EditorWebApp.py
# Date:  02-Feb-2012
# Updates:
#
# 2012-02-02    RPS    Created.
# 2012-04-02    RPS    Updates to reflect improved handling of cases where datafile being processed does not contain data corresponding
#                      to cif category being requested for display/edit.
# 2012-04-06    RPS    Introduced support for adding new record into cif category/DataTable
# 2012-04-10    RPS    Introduced support for deleting a record.
# 2012-04-16    RPS    Introduced hook for server-side validation of user-submitted edits.
# 2012-04-17    RPS    Updates for validation of data being submitted as edits to given cif category.attribute
# 2012-04-18    RPS    Updated for more efficient use of PdbxDictionaryInfo object during validation of proposed edits.
# 2012-04-22    RPS    Introduced support for writing out edited cif data to output file as response to UI action button.
# 2012-04-26    RPS    Updates related to writing out edited cif data to output file as response to UI action button.
# 2012-04-26    RPS    Updates for improved handling of different input sources of cif file.
# 2012-05-08    RPS    _validateEditOp() updated as per updates in PdbxDataIo to incorporate validation against boundary
#                        constraints when applicable.
# 2012-06-28    RPS    Introduced support for launching of Jmol viewer relative to specific records selected via DataTable
#                        interface, such that Jmol scripting commands are customized based on cif category and row selected.
# 2012-07-30    RPS    _getDataTblData() updated to accommodate column-specific filtering
# 2012-08-16    RPS    added URL mapping in accordance with setting for 'SITE_CIF_EDITOR_URL' in wwpdb.utils.config.ConfigInfoData.py
# 2012-08-21    RPS    Update required for proper integration with WF tracking.
# 2012-09-25    RPS    Disabling communication with status database until decision is made as to how this module fits
#                        into workflow processing
# 2012-10-11    RPS    Now explicitly deriving path of directory that serves as parent to "sessions" from ConfigInfoData.
# 2012-10-18    ZF     Added subdirectory attribute to __saveEditorModState function.
# 2013-02-26    RPS    Introduced support for "undo"-ing edits.
# 2013-03-15    RPS    Support for sorting of columns when required for particular cif categories (e.g. citation authors)
# 2013-04-22    RPS    Introduced support for identifying and checking for "mandatory" cif items (i.e. items that require non-null value).
# 2013-05-17    RPS    Removed now obsolete code that had been in place for constructing "transposed view" datatables via server-side strategy.
#                        Front-end now bears primary responsibility for doing this.
# 2013-06-04    RPS    Improved handling of edit and undo requests.
# 2013-06-20    RPS    Updated to accommodate display of entry title.
# 2013-07-16    RPS    Ad hoc use of the EditorWebApp to accommodate beta testing feedback of common tool new dep system.
# 2014-02-06    RPS    __saveEditorModState() updated to correct for use of "next" instead of "latest" when determining version of file for save out
# 2014-02-24    RPS    Added support for handling requests to skip link/site/helix/sheet calculations.
# 2014-06-05    RPS    Updated with improved features for providing annotator with information regarding violation of dictionary constraints.
# 2014-07-09    RPS    Introduced changes that will eventually support "insertRow" functionality
# 2014-09-19    RPS    Changed strategy for making snapshots to support rollbacks. An initial zero-index snapshot had already been made when user
#                        action invokes first call to have datatables populated in the browser. The pre-existing zero-index snapshot serves as readily
#                        available initial rollback point, and thus allows us to make snapshots *after* any edit actions so user does not have to wait
#                        for snapshot completion for edit action roundtrip to be completed and allow user to interact with screen again.
# 2015-04-15    RPS    Introducing support for CIF Editor self-Config UI.
#                        Introducing "abort" exit method.
# 2015-04-21    RPS    Adding os.wait() to end of self.__makeDataStoreSnapShot() to prevent creation of "zombie" child processes.
# 2015-06-16    RPS    Added self.propagateTitleOp() for copying title data between "struct" and "citation" categories
# 2015-07-06    RPS    Added self._reloadOp() to support handling of EM entries (i.e. allows switching between map only and map+model views)
# 2016-03-02    RPS    Updates to accommodate handling possibility of unicode characters
# 2016-03-08    RPS    __makeDataStoreSnapShot() updated to call pdbxDataIo.purgeDataStoreSnapShots as a prerequisite to creating an initial rollback snapshot
# 2017-02-19    EP     _launchOp() store the default view - so can do without a recalc or guess.
# 2018-06-28    Ep     Add _getDataMultiTblConfigDtls() to provide configs on the whole page at once. Reduces contention from web server and retry of
#                        locks on persistant storage.
##
"""
General annotation editor tool web request and response processing modules.

This software was developed as part of the World Wide Protein Data Bank
Common Deposition and Annotation System Project

Copyright (c) 2012 wwPDB

This software is provided under a Creative Commons Attribution 3.0 Unported
License described at http://creativecommons.org/licenses/by/3.0/.

"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.07"

import base64
import logging
import mimetypes
import ntpath
import os
import smtplib
import sys
import time
import types

#
from wwpdb.io.graphics.GraphicsContext3D import GraphicsContext3D

#
from wwpdb.io.locator.DataReference import DataFileReference
from wwpdb.utils.config.ConfigInfoApp import ConfigInfoAppCommon

#
# from wwpdb.utils.wf.dbapi.WfTracking import WfTracking

from wwpdb.apps.editormodule.depict.EditorDepict import EditorDepict
from wwpdb.apps.editormodule.io.PdbxDataIo import PdbxDataIo
from wwpdb.apps.editormodule.webapp.WebRequest import EditorInputRequest, ResponseContent

# from json import loads, dumps
# from time import localtime, strftime

logger = logging.getLogger(__name__)


class EditorWebApp(object):
    """Handle request and response object processing for the general annotation editor tool application."""

    def __init__(self, parameterDict=None, verbose=False, log=sys.stderr, siteId="WWPDB_DEV"):
        """
        Create an instance of `EditorWebApp` to manage an editor web request.

         :param `parameterDict`: dictionary storing parameter information from the web request.
             Storage model for GET and POST parameter data is a dictionary of lists.
         :param `verbose`:  boolean flag to activate verbose logging.
         :param `log`:      stream for logging.

        """
        if parameterDict is None:
            parameterDict = {}
        self.__verbose = verbose
        self.__lfh = log
        self.__debug = False
        self.__siteId = siteId
        self.__cICommon = ConfigInfoAppCommon(self.__siteId)
        self.__topSessionPath = self.__cICommon.get_site_web_apps_top_sessions_path()
        self.__templatePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        #

        if isinstance(parameterDict, dict):
            self.__myParameterDict = parameterDict
        else:
            self.__myParameterDict = {}

        if self.__verbose:
            logger.info("REQUEST STARTING ------------------------------------")
            logger.info("dumping input parameter dictionary")
            logger.info("%s", "".join(self.__dumpRequest()))

        self.__reqObj = EditorInputRequest(self.__myParameterDict, verbose=self.__verbose, log=self.__lfh)
        #
        self.__reqObj.setValue("TopSessionPath", self.__topSessionPath)
        self.__reqObj.setValue("TemplatePath", self.__templatePath)
        self.__reqObj.setValue("WWPDB_SITE_ID", self.__siteId)
        os.environ["WWPDB_SITE_ID"] = self.__siteId
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        #
        if self.__verbose:
            logger.info("-----------------------------------------------------")
            logger.info("Leaving _init with request contents")
            self.__reqObj.printIt(ofh=self.__lfh)
            logger.info("---------------EditorWebApp - done -------------------------------")
            self.__lfh.flush()

    def doOp(self):
        """Execute request and package results in response dictionary.

        :Returns:
             A dictionary containing response data for the input request.
             Minimally, the content of this dictionary will include the
             keys: CONTENT_TYPE and REQUEST_STRING.
        """
        stw = EditorWebAppWorker(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        rC = stw.doOp()
        if self.__debug:
            rqp = self.__reqObj.getRequestPath()
            logger.debug("+EditorWebApp.doOp() operation %s", rqp)
            logger.debug("+EditorWebApp.doOp() return format %s", self.__reqObj.getReturnFormat())
            if rC is not None:
                logger.info("%s", ("".join(rC.dump())))
            else:
                logger.info("+EditorWebApp.doOp() return object is empty")

        #
        # Package return according to the request return_format -
        #
        return rC.get()

    def __dumpRequest(self):
        """Utility method to format the contents of the internal parameter dictionary
        containing data from the input web request.

        :Returns:
            ``list`` of formatted text lines
        """
        retL = []
        retL.append("\n-----------------EditorWebApp().__dumpRequest()-----------------------------\n")
        retL.append("Parameter dictionary length = %d\n" % len(self.__myParameterDict))
        for k, vL in self.__myParameterDict.items():
            retL.append("Parameter %30s :" % k)
            for v in vL:
                retL.append(" ->  %r\n" % v)
        retL.append("-------------------------------------------------------------\n")
        return retL


class EditorWebAppWorker(object):
    def __init__(self, reqObj=None, verbose=False, log=sys.stderr):
        """
        Worker methods for the general annotation editor application

        Performs URL - application mapping and application launching
        for general annotation editor tool.

        All operations can be driven from this interface which can
        supplied with control information from web application request
        or from a testing application.
        """
        self.__verbose = verbose
        self.__lfh = log
        self.__debug = True
        self.__reqObj = reqObj
        self.__sObj = None
        self.__sessionId = None
        self.__sessionPath = None
        self.__rltvSessionPath = None
        #
        self.__appPathD = {
            "/service/editor/environment/dump": "_dumpOp",
            "/service/editor/launch": "_launchOp",
            "/service/editor/reload": "_reloadOp",
            "/service/editor/get_dtbl_data": "_getDataTblData",
            "/service/editor/get_dtbl_config_dtls": "_getDataTblConfigDtls",
            "/service/editor/get_multi_dtbl_config_dtls": "_getDataMultiTblConfigDtls",
            "/service/editor/validate_edit": "_validateEditOp",
            "/service/editor/submit_edit": "_submitEditOp",
            "/service/editor/propagate_title": "_propagateTitleOp",
            "/service/editor/act_on_row": "_rowActionOp",
            "/service/editor/devproto": "_devproto",
            "/service/editor/test_see_json": "_getCifCategoryJsonOp",
            "/service/editor/exit_not_finished": "_exit_notFinished",
            "/service/editor/exit_finished": "_exit_finished",
            "/service/editor/exit_abort": "_exit_abort",
            "/service/editor/get_jmol_setup": "_getJmolSetup",
            "/service/editor/get_ctgries_w3dcontext": "_getCategories3Dcontext",
            "/service/editor/undo": "_undoEdits",
            "/service/editor/check_mandatory_items": "_checkForMandatoryItems",
            "/service/editor/check_dict_violations": "_checkForDictViolations",
            "/service/editor/skip_calc": "_skipCalcOp",
            "/service/editor/skip_calc_undo": "_undoSkipCalcOp",
            "/service/editor/check_skip_calc": "_checkSkipCalc",
            "/service/editor/init_rollback_point": "_createInitRollbackPoint",
            # ##############  below are URLs to be used for WFM environ######################
            "/service/editor/new_session/wf": "_launchOp",
            "/service/editor/wf/new_session": "_launchOp",
            "/service/editor/wf/test": "_wfDoSomethingOp",
            "/service/editor/wf/launch": "_wfLaunchOp",
            "/service/editor/wf/exit_not_finished": "_exit_notFinished",
            "/service/editor/wf/exit_finished": "_exit_finished",
            ###################################################################################################
            "/service/feedback": "_captureFeedback"
            # this is for capturing tester feedback for common d&a tool
        }

    def doOp(self):
        """Map operation to path and invoke operation.

        :Returns:

        Operation output is packaged in a ResponseContent() object.
        """
        return self.__doOpException()

    def __doOpNoException(self):  # pylint: disable=unused-private-member
        """Map operation to path and invoke operation.  No exception handling is performed.

        :Returns:

        Operation output is packaged in a ResponseContent() object.
        """
        #
        reqPath = self.__reqObj.getRequestPath()
        if reqPath not in self.__appPathD:
            # bail out if operation is unknown -
            rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            rC.setError(errMsg="Unknown operation")
            return rC
        else:
            mth = getattr(self, self.__appPathD[reqPath], None)
            rC = mth()
        return rC

    def __doOpException(self):
        """Map operation to path and invoke operation.  Exceptions are caught within this method.

        :Returns:

        Operation output is packaged in a ResponseContent() object.
        """
        #
        try:
            reqPath = self.__reqObj.getRequestPath()
            if reqPath not in self.__appPathD:
                # bail out if operation is unknown -
                rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
                rC.setError(errMsg="Unknown operation")
            else:
                mth = getattr(self, self.__appPathD[reqPath], None)
                rC = mth()
            return rC
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("__doOpException failure")
            rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
            rC.setError(errMsg="Operation failure")
            return rC

    ################################################################################################################
    # ------------------------------------------------------------------------------------------------------------
    #      Top-level REST methods
    # ------------------------------------------------------------------------------------------------------------
    #
    def _dumpOp(self):
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        rC.setHtmlList(self.__reqObj.dump(format="html"))
        return rC

    def _captureFeedback(self):
        self.__getSession()
        #
        senderEmail = str(self.__reqObj.getValue("sender"))
        title = str(self.__reqObj.getValue("title")) if self.__reqObj.getValue("title") is not None else ""
        fname = str(self.__reqObj.getValue("fname"))
        lname = str(self.__reqObj.getValue("lname"))
        suffix = str(self.__reqObj.getValue("suffix")) if self.__reqObj.getValue("suffix") is not None else ""
        subject = str(self.__reqObj.getValue("subject"))
        depId = str(self.__reqObj.getValue("dep_id")) if self.__reqObj.getValue("suffix") is not None else ""
        feedback = str(self.__reqObj.getValue("feedback"))
        #
        haveUploadFile = False
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        #
        if self.__isFileUpload():
            haveUploadFile = self.__uploadFeedbackFile()
            if haveUploadFile:
                uploadFlPth = self.__reqObj.getValue("filePath")
                uploadFlName = self.__reqObj.getValue("uploadFileName")
                uploadFlMimeTyp = self.__reqObj.getValue("mimeType")
                # Read the file and encode it into base64 format
                fo = open(uploadFlPth, "rb")
                fileContent = fo.read()
                encodedContent = base64.b64encode(fileContent)  # base64
        #
        msgStrDict = {}
        htmlStrDict = {}
        #
        receiver = "deposit-feedback@mail.wwpdb.org"
        # receiver = 'rsala@rcsb.rutgers.edu'
        #
        msgTmplt = """From: <%(sender)s>
To: <%(receiver)s>
Subject: %(subject)s
%(mime_hdr)s%(msg_content)s
"""
        if haveUploadFile:
            bndryDelimDef = "----174088543903"
            bndryDelim = "--" + bndryDelimDef

            mimeHdr = """MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="%s"
%s
""" % (
                bndryDelimDef,
                bndryDelim,
            )
            #
            msgBodyMimeSpec = """Content-Type: text/plain
Content-Transfer-Encoding:8bit

"""
            # Define the attachment section
            attachment = """Content-Type: %s; name=\"%s\"
Content-Transfer-Encoding:base64
Content-Disposition: attachment; filename=\"%s\"

%s
%s--
""" % (
                uploadFlMimeTyp,
                uploadFlName,
                uploadFlName,
                encodedContent,
                bndryDelim,
            )

        #
        else:
            bndryDelimDef = bndryDelim = ""
            mimeHdr = "\n"
            msgBodyMimeSpec = ""
            attachment = ""
        #

        msgBodyTmplt = """%(msg_mime_spec)sFeedback provided by: %(name)s

%(feedback)s

%(dep_id)s
%(bndry_delim)s"""
        #
        if len(suffix) > 1:
            suffix = ", " + suffix
        if len(title) > 1:
            title = title + " "
        name = title + fname + " " + lname + suffix
        if len(depId) > 1:
            depId = "Deposition Dataset ID: " + depId
        #
        msgStrDict["dep_id"] = depId
        msgStrDict["msg_mime_spec"] = msgBodyMimeSpec
        msgStrDict["name"] = name
        msgStrDict["feedback"] = feedback
        msgStrDict["bndry_delim"] = bndryDelim
        #
        msgBody = msgBodyTmplt % msgStrDict
        #
        if subject == "fileuploadsmmry":
            subject = "File Upload Summary"
        elif subject == "admin":
            subject = "Admin"
        elif subject == "macromolecule":
            subject = "Macromolecule"
        elif subject == "refinement":
            subject = "Refinement"
        elif subject == "datacollection":
            subject = "Data Collection"
        elif subject == "ligandcheck":
            subject = "Ligand Check"
        elif subject == "filedownload":
            subject = "File Download"
        elif subject == "misc":
            subject = "Miscellaneous"
        #
        subject = "Feedback: " + subject
        #
        msgStrDict["sender"] = senderEmail
        msgStrDict["receiver"] = receiver
        msgStrDict["subject"] = subject
        msgStrDict["mime_hdr"] = mimeHdr
        msgStrDict["msg_content"] = msgBody
        #
        message = msgTmplt % msgStrDict + attachment
        #
        try:
            smtpObj = smtplib.SMTP("localhost")
            smtpObj.sendmail(senderEmail, receiver, message)
            htmlStrDict["msg"] = "Feedback received. Thank you."
            #
            if self.__verbose:
                logger.info("-- Successfully generated email from %s", senderEmail)
                logger.info("- email message was %r", message)
        except smtplib.SMTPException:
            htmlStrDict["msg"] = "Error occurred when capturing feedback."
            logger.exception("Failure to send message")
            if self.__verbose:
                logger.info("-- Failed to generate email from %s", senderEmail)
        #
        rtrnHtmlTmplt = """<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>wwPDB New Deposition System</title>
<link href="http://deposit-feedback.wwpdb.org/assets/styles/bootstrap.min.css" rel="stylesheet" type="text/css" media="screen" />
<link rel="stylesheet" type="text/css" media="all" href="http://deposit-feedback.wwpdb.org/assets/styles/wwpdb_feedback.css" />
</head>
<body class="oneColLiqCtrHdr">

    <div id="header">
        <div id="logo"><img src="/images/wwpdb_logo.gif" width="187" height="58" alt="logo" /> </div>
        <div id="headerCont">
              <h3>wwPDB New Deposition System</h3>
        </div>
        <br class="clearfloat" />
    </div>
    <div style="text-align: center; font-size: large; width: 45%%; margin-left: auto; margin-right: auto; margin-top: 250px;">
        %(msg)s
    </div>
<script type="text/javascript" src="/js/jquery/core/jquery.min.js"></script>
<script type="text/javascript" src="http://deposit-feedback.wwpdb.org/assets/js/bootstrap.min.js"></script>
</body>
</html>"""
        #
        rtrnHtml = rtrnHtmlTmplt % htmlStrDict
        rC.setHtmlText(rtrnHtml)
        #
        return rC

    def _launchOp(self):
        """Launch general annotation editor module interface

        :Helpers:
            wwpdb.apps.editormodule.depict.EditorDepict

        :Returns:
            Operation output is packaged in a ResponseContent() object.
            The output consists of a HTML starter container page for quicker return to the client.
            This container page is then populated with content via AJAX calls.
        """
        if self.__debug:
            logger.debug("+++++++++++++++++++++ Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        # determine if currently operating in Workflow Managed environment
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        #
        dataFile = str(self.__reqObj.getValue("datafile"))
        fileSource = str(self.__reqObj.getValue("filesource")).strip().lower()
        #
        if self.__verbose:
            logger.info("-- datafile is:%s", dataFile)
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        if self.__verbose:
            logger.info("+EditorWebAppWorker._launchOp() workflow flag is %r", bIsWorkflow)

        if bIsWorkflow:
            # Update WF status database --
            pass
            # """
            # bSuccess = self.__updateWfTrackingDb("open")
            # if( not bSuccess ):
            #     rC.setError(errMsg="+EditorWebAppWorker._launchOp() - TRACKING status, update to 'open' failed for session %s \n" % self.__sessionId )
            # else:
            #     if self.__verbose:
            #         logger.info("+EditorWebAppWorker._launchOp() Tracking status set to open")
            # """
        else:
            if fileSource and fileSource == "rcsb_dev":
                pass
            elif fileSource and fileSource == "upload":
                if not self.__isFileUpload("cifinput"):
                    rC.setError(errMsg="No file uploaded")
                    return rC
                #
                bSuccess, sFileName, sFileAbsPath = self.__uploadFile("cifinput")

                if bSuccess:
                    self.__reqObj.setValue("datafile", sFileName)
                    self.__reqObj.setValue("filePath", sFileAbsPath)

                    fName = sFileName.strip()
                    if fName.lower().startswith("rcsb"):
                        fId = fName.lower()[:10]
                    elif fName.lower().startswith("d_"):
                        fId = fName[:12]
                    else:
                        fId = "000000"
                        if self.__verbose:
                            logger.info("+EditorWebApp._launchOp() using default identifier for %s", str(sFileName))

                    self.__reqObj.setValue("identifier", fId)
                    #
                    if self.__verbose:
                        logger.info("+EditorWebApp._launchOp() identifier %s", self.__reqObj.getValue("identifier"))

                    if self.__isFileUpload("configfile"):
                        bSuccessCnfg, _sFileNameCnfg, sFileAbsPathCnfg = self.__uploadFile("configfile")

                        if bSuccessCnfg:
                            self.__reqObj.setValue("configFilePath", sFileAbsPathCnfg)

        #
        # instantiate datastore to be used for capturing/persisting edits
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)
        if self.__debug:
            logger.debug("+++++++++++++++++++++ before call to pdbxDataIo.initializeDataStore at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        dataBlockName, entryTitle, entryAccessionIdsLst = pdbxDataIo.initializeDataStore()
        if self.__debug:
            logger.debug("+++++++++++++++++++++ after call to pdbxDataIo.initializeDataStore at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

        # instantiate dictionary info store to be used for retrieving cif category meta data
        if self.__debug:
            logger.debug("+++++++++++++++++++++ before call to pdbxDataIo.initializeDictInfoStore at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        pdbxDataIo.initializeDictInfoStore()
        if self.__debug:
            logger.debug("+++++++++++++++++++++ after call to pdbxDataIo.initializeDictInfoStore at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

        defView = pdbxDataIo.getDefView()
        if self.__debug:
            logger.debug("+++++++++++++++++++++ defView is %s", defView)

        #
        if self.__verbose:
            logger.info("+EditorWebAppWorker._launchOp() Call EditorDepict with workflow %r", bIsWorkflow)
        #
        self.__reqObj.setValue("entrytitle", entryTitle)
        self.__reqObj.setValue("datablockname", dataBlockName)
        #
        if self.__verbose:
            logger.info("+EditorWebAppWorker._launchOp() Call EditorDepict with defView %r", defView)

        if defView:
            self.__reqObj.setValue("defview", defView)

        #
        # Legacy entries will not have requested accession id list - those are models
        if (len(entryAccessionIdsLst) == 0) or (entryAccessionIdsLst and "PDB" in entryAccessionIdsLst):
            self.__reqObj.setValue("emmodelview", "y")
        #
        edtrDpct = EditorDepict(self.__verbose, self.__lfh)
        edtrDpct.setSessionPaths(self.__reqObj)
        oL = edtrDpct.doRender(self.__reqObj, bIsWorkflow)
        rC.setHtmlText("\n".join(oL))
        #
        return rC

    def _reloadOp(self):
        """Reload general annotation editor module interface

        :Helpers:
            wwpdb.apps.editormodule.depict.EditorDepict

        :Returns:
            Operation output is packaged in a ResponseContent() object.
            The output consists of a HTML starter container page for quicker return to the client.
            This container page is then populated with content via AJAX calls.
        """
        if self.__debug:
            logger.debug("+++++++++++++++++++++ Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        # determine if currently operating in Workflow Managed environment
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        #
        dataFile = str(self.__reqObj.getValue("datafile"))
        #
        if self.__verbose:
            logger.info("-- datafile is:%s", dataFile)
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        if self.__verbose:
            logger.info("+EditorWebAppWorker._reloadOp() workflow flag is %r", bIsWorkflow)

        #
        if self.__verbose:
            logger.info("+EditorWebAppWorker._reloadOp() Call EditorDepict with workflow %r", bIsWorkflow)
        #
        edtrDpct = EditorDepict(self.__verbose, self.__lfh)
        edtrDpct.setSessionPaths(self.__reqObj)
        oL = edtrDpct.doRender(self.__reqObj, bIsWorkflow)
        rC.setHtmlText("\n".join(oL))
        #
        return rC

    def _devproto(self):
        """FOR DEV PROTOTYPING OF WEB PAGE UI"""
        if self.__verbose:
            logger.info("+EditorWebAppWorker._devproto() Starting now")
        # determine if currently operating in Workflow Managed environment
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        #
        dataFile = str(self.__reqObj.getValue("datafile"))
        if self.__verbose:
            logger.info("-- datafile is:%s", dataFile)
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        if self.__verbose:
            logger.info("+EditorWebAppWorker._devproto() workflow flag is %r", bIsWorkflow)

        # if bIsWorkflow:
        #     # Update WF status database --
        #     """
        #     bSuccess = self.__updateWfTrackingDb("open")
        #     if( not bSuccess ):
        #         rC.setError(errMsg="+EditorWebAppWorker._devproto() - TRACKING status, update to 'open' failed for session %s \n" % self.__sessionId )
        #     else:
        #         if self.__verbose:
        #             logger.info("+EditorWebAppWorker._devproto() Tracking status set to open")
        #     """
        # else:
        #     """
        #     if not self.__isFileUpload():
        #         rC.setError(errMsg='No file uploaded')
        #         return rC
        #     #
        #     self.__uploadFile()
        #     """
        #
        if self.__verbose:
            logger.info("+EditorWebAppWorker._devproto() Call EditorDepict with workflow %r", bIsWorkflow)
        #
        # instantiate datastore to be used for capturing/persisting edits
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)
        dataBlockName, _entryTitle, _entryAccessionIdsLst = pdbxDataIo.initializeDataStore()
        pdbxDataIo.initializeDictInfoStore()
        #
        edtrDpct = EditorDepict(self.__verbose, self.__lfh)
        edtrDpct.setSessionPaths(self.__reqObj)
        oL = edtrDpct.doRenderDevProto(self.__reqObj, bIsWorkflow, dataBlockName)
        rC.setHtmlText("\n".join(oL))
        #
        return rC

    def _checkForMandatoryItems(self):

        #
        if self.__verbose:
            logger.info("Starting.")
            #
        self.__getSession()
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)
        #
        rtrnRslts = pdbxDataIo.checkForMandatoryItems()

        if self.__debug:
            logger.debug("-- rtrnDict of missing mandatory items is: %r", rtrnRslts)
        # jsonDict['results'] = rtrnRslts

        if self.__verbose:
            logger.info("-- rtrnRslts is: %s", rtrnRslts)

        rC.addDictionaryItems(rtrnRslts)

        return rC

    def _checkForDictViolations(self):

        #
        if self.__verbose:
            logger.info("Starting.")
            #
        self.__getSession()
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)
        #
        rtrnRslts = pdbxDataIo.checkForDictViolations()

        if self.__debug:
            logger.debug("rtrnDict of dictionary violations is: %r", rtrnRslts)
        # jsonDict['results'] = rtrnRslts

        if self.__verbose:
            logger.info("rtrnRslts is: %s", rtrnRslts)

        rC.addDictionaryItems(rtrnRslts)

        return rC

    def _getCategories3Dcontext(self):
        """

        :Helpers:
            wwpdb.utils.rcsb.GraphicsContext3D

        :Returns:
            Operation output is packaged in a ResponseContent() object.
            The output consists of dictionary (to be converted to JSON object)
            which has 'categories' key/property whose value is a comma separated string
            of identifiers corresponding to names of cif categories having special 3D graphics contexts

        """
        #
        rtrnDict = {}
        ctgryLst = []
        #
        if self.__verbose:
            logger.info("-- Starting.")
            #
        self.__getSession()
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        gC = GraphicsContext3D(app3D="JMol", verbose=self.__verbose, log=self.__lfh)
        ctgryLst = gC.getCategoriesWithContext()
        #
        rtrnDict["categories"] = ",".join(ctgryLst)

        if self.__verbose:
            logger.info("-- rtrnDict['categories'] is: %s", rtrnDict["categories"])

        rC.addDictionaryItems(rtrnDict)

        return rC

    def _getJmolSetup(self):
        """

        :Helpers:
            wwpdb.apps.editormodule.depict.EditorDepict

        :Returns:
            Operation output is packaged in a ResponseContent() object.
            The output consists of JSON object with property(ies):
                'htmlmrkup' --> markup representing Jmol object element
        """
        #
        rtrnDict = {}
        #
        if self.__verbose:
            logger.info("-- Starting.")
            #
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        self.__reqObj.setValue("RelativeSessionPath", self.__rltvSessionPath)
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        edtrDpct = EditorDepict(verbose=self.__verbose, log=self.__lfh)
        jmolMrkp = edtrDpct.getJmolMarkup(self.__reqObj, bIsWorkflow)

        rtrnDict["htmlmrkup"] = "".join(jmolMrkp)

        if self.__verbose:
            logger.info("rtrnDict['htmlmrkup'] is:%s", rtrnDict["htmlmrkup"])

        rC.addDictionaryItems(rtrnDict)

        return rC

    def _getDataTblConfigDtls(self):
        """Get config details for staging display of given cif category/datatable in webpage.
        Data returned includes HTML <table> starter template for displaying given cif category
        and various settings for column, cell specific display details, validation behavior, etc.

        :Helpers:
            wwpdb.apps.editormodule.depict.EditorDepict

        :Returns:
            Operation output is packaged in a ResponseContent() object.
            The output consists of JSON object which has two primary properties:
                'html' --> <table> template representing the category with column headers for
                            each attribute defined for the category and conforming to structure
                            expected by jQuery DataTables plugin
                'ctgry_dict' --> multi-layered dictionary of display/validation settings to be used
                                 for configuring the behavior of the DataTable
        """
        start = time.time()
        #
        rtrnDict = {}
        catObjDict = {}
        #
        if self.__verbose:
            logger.info("Starting")

        self.__getSession()

        cifCtgry = self.__reqObj.getValue("cifctgry")
        if self.__verbose:
            logger.debug("  cifctgry is:%s", cifCtgry)

        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        edtrDpct = EditorDepict(verbose=self.__verbose, log=self.__lfh)
        dataTblTmplt, catObjDict = edtrDpct.getDataTableTemplate(self.__reqObj, cifCtgry)
        # dataTblTmplt = edtrDpct.getDataTableTemplate( cifCtgry, ctgryColList, bTrnspsdTbl, catObjDict['col_displ_name'] )  # example of supporting user friendly column display names

        rtrnDict["html"] = "".join(dataTblTmplt)

        # stuff Category Dict into return dictionary for return to web page
        rtrnDict["ctgry_dict"] = catObjDict

        rC.addDictionaryItems(rtrnDict)

        end = time.time()
        if self.__verbose:
            logger.info("Done -- in %s ms", ((end - start) * 1000))

        return rC

    def _getDataMultiTblConfigDtls(self):
        """Get config details for multiple display itemsof given cif category/datatable in webpage.
        Data returned includes HTML <table> starter template for displaying given cif category
        and various settings for column, cell specific display details, validation behavior, etc.

        :Helpers:
            wwpdb.apps.editormodule.depict.EditorDepict

        :Returns:
            Operation output is packaged in a ResponseContent() object.
            The output consists of JSON object which has a list of dictionary with two primary properties:
                'html' --> Dictionary keyed by cif catgegory of <table> template representing the category
                            with column headers for each attribute defined for the category and conforming to structure
                            expected by jQuery DataTables plugin
                'ctgry_dict' --> multi-layered dictionary of display/validation settings to be used
                                 for configuring the behavior of the DataTable
        """
        start = time.time()
        #
        rtrnDict = {}
        #
        if self.__verbose:
            logger.info("Starting")

        self.__getSession()

        cifCtgries = self.__reqObj.getValue("cifctgry")
        dispLabels = self.__reqObj.getValue("displabels").split(",")

        logger.debug("dispLabels is %s", dispLabels)

        self.__reqObj.setReturnFormat(return_format="json")

        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        htmlDict = {}
        ctgryDict = {}
        cifCtgrySplit = cifCtgries.split("+")
        for i in range(len(cifCtgrySplit)):
            cifCtgry = cifCtgrySplit[i]

            if self.__verbose:
                logger.debug("  cifctgry is:%s", cifCtgry)

            edtrDpct = EditorDepict(verbose=self.__verbose, log=self.__lfh)
            dataTblTmplt, catObjDict = edtrDpct.getDataTableTemplate(self.__reqObj, cifCtgry, dispLabels[i])

            htmlDict[cifCtgry] = "".join(dataTblTmplt)
            ctgryDict[cifCtgry] = catObjDict

        # stuff Category Dict into return dictionary for return to web page
        rtrnDict["html"] = htmlDict
        rtrnDict["ctgry_dict"] = ctgryDict
        rC.addDictionaryItems(rtrnDict)

        end = time.time()
        if self.__verbose:
            logger.info("Done -- in %s ms", ((end - start) * 1000))

        return rC

    def _createInitRollbackPoint(self):
        """ """
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        self.__getSession()

        # let's create initial snapshot copy of cif content database, so that we can "undo" the currently targeted edit if desired
        self.__makeDataStoreSnapShot(0)
        rtrnDict = {}
        rtrnDict["status"] = "OK"

        rC.addDictionaryItems(rtrnDict)

        return rC

    def _getDataTblData(self):
        """Get data needed to populate DataTable for displaying given cif category

        :Helpers:
            wwpdb.apps.editormodule.depict.EditorDepict
            wwpdb.apps.editormodule.io.PdbxDataIo

        :Returns:
            Operation output is packaged in a ResponseContent() object.
            The output consists of a JSON object representing the category/items
            and conforming to structure expected by jQuery DataTables plugin for rendering
        """
        start = time.time()
        logger.info("Starting")
        #
        self.__getSession()
        iDisplayStart = int(self.__reqObj.getValue("iDisplayStart"))
        iDisplayLength = int(self.__reqObj.getValue("iDisplayLength"))
        sEcho = int(self.__reqObj.getValue("sEcho"))  # casting to int as recommended by DataTables
        sSearch = self.__reqObj.getValue("sSearch")

        cifCtgry = self.__reqObj.getValue("cifctgry")
        #
        if self.__verbose:
            logger.debug("-- cifctgry is:%s", cifCtgry)
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)
        #
        _bOk, ctgryColList = pdbxDataIo.getCategoryColList(cifCtgry)
        # ############# in below block we are accommodating any requests for column-specific search filtering ###################################
        numColumns = len(ctgryColList)
        colSearchDict = {}
        for n in range(0, numColumns):
            qryStrParam = "sSearch_" + str(n)
            qryBoolParam = "bSearchable_" + str(n)

            bIsColSearchable = self.__reqObj.getValue(qryBoolParam) == "true"
            if bIsColSearchable:
                srchString = self.__reqObj.getValue(qryStrParam)
                if srchString and len(srchString) > 0:
                    colSearchDict[n] = srchString
                    if self.__verbose and self.__debug:
                        logger.info("-- search term for field[%s] is: %s", n, colSearchDict[n])
        ########################################################################################################################################
        ctgryRecordList, iTotalRecords, iTotalDisplayRecords = pdbxDataIo.getCategoryRowList(cifCtgry, iDisplayStart, iDisplayLength, sSearch, colSearchDict)
        #
        # if (self.__verbose and self.__debug ):
        #    logger.debug("-- ctgryRecordList returned from PdbxDataIo is: %r\n" % ctgryRecordList)
        edtrDpct = EditorDepict(verbose=self.__verbose, log=self.__lfh)
        dataTblDict = edtrDpct.getJsonDataTable(self.__reqObj, ctgryRecordList, iDisplayStart, ctgryColList)
        dataTblDict["sEcho"] = sEcho
        dataTblDict["iTotalRecords"] = iTotalRecords
        dataTblDict["iTotalDisplayRecords"] = iTotalDisplayRecords
        #
        rC.addDictionaryItems(dataTblDict)

        end = time.time()
        logger.info("Done -- in %s ms", ((end - start) * 1000))
        return rC

    def _getCifCategoryJsonOp(self):
        """for DEV -- return cif category to be displayed on webpage as JSON object for inspection"""

        if self.__verbose:
            logger.info("+EditorWebAppWorker._getCifCategoryJsonOp() starting")

        self.__getSession()
        # iDisplayStart = int( self.__reqObj.getValue("iDisplayStart") )
        # iDisplayLength = int( self.__reqObj.getValue("iDisplayLength") )
        # sEcho = int( self.__reqObj.getValue("sEcho") ) # casting to int as recommended by DataTables
        sEcho = 10

        cifCtgry = self.__reqObj.getValue("cifctgry")
        self.__reqObj.setDefaultReturnFormat(return_format="html")

        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)

        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)
        _bOk, ctgryColList = pdbxDataIo.getCategoryColList(cifCtgry)
        ctgryRecordList, iTotalRecords, iTotalDisplayRecords = pdbxDataIo.getCategoryRowList(cifCtgry, 0, 20, "", {})

        edtrDpct = EditorDepict(verbose=self.__verbose, log=self.__lfh)
        dataTblDict = edtrDpct.getJsonDataTable(self.__reqObj, ctgryRecordList, 0, ctgryColList)
        dataTblDict["sEcho"] = sEcho
        dataTblDict["iTotalRecords"] = iTotalRecords
        dataTblDict["iTotalDisplayRecords"] = iTotalDisplayRecords

        rC.setHtmlText(str(dataTblDict))

        return rC

    def _validateEditOp(self):
        #
        if self.__debug:
            logger.debug("++++++++++++STARTING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        rtrnDict = {}
        #
        self.__getSession()
        newValue = self.__reqObj.getRawValue("new_value")
        cifCtgry = self.__reqObj.getValue("cifctgry")
        rowIdx = self.__reqObj.getValue("row_idx")
        colIdx = int(self.__reqObj.getValue("col_idx"))
        #
        if self.__verbose:
            logger.info("cifctgry is:'%s', rowIdx is:'%s', colIdx is:'%s', and newValue is:'%r'", cifCtgry, rowIdx, colIdx, newValue)
        #
        self.__reqObj.setReturnFormat(return_format="json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        # INVOKE VALIDATION METHOD
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)
        if self.__debug:
            logger.debug("++++++++++++ just before call to pdbxDataIo.validateItemValue at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        rtrnDict = pdbxDataIo.validateItemValue(cifCtgry, newValue, rowIdx, colIdx)
        #
        if self.__debug:
            logger.debug("++++++++++++ just after call to pdbxDataIo.validateItemValue at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        rC.addDictionaryItems(rtrnDict)

        return rC

    def _submitEditOp(self):
        #
        if self.__debug:
            logger.debug("++++++++++++STARTING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        self.__getSession()
        newValue = self.__reqObj.getRawValue("new_value")
        newMultiValue = "; ".join(self.__reqObj.getValueList("new_value[]"))
        cifCtgry = self.__reqObj.getValue("cifctgry")
        rowIdx = self.__reqObj.getValue("row_idx")
        colIdx = int(self.__reqObj.getValue("col_idx"))
        #
        editActnIndx = int(self.__reqObj.getValue("edit_actn_indx"))
        #
        if self.__verbose:
            logger.info("cifctgry is:%s", cifCtgry)
            logger.info("editActnIndx is:%s", editActnIndx)
        #
        self.__reqObj.setDefaultReturnFormat(return_format="html")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        rowIdx = int(rowIdx.replace("row_", ""))
        #
        if self.__verbose:
            logger.info("rowIdx is now: %d", rowIdx)
        #
        if newMultiValue:
            try:
                newMultiValue.encode("ascii")
                # ASCII
                newValue = newMultiValue
            except UnicodeEncodeError:
                # Unicode
                newValue = self.__encodeUtf8ToCif(newMultiValue)
        #
        rtrnValue = None
        #
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)

        if self.__debug:
            logger.debug("++++++++++++ just before call to pdbxDataIo.setItemValue at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            self.__lfh.flush()
            #
        bOk = pdbxDataIo.setItemValue(cifCtgry, newValue, rowIdx, colIdx)
        #
        if self.__debug:
            logger.debug("++++++++++++just after call to pdbxDataIo.setItemValue at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            self.__lfh.flush()

        if bOk:
            rtrnValue = newValue
            # 2014-09-22 decided to change strategy for making snapshots to support rollbacks.
            # at point in time of this method, an initial zero-index snapshot had already been made when user action invokes first call to
            # have datatables populated in the browser. So we now make snapshots after the edit action so user does not have to wait for
            # snapshot completion for edit action roundtrip to be completed and allow user to interact with screen again.
            self.__makeDataStoreSnapShot(editActnIndx + 1)

        else:
            rtrnValue = "ERROR UPDATING VALUE"

        if self.__debug:
            logger.debug("type(newValue) is: %s", type(newValue))

        # Convert if not ASCII
        try:
            newValue.encode("ascii")
            # Ascii - do nothing
        except UnicodeEncodeError:
            newValue = self.__encodeUtf8ToCif(newValue)

        rtrnValue = newValue

        rC.setHtmlText(rtrnValue)
        #
        if self.__debug:
            logger.debug("++++++++++++COMPLETING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        return rC

    def _propagateTitleOp(self):
        #
        if self.__debug:
            logger.debug("++++++++++++STARTING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        #
        rtrnDict = {}
        #
        self.__getSession()
        targetCifCtgry = self.__reqObj.getValue("cifctgry")
        #
        editActnIndx = int(self.__reqObj.getValue("edit_actn_indx"))
        #
        if self.__verbose:
            logger.info("-- source cifctgry is:%s", targetCifCtgry)
            logger.info("-- editActnIndx is:%s", editActnIndx)
        #
        self.__reqObj.setReturnFormat("json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)
        #
        bOk, origValue = pdbxDataIo.propagateTitle(targetCifCtgry)
        #
        if self.__debug:
            logger.debug("++++++++++++ just after call to pdbxDataIo.setItemValue at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            self.__lfh.flush()

        if bOk:
            rtrnDict["status"] = "OK"
            rtrnDict["orig_value"] = origValue
            # 2014-09-22 decided to change strategy for making snapshots to support rollbacks.
            # at point in time of this method, an initial zero-index snapshot had already been made when user action invokes first call to
            # have datatables populated in the browser. So we now make snapshots after the edit action so user does not have to wait for
            # snapshot completion for edit action roundtrip to be completed and allow user to interact with screen again.
            self.__makeDataStoreSnapShot(editActnIndx + 1)

        else:
            rtrnDict["status"] = "ERROR"

        rC.addDictionaryItems(rtrnDict)
        #
        if self.__debug:
            logger.debug("++++++++++++COMPLETING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        return rC

    def _rowActionOp(self):
        #
        rtrnDict = {}
        #
        if self.__debug:
            logger.debug("++++++++++++STARTING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        #
        cloneList = None
        self.__getSession()
        context = self.__reqObj.getValue("context")
        cifCtgry = self.__reqObj.getValue("cifctgry")
        action = self.__reqObj.getValue("action")
        editActnIndx = int(self.__reqObj.getValue("edit_actn_indx"))
        cloneItems = self.__reqObj.getValue("clone_items")
        #
        if self.__verbose:
            logger.info("-- cifctgry is:%s", cifCtgry)
            logger.info("-- editActnIndx is:%s", editActnIndx)
            logger.info("-- action is:%s", action)
            #
        if action == "delrow" or action == "insert":
            rowIdx = self.__reqObj.getValue("row_idx")
            numRows = int(self.__reqObj.getValue("num_rows")) if self.__reqObj.getValue("num_rows") else None
            logger.info(" -- rowIdx is:%s", rowIdx)
            rowIdx = int(rowIdx.replace("row_", ""))  # remove prefix so that can be used by PdbxDataIo

            if context == "editorconfig" and action == "insert":
                cloneList = cloneItems.split(":")

        #
        self.__reqObj.setReturnFormat("json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)

        #
        sErrMsg = "Problem when submitting request."
        if action == "delrow":
            ok, sErrMsg = pdbxDataIo.deleteRows(cifCtgry, rowIdx, numRows)
        elif action == "insert":
            ok = pdbxDataIo.insertRows(p_ctgryNm=cifCtgry, p_rowIdx=rowIdx, p_relativePos="after", p_cloneList=cloneList, p_iNumRows=numRows)
        else:
            ok = pdbxDataIo.addNewRow(cifCtgry)
        #
        if ok:
            rtrnDict["status"] = "OK"
            # 2014-09-22 decided to change strategy for making snapshots to support rollbacks.
            # at point in time of this method, an initial zero-index snapshot had already been made when user action invokes first call to
            # have datatables populated in the browser. So we now make snapshots after the edit action so user does not have to wait for
            # snapshot completion for edit action roundtrip to be completed and allow user to interact with screen again.
            self.__makeDataStoreSnapShot(editActnIndx + 1)
        else:
            rtrnDict["status"] = "ERROR"
            rtrnDict["err_msg"] = sErrMsg
        #
        rC.addDictionaryItems(rtrnDict)
        #
        if self.__debug:
            logger.debug("++++++++++++COMPLETING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        return rC

    def _skipCalcOp(self):
        return self._updateSkipCalc("skip")

    def _undoSkipCalcOp(self):
        return self._updateSkipCalc("undo")

    def _updateSkipCalc(self, action):
        #
        rtrnDict = {}
        #
        if self.__debug:
            logger.debug("++++++++++++STARTING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        #
        self.__getSession()
        task = self.__reqObj.getValue("task")
        #
        if self.__verbose:
            logger.info("-- task is:%s", task)
            logger.info("-- action is:%s", action)
            #
        self.__reqObj.setReturnFormat("json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)
        #
        ok = pdbxDataIo.rmSkipCalcRequest(task) if (action == "undo") else pdbxDataIo.addSkipCalcRequest(task)
        #
        if ok:
            rtrnDict["status"] = "OK"
        else:
            rtrnDict["status"] = "ERROR"
        #
        rC.addDictionaryItems(rtrnDict)
        #
        if self.__debug:
            logger.debug("++++++++++++COMPLETING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        return rC

    def _checkSkipCalc(self):
        #
        rtrnDict = {}
        #
        if self.__debug:
            logger.debug("++++++++++++STARTING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        #
        self.__getSession()
        task = self.__reqObj.getValue("task")
        #
        if self.__verbose:
            logger.info("task is:%s", task)
        #
        self.__reqObj.setReturnFormat("json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)
        #
        skipRequested = pdbxDataIo.checkSkipCalcRequest(task)
        #
        if skipRequested is True:
            rtrnDict["status"] = "y"
        else:
            rtrnDict["status"] = "n"
        #
        rC.addDictionaryItems(rtrnDict)
        #
        if self.__debug:
            logger.debug("++++++++++++COMPLETING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        return rC

    def _undoEdits(self):
        #
        rtrnDict = {}
        #
        if self.__debug:
            logger.debug("++++++++++++STARTING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        #
        self.__getSession()
        undoMode = self.__reqObj.getValue("mode")
        cifCtgry = self.__reqObj.getValue("cifctgry")
        rewindIndex = int(self.__reqObj.getValue("rewind_idx"))
        #
        if self.__verbose:
            logger.info("undoMode is:%s", undoMode)
            logger.info("cifCtgry is:%s", cifCtgry)
            logger.info("rewindIndex is:%s", rewindIndex)
        #
        self.__reqObj.setReturnFormat("json")
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)
        if self.__debug:
            logger.debug("++++++++++++ just before call to pdbxDataIo._undoEdits at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        ok = pdbxDataIo.undoEdits(cifCtgry, rewindIndex)
        #
        if self.__debug:
            logger.debug("++++++++++++ just after call to pdbxDataIo._undoEdits at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        if ok:
            rtrnDict["status"] = "OK"
        else:
            rtrnDict["status"] = "ERROR"
        #
        rC.addDictionaryItems(rtrnDict)
        #
        if self.__debug:
            logger.debug("++++++++++++COMPLETING at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        return rC

    def _exit_finished(self):
        """Exiting General Annotation Editor Module when annotator has completed all necessary processing"""
        return self.__exitEditorMod(mode="completed")

    def _exit_notFinished(self):
        """Exiting General Annotation Editor Module when annotator has NOT completed all necessary processing
        and user intends to resume use of lig module at another point to continue updating data.
        """
        return self.__exitEditorMod(mode="unfinished")

    def _exit_abort(self):
        return self.__exitEditorMod(mode="abort")

    ################################################################################################################
    # ------------------------------------------------------------------------------------------------------------
    #      Private helper methods
    # ------------------------------------------------------------------------------------------------------------
    #
    def __encodeUtf8ToCif(self, p_content):
        """Encoding unicode/utf-8 content into cif friendly ascii"""
        text = p_content.encode("ascii", "xmlcharrefreplace")
        if sys.version_info[0] > 2:
            text = text.decode("ascii")
        return text

    def __makeDataStoreSnapShot(self, p_editActnIndx):
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)

        if int(p_editActnIndx) == 0:
            # 0-index means app is being asked to create initial "rollback" snapshot --> this occurs at start of each "fetch session"
            # a "fetch session" refers to duration of time that begins when user makes a nav tab selection that populates the webpage
            # with content from a group of cif categories and ends when the user decides to click on another nav tab selection for a
            # different set of cif categories to be loaded on the page, thereby launching another "fetch session"

            # we need to remove all existing snapshots if we're creating an initial rollback
            pdbxDataIo.purgeDataStoreSnapShots()

        smph = self.__setSemaphore()
        if self.__verbose:
            logger.info("Just before fork to create child process w/ separate log generated in session directory.")
            #
        pid = os.fork()
        if pid == 0:
            # if here, means we are in the child process

            sys.stdout = RedirectDevice()
            sys.stderr = RedirectDevice()
            os.setpgrp()
            os.umask(0)
            #
            # redirect the logfile
            self.__openSemaphoreLog(smph)
            sys.stdout = self.__lfh
            sys.stderr = self.__lfh
            #
            if self.__verbose:
                logger.info("Child Process: PID# %s", os.getpid())
                self.__lfh.flush()
            #
            try:
                # let's create snapshot copy of cif content database, so that we can "undo" the currently targeted edit if desired
                pdbxDataIo.makeDataStoreSnapShot(p_editActnIndx)
                self.__postSemaphore(smph, "OK")

            except:  # noqa: E722 pylint: disable=bare-except
                logger.exception("In __makeDataStoreSnapShot")
                logger.info("+Failing for child Process: PID# %s", os.getpid())
                self.__postSemaphore(smph, "FAIL")
                self.__lfh.flush()
                self.__verbose = False

            self.__verbose = False
            os._exit(0)  # pylint: disable=protected-access

        return os.wait()[0]

    def __exitEditorMod(self, mode):
        """Function to accommodate user request to exit editor module,
        close interface, and return to workflow manager interface.
        Supports different 'modes' = ('completed' | 'unfinished')

        :Params:
            ``mode``:
                'completed' if annotator has completed all edits to mmCif data and wishes to
                    conclude work in the General Annotation mmCif Editor.
                'unfinished' if annotator wishes to leave General Annotation mmCif Editor but resume work at a later point.
                'abort' if annotator wishes to leave General Annotation mmCif Editor and abort any changes made during the session.

        :Returns:
            ResponseContent object.
        """
        #
        if self.__verbose:
            logger.info("--------------------------------------------")
            logger.info("+EditorWebAppWorker.__exitEditorMod() - starting")
        #
        #
        bIsWorkflow = self.__isWorkflow()
        #
        self.__getSession()
        sessionId = self.__sessionId
        depId = self.__reqObj.getValue("identifier")
        instId = self.__reqObj.getValue("instance")
        classId = self.__reqObj.getValue("classID")
        fileSource = str(self.__reqObj.getValue("filesource")).strip().lower()
        #
        if self.__verbose:
            logger.info("--------------------------------------------")
            logger.info(" -- depId is: %s", depId)
            logger.info(" -- instId is: %s", instId)
            logger.info(" -- classId is: %s", classId)
            logger.info(" -- sessionId is: %s", sessionId)
            logger.info(" -- fileSource is: %s", fileSource)

        #
        self.__reqObj.setReturnFormat("json")
        #
        rC = ResponseContent(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
        #
        # Update WF status database and persist chem comp assignment states -- ONLY if lig module was running in context of wf-engine
        #
        if bIsWorkflow:
            try:
                if mode != "abort":
                    bOkay = self.__saveEditorModState()
                    # """
                    # if( bOkay ):
                    #     bSuccess = self.__updateWfTrackingDb(state)
                    #     if( not bSuccess ):
                    #         rC.setError(errMsg="+EditorWebAppWorker.__exitEditorMod() - TRACKING status, update to '%s' failed for session %s \n" % (state,sessionId) )
                    # else:
                    #     rC.setError(errMsg="+EditorWebAppWorker.__exitEditorMod() - problem saving cif file")
                    # """
                else:
                    if self.__verbose:
                        logger.info("-- user aborted session for depid: %s", depId)

            except:  # noqa: E722 pylint: disable=bare-except
                if self.__verbose:
                    logger.info("problem saving cif file")
                logger.exception("Exception while saving file")
                rC.setError(errMsg="+%s.%s() -- exception thrown on saving cif file\n" % ("EditorWebAppWorker", "__exitEditorMod"))

        else:
            try:
                if mode != "abort":
                    bOkay = self.__saveEditorModState()
                    if bOkay:
                        if self.__verbose:
                            logger.info("successfully saved cif file to session directory %s at %s", self.__sessionPath, time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
                    else:
                        if self.__verbose:
                            logger.info("failed to save cif file to session directory %s at %s", self.__sessionPath, time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
                        rC.setError(errMsg="+EditorWebAppWorker.__exitEditorMod() - problem saving cif file")

                else:
                    if self.__verbose:
                        logger.info("user aborted session for depid: %s", depId)

            except:  # noqa: E722 pylint: disable=bare-except
                if self.__verbose:
                    logger.info("failed to save cif file to session directory %s at %s", self.__sessionPath, time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
                logger.exception("In save cif")
                rC.setError(errMsg="+%s.%s() -- exception thrown on saving cif file" % ("EditorWebAppWorker", "__exitEditorMod"))
            # """
            # if self.__verbose:
            #         logger.info("+%s.%s() -- Not in WF environ so skipping status update to TRACKING database for session %s \n"%(className, methodName, sessionId) )
            # """
        #
        return rC

    # def __updateWfTrackingDb(self, p_status):
    #     """Private function used to udpate the Workflow Status Tracking Database

    #     :Params:
    #         ``p_status``: the new status value to which the deposition data set is being set

    #     :Helpers:
    #         wwpdb.apps.editormodule.utils.WfTracking.WfTracking

    #     :Returns:
    #         ``bSuccess``: boolean indicating success/failure of the database update
    #     """
    #     #
    #     bSuccess = False
    #     #
    #     sessionId = self.__sessionId
    #     depId = self.__reqObj.getValue("identifier").upper()
    #     instId = self.__reqObj.getValue("instance")
    #     # classId=  str(self.__reqObj.getValue("classID")).lower()
    #     classId = "View"
    #     #
    #     try:
    #         wft = WfTracking(verbose=self.__verbose, log=self.__lfh)
    #         wft.setInstanceStatus(depId=depId, instId=instId, classId=classId, status=p_status)
    #         bSuccess = True
    #         if self.__verbose:
    #             logger.info("+EditorWebAppWorker.__updateWfTrackingDb() -TRACKING status updated to '%s' for session %s \n" % (p_status, sessionId))
    #     except:  # noqa: E722 pylint: disable=bare-except
    #         bSuccess = False
    #         if self.__verbose:
    #             logger.info("+EditorWebAppWorker.__updateWfTrackingDb() - TRACKING status, update to '%s' failed for session %s \n" % (p_status, sessionId))
    #         traceback.print_exc(file=self.__lfh)
    #         #
    #     return bSuccess

    def __saveEditorModState(self):
        """PLACEHOLDER"""
        exprtDirPath = None
        exprtFilePath = None
        fileSource = str(self.__reqObj.getValue("filesource")).strip().lower()
        dataFile = str(self.__reqObj.getValue("datafile"))
        depId = self.__reqObj.getValue("identifier")
        instId = self.__reqObj.getValue("instance")
        # classId = self.__reqObj.getValue("classid")
        #
        if self.__verbose:
            logger.info("--------------------------------------------")
            logger.info("+EditorWebAppWorker.__saveEditorModState() - dataFile   %s", dataFile)
        #
        if fileSource in ["archive", "wf-archive", "wf_archive"]:
            logger.info("+EditorWebAppWorker.__saveEditorModState() - processing archive | filesource %r", fileSource)
            dfRef = DataFileReference()
            dfRef.setDepositionDataSetId(depId)
            dfRef.setStorageType("archive")
            dfRef.setContentTypeAndFormat("model", "pdbx")
            dfRef.setVersionId("next")

            if dfRef.isReferenceValid():
                exprtDirPath = dfRef.getDirPathReference()
                exprtFilePath = dfRef.getFilePathReference()
                sP = dfRef.getSitePrefix()
                if self.__verbose:
                    logger.info("+EditorWebAppWorker.__saveEditorModState() site prefix             : %s", sP)
                    logger.info("+EditorWebAppWorker.__saveEditorModState() CC assign details export directory path: %s", exprtDirPath)
                    logger.info("+EditorWebAppWorker.__saveEditorModState() CC assign details export file      path: %s", exprtFilePath)
            else:
                logger.info("+EditorWebAppWorker.__saveEditorModState() Bad archival reference for id %s", depId)

        elif fileSource in ["wf-instance", "wf_instance"]:
            logger.info("+EditorWebAppWorker.__saveEditorModState() - processing instance | filesource %r", fileSource)
            dfRef = DataFileReference()
            dfRef.setDepositionDataSetId(depId)
            dfRef.setWorkflowInstanceId(instId)
            dfRef.setStorageType("wf-instance")
            dfRef.setContentTypeAndFormat("model", "pdbx")
            dfRef.setVersionId("next")

            if dfRef.isReferenceValid():
                exprtDirPath = dfRef.getDirPathReference()
                exprtFilePath = dfRef.getFilePathReference()
                sP = dfRef.getSitePrefix()
                if self.__verbose:
                    logger.info("+EditorWebAppWorker.__saveEditorModState() site prefix             : %s", sP)
                    logger.info("+EditorWebAppWorker.__saveEditorModState() CC assign details export directory path: %s", exprtDirPath)
                    logger.info("+EditorWebAppWorker.__saveEditorModState() CC assign details export           path: %s", exprtFilePath)
            else:
                logger.info("+EditorWebAppWorker.__saveEditorModState() Bad wf-instance reference for id %s wf id %s", depId, instId)
        elif fileSource in ["rcsb_dev"]:
            logger.info("+EditorWebAppWorker.__saveEditorModState() - processing for 'rcsb_dev' filesource.")
            exprtDirPath = self.__sessionPath
            exprtFilePath = os.path.join(self.__sessionPath, "rcsb_dev_testCifFileSave.cif")
        else:
            logger.info("+EditorWebAppWorker.__saveEditorModState() - processing undefined | filesource %r", fileSource)
            exprtDirPath = self.__sessionPath
            exprtFilePath = os.path.join(self.__sessionPath, dataFile)
            subdirectory = self.__reqObj.getValue("subdirectory")
            if subdirectory and len(subdirectory) > 1 and subdirectory != "none":
                exprtDirPath = os.path.join(self.__sessionPath, subdirectory)
                exprtFilePath = os.path.join(self.__sessionPath, subdirectory, dataFile)

        # export updated mmCif file here
        # bOk = callExportFile Function
        pdbxDataIo = PdbxDataIo(self.__reqObj, self.__verbose, self.__lfh)
        bOk = pdbxDataIo.doExport(exprtDirPath, exprtFilePath)
        return bOk

    def __getSession(self):
        """Join existing session or create new session as required."""
        #
        self.__sObj = self.__reqObj.newSessionObj()
        self.__sessionId = self.__sObj.getId()
        self.__sessionPath = self.__sObj.getPath()
        self.__rltvSessionPath = self.__sObj.getRelativePath()
        if self.__verbose:
            logger.info("------------------------------------------------------")
            logger.info("+EditorWebApp.__getSession() - creating/joining session %s", self.__sessionId)
            # logger.info("+EditorWebApp.__getSession() - workflow storage path    %s\n" % self.__workflowStoragePath)
            logger.info("+EditorWebApp.__getSession() - session path %s", self.__sessionPath)
            logger.info("+EditorWebApp.__getSession() - relative session path %s", self.__rltvSessionPath)

    def __isFileUpload(self, fileTag="file"):
        """Generic check for the existence of request parameter "file"."""
        # Gracefully exit if no file is provide in the request object -
        fs = self.__reqObj.getRawValue(fileTag)
        if sys.version_info[0] < 3:
            if (fs is None) or (isinstance(fs, types.StringType)) or (isinstance(fs, types.UnicodeType)):  # pylint: disable=no-member
                return False
        else:
            if (fs is None) or (isinstance(fs, str)) or (isinstance(fs, bytes)):
                return False
        return True

    def __uploadFile(self, fileTag="file"):
        #
        #
        if self.__verbose:
            logger.info("+EditorWebApp.__uploadFile() - file upload starting")

        #
        # Copy upload file to session directory -
        try:
            fs = self.__reqObj.getRawValue(fileTag)
            # fNameInput = str(fs.filename).lower()
            fNameInput = str(fs.filename)
            #
            # Need to deal with some platform issues -
            #
            if fNameInput.find("\\") != -1:
                # likely windows path -
                fName = ntpath.basename(fNameInput)
            else:
                fName = os.path.basename(fNameInput)

            #
            if self.__verbose:
                logger.info("+EditorWebApp.__uploadFile() - upload file %s", fs.filename)
                logger.info("+EditorWebApp.__uploadFile() - base file   %s", fName)
                #
            # Store upload file in session directory -

            fPathAbs = os.path.join(self.__sessionPath, fName)
            ofh = open(fPathAbs, "wb")
            ofh.write(fs.file.read())
            ofh.close()
            if self.__verbose:
                logger.info("+EditorWebApp.__uploadFile() Uploaded file %s", str(fName))
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                logger.info("+EditorWebApp.__uploadFile() File upload processing failed for %s", str(fs.filename))
                logger.exception("File upload processing failure")

            return False

        return True, fName, fPathAbs

    def __uploadFeedbackFile(self, fileTag="file"):

        #
        #
        if self.__verbose:
            logger.info("+EditorWebApp.__uploadFeedbackFile() - file upload starting")
        # Copy upload file to session directory -
        try:
            fs = self.__reqObj.getRawValue(fileTag)
            fNameInput = str(fs.filename)
            #
            # Need to deal with some platform issues -
            #
            if fNameInput.find("\\") != -1:
                # likely windows path -
                fName = ntpath.basename(fNameInput)
            else:
                fName = os.path.basename(fNameInput)

            #
            mimeType = mimetypes.guess_type(fNameInput)[0]
            #
            if self.__verbose:
                logger.info("+EditorWebApp.__uploadFeedbackFile() - upload file %s", fs.filename)
                logger.info("+EditorWebApp.__uploadFeedbackFile() - base file   %s", fName)
                logger.info("+EditorWebApp.__uploadFeedbackFile() - mime type   %s", mimeType)
                #
            # Store upload file in session directory -

            fPathAbs = os.path.join(self.__sessionPath, fName)
            ofh = open(fPathAbs, "wb")
            ofh.write(fs.file.read())
            ofh.close()
            self.__reqObj.setValue("uploadFileName", fName)
            self.__reqObj.setValue("filePath", fPathAbs)
            self.__reqObj.setValue("mimeType", mimeType)
            if self.__verbose:
                logger.info("+EditorWebApp.__uploadFeedbackFile() Uploaded file %s", str(fName))
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                logger.info("+EditorWebApp.__uploadFeedbackFile() File upload processing failed for %s", str(fs.filename))
                logger.exception("Failure in upload feedback file")

            return False
        #
        return True

    def __setSemaphore(self):
        sVal = str(time.strftime("TMP_%Y%m%d%H%M%S", time.localtime()))
        self.__reqObj.setValue("semaphore", sVal)
        return sVal

    def __openSemaphoreLog(self, semaphore="TMP_"):
        fPathAbs = os.path.join(self.__sessionPath, semaphore + ".log")
        self.__lfh = open(fPathAbs, "w")

    def __postSemaphore(self, semaphore="TMP_", value="OK"):
        fPathAbs = os.path.join(self.__sessionPath, semaphore)
        fp = open(fPathAbs, "w")
        fp.write("%s\n" % value)
        fp.close()
        return semaphore

    def __isWorkflow(self):
        """Determine if currently operating in Workflow Managed environment

        :Returns:
            boolean indicating whether or not currently operating in Workflow Managed environment
        """
        #
        fileSource = str(self.__reqObj.getValue("filesource")).lower()
        #
        if self.__verbose:
            logger.info("+EditorWebAppWorker.__isWorkflow() - filesource is %s", fileSource)
        #
        # add wf_archive to fix PDBe wfm issue -- jdw 2011-06-30
        #
        if fileSource in ["archive", "wf-archive", "wf_archive", "wf-instance", "wf_instance"]:
            # if the file source is any of the above then we are in the workflow manager environment
            return True
        else:
            # else we are in the standalone dev environment
            return False


class RedirectDevice:
    def write(self, s):
        pass
