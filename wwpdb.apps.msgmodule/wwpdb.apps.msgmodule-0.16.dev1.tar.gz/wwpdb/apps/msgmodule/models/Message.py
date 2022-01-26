##
# File:    Message.py
# Author:  R. Sala
# Date:    03-Dec-2015
# Version: 0.001 Initial version
#
# Updates:
#    03-Dec-2015    RPS    Created.
##
"""
A module to define models for different kinds of Message entities

"""
__docformat__ = "restructuredtext en"
__author__ = "Raul Sala"
__email__ = "rsala@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.001"

import sys
import logging

from wwpdb.apps.msgmodule.io.MessagingDataImport import MessagingDataImport

logger = logging.getLogger(__name__)


class Message(object):
    msgsContentType = "msgs"
    defaultMsgsToDpstrFilePath = "/net/wwpdb_da/da_top/wwpdb_da_test/source/python/pdbx_v2/message/messages-to-depositor.cif"
    defaultMsgsFrmDpstrFilePath = "/net/wwpdb_da/da_top/wwpdb_da_test/source/python/pdbx_v2/message/messages-from-depositor.cif"
    defaultNotesFilePath = "/net/wwpdb_da/da_top/wwpdb_da_test/source/python/pdbx_v2/message/notes-from-annotator.cif"

    @staticmethod
    def encodeUtf8ToCif(p_content):
        """Encoding unicode/utf-8 content into cif friendly ascii
        Have to replace any ';' that begin a newline with a ' ;' in order to preserve ; matching required for multiline items
        """
        if sys.version_info[0] < 3:
            return p_content.encode("ascii", "xmlcharrefreplace").replace("\n;", "\n ;").replace("\\\\xa0", " ")
        else:
            return p_content.encode("ascii", "xmlcharrefreplace").decode("ascii").replace("\n;", "\n ;").replace("\\\\xa0", " ")

    @staticmethod
    def fromReqObj(p_reqObj, verbose=True, log=sys.stderr):
        """Factory method that takes input requestObject and depending on the given request parameters
        creates a Message object from Message super class or one of its subclasses (Note, ReminderMessage)

        :Params:
            :param `p_reqObj`: request object
            :param `verbose`: True or False
            :param `log`: handle to file for logging output

        :Returns:
            Message object

        """
        msgDict = {}

        msgDict["deposition_data_set_id"] = p_reqObj.getValue("identifier")
        msgDict["sender"] = p_reqObj.getValue("sender")
        msgDict["message_subject"] = Message.encodeUtf8ToCif(p_reqObj.getRawValue("subject"))
        msgDict["message_text"] = Message.encodeUtf8ToCif(p_reqObj.getRawValue("message"))

        #
        msgType = p_reqObj.getValue("message_type")
        msgDict["message_type"] = msgType if msgType is not None and len(msgType) > 0 else "text"  # "archive" | "archive_manual" | "archive_flag" | "forward" | "forward_manual"

        # below two fields not currently used but may come into play in future
        msgDict["context_type"] = p_reqObj.getValue("context_type")
        msgDict["context_value"] = p_reqObj.getValue("context_value")

        sendStatus = p_reqObj.getValue("send_status")
        msgDict["send_status"] = (
            sendStatus if sendStatus else "Y"
        )  # set to "Y" or "N" for "live" vs. "draft", in all other contexts such as archive,forward,autoMsg --> this is "Y"

        # message_state is artificially introduced into p_reqObj by MessagingWebApp to distinguish "livemsg" from "draft"
        # NOTE: this field is not part of the PdbxMessage data structure, and thus is not persisted to data file.
        msgDict["message_state"] = p_reqObj.getValue("message_state")

        msgId = p_reqObj.getValue("msg_id")
        if msgDict["message_state"] == "draft" and msgId and len(msgId) > 1:
            msgDict["message_id"] = msgId

        parentMsgId = p_reqObj.getValue("parent_msg_id")  # if this msg was in response to another msg
        if msgDict["message_state"] == "livemsg" and parentMsgId and len(parentMsgId) > 1:
            msgDict["parent_message_id"] = parentMsgId

        contentType = p_reqObj.getValue("content_type")  # "notes" vs. "msgs"

        fileRefLst = p_reqObj.getValueList("msg_file_references")  # msg_file_references includes file references selected via checkboxes in UI PLUS those references that represent
        # auxiliary file uploads and which are added via processing in  MessingWebApp

        msgCategory = p_reqObj.getValue("msg_category") if p_reqObj.getValue("msg_category") is not None else ""  # in support of "reminder" category of emails

        if contentType == "notes":
            return Note(msgDict, fileRefLst, verbose, log)
        else:
            if msgCategory == "reminder":
                rtrnMsg = ReminderMessage(msgDict, fileRefLst, verbose, log)
            else:
                rtrnMsg = Message(msgDict, fileRefLst, verbose, log)

            return rtrnMsg

    def __init__(self, p_msgDict, p_fileRefLst=None, p_verbose=True, p_log=sys.stderr):
        """__init__

        :Params:
            :param `p_msgDict`: dictionary of items representing the given message entity
            :param `p_fileRefLst`: list of any file references ("attachments") associated with the message entity
            :param `p_verbose`: True or False
            :param `p_log`: handle to file for logging output

        :Returns:
            na

        """
        if p_fileRefLst is None:
            p_fileRefLst = []
        self._verbose = p_verbose
        self._lfh = p_log
        #
        self._msgDict = p_msgDict.copy()
        #
        self._bIsAutoMsg = False
        self._bIsReminderMsg = False
        # Should the MessageClass force sending of email (note)
        self._bIsNoteEmail = False
        #
        self.fileReferences = p_fileRefLst

    def getMsgDict(self):
        """Returns copy of dictionary that represents the message being processed

        :Params:
            :param na

        :Returns:
            copy of object's message dictionary

        """
        return self._msgDict.copy()

    @property
    def isLive(self):
        """Is the message actually being sent (as opposed to being just a draft at this point in time)

        :Params:
            :param na

        :Returns:
            boolean indicating whether message is live, i.e. actually being sent to depositor

        """
        return self._msgDict["message_state"] == "livemsg"
        # NOTE: this field is not part of the PdbxMessage data structure, and thus is not persisted to data file.

    @property
    def isDraft(self):
        """Is the message just a draft at this point in time

        :Params:
            :param na

        :Returns:
            boolean indicating whether message is a "draft"

        """
        return self._msgDict["message_state"] == "draft"
        # NOTE: this field is not part of the PdbxMessage data structure, and thus is not persisted to data file.

    @property
    def isAutoMsg(self):
        """Is the message one that is being automatically sent by another server-side python module (e.g. Release module)
        (i.e. as opposed to being invoked via URL request)

        :Params:
            :param na

        :Returns:
            boolean indicating whether message is a an "auto" msg

        """
        return self._bIsAutoMsg is True

    @property
    def isReminderMsg(self):
        """Is the message one that is being generated via URL request to have a reminder message propagated to depositor

        :Params:
            :param na

        :Returns:
            boolean indicating whether message is a an "reminder" msg

        """
        return self._bIsReminderMsg is True

    @property
    def contentType(self):
        """Property returning the contentType of the message
        (i.e. "msgs" vs "notes" type, which determines which datafile the message entity is persisted to)

        :Params:
            :param na

        :Returns:
            String indicating "msgs" | "notes"

        """
        return Message.msgsContentType
        # return "msgs"

    @property
    def messageSubject(self):
        """Property returning the subject line of the message

        :Params:
            :param na

        :Returns:
            String representing subject line of the message

        """
        return self._msgDict["message_subject"]

    @property
    def messageText(self):
        """Property returning the textual body of the message

        :Params:
            :param na

        :Returns:
            String representing the message's content body

        """
        return self._msgDict["message_text"]

    @property
    def messageId(self):
        """Property returning the unique ID of the message

        :Params:
            :param na

        :Returns:
            String representing the message's unique ID

        """
        return self._msgDict["message_id"]

    @messageId.setter
    def messageId(self, p_msgId):
        """Property setter allowing assignment of unique ID for the message

        :Params:
            :param p_msgId - message ID to be assigned to this message

        :Returns:
            na

        """
        self._msgDict["message_id"] = p_msgId

    @property
    def depositionId(self):
        """Property returning the ID of deposition to which the message relates

        :Params:
            :param na

        :Returns:
            String representing the ID of deposition to which the message relates

        """
        return self._msgDict["deposition_data_set_id"]

    @property
    def sendStatus(self):
        """Property returning sendStatus of the message
        i.e. "Y" | "N"  indicating whether or not the message has actually been sent or not
        will be "N" in cases where a draft is being saved or updated (and not actually sent)

        :Params:
            :param na

        :Returns:
            String representing the "Y" or "N" send status

        """
        return self._msgDict["send_status"]

    @property
    def messageType(self):
        """Property returning "type" of the message

        Can be one of the following:
            "text"               - default, conventional msg that is captured in messages data file (seen by both annotator and depositor), OR
                                   conventional note authored by annotator and captured in notes data file (seen by annotator only)
            "archive{_auto}"     - msg that is archived to notes data file via URL request (called by email server processing), does not trigger flag for annotator attention
            "archive_manual"     - msg that is archived to notes data file via manual user interaction with UI, triggers flag for annotator attention
            "archive_auto_noorig"- msg that is archived to notes via automatic server process (not by email handler), but does not contain _pdbx_deposition_message_origcomm_reference
            "archive_flag"       - msg that is archived to notes data file via URL request (called by email server processing), but needs to be flagged for annotator attention
            "forward"            - msg that is forwarded into system via URL request (called by email server processing), captured in messages data file,
                                   seen by both annotator and depositor
            "forward_manual"     - msg that is forwarded via manual user interaction with UI, captured in messages data file, seen by both annotator and depositor

        :Params:
            :param na

        :Returns:
            String representing the type of message

        """
        return self._msgDict["message_type"]

    @property
    def isBeingSent(self):
        """Property returning boolean indicating whether the message is being sent

        :Params:
            :param na

        :Returns:
            Boolean indicating whether message is being sent (as opposed to remaining in draft form)

        """
        return self._msgDict["send_status"] == "Y"

    def getFileReferences(self):
        """method that returns list of any file references ("attachments") associated with the message entity

        :Params:
            :param na

        :Returns:
            list of any file references ("attachments") associated with the message entity

        """
        return self.fileReferences

    def setFileReferences(self, p_fileRefsLst):
        """method that sets list of any file references ("attachments") associated with the message entity

        :Params:
            :param p_fileRefsLst

        :Returns:
            na

        """
        self.fileReferences = p_fileRefsLst

    def getOutputFileTarget(self, p_reqObj):
        """for given deposition, determine path to cif messaging data file to be updated

        :Params:
            :param `p_reqObj` : request Object

        :Returns:
            returnFilePath : absolute path to cif data file containing messages or notes for the given deposition

        """
        returnFilePath = None

        msgDI = MessagingDataImport(p_reqObj, verbose=self._verbose, log=self._lfh)

        returnFilePath = msgDI.getFilePath(contentType="messages-to-depositor", format="pdbx") if self._isWorkflow(p_reqObj) else Message.defaultMsgsToDpstrFilePath
        logger.info("messages-to-depositor path is: %s", returnFilePath)

        return returnFilePath

    def _isWorkflow(self, p_reqObj):
        """Determine if currently operating in Workflow Managed environment

        :Returns:
            boolean indicating whether or not currently operating in Workflow Managed environment
        """
        #
        fileSource = str(p_reqObj.getValue("filesource")).lower()
        #
        if fileSource and fileSource in ["archive", "wf-archive", "wf_archive", "wf-instance", "wf_instance"]:
            # if the file source is any of the above then we are in the workflow manager environment
            return True
        else:
            # else we are in the standalone dev environment
            return False

    @property
    def isNoteEmail(self):
        """Is the message is being automatically sent by another server-side python module (e.g. reminder), but
        does not normally trigger an email message, force sending

        :Params:
            :param na

        :Returns:
            boolean indicating whether message should send email

        """
        return self._bIsNoteEmail is True


class AutoMessage(Message):
    """Subclass to represent message that is being automatically sent by another server-side python module (e.g. Release module)
    (i.e. as opposed to being invoked via URL request by a web app client )

    """

    def __init__(self, p_msgDict, p_fileRefLst=None, p_verbose=True, p_log=sys.stderr):
        if p_fileRefLst is None:
            p_fileRefLst = []
        Message.__init__(self, p_msgDict, p_fileRefLst, p_verbose, p_log)
        #
        self._bIsAutoMsg = True
        self._msgDict["message_state"] = "livemsg"  # NOTE: this field is not part of the PdbxMessage data structure, and thus is not persisted to data file.


class ReminderMessage(Message):
    """Subclass to represent release date "reminder" messages that require different handling (e.g. for HPUB entries). These are invoked via URL request."""

    def __init__(self, p_msgDict, p_fileRefLst=None, p_verbose=True, p_log=sys.stderr):
        if p_fileRefLst is None:
            p_fileRefLst = []
        Message.__init__(self, p_msgDict, p_fileRefLst, p_verbose, p_log)
        #
        self._bIsReminderMsg = True
        self._msgDict["message_state"] = "livemsg"  # NOTE: this field is not part of the PdbxMessage data structure, and thus is not persisted to data file.


class Note(Message):
    """Subclass to represent "Note" message content type, which are persisted to a separate notes data file."""

    notesContentType = "notes"

    def getOutputFileTarget(self, p_reqObj):
        """for given deposition, determine path to cif messaging data file to be updated

        :Params:
            :param `reqObj` : request Object

        :Returns:
            returnFilePath : absolute path to cif data file containing messages or notes for the given deposition
        """
        returnFilePath = None

        msgDI = MessagingDataImport(p_reqObj, verbose=self._verbose, log=self._lfh)

        returnFilePath = msgDI.getFilePath(contentType="notes-from-annotator", format="pdbx") if self._isWorkflow(p_reqObj) else Message.defaultNotesFilePath
        logger.info("-- notes-from-annotator path is: %s", returnFilePath)

        return returnFilePath

    @property
    def contentType(self):
        return Note.notesContentType
        # return "notes"


class AutoNote(Note):
    """Subclass to represent message that is being automatically sent by another server-side python module and destined for notes (e.g. Release module)
    (i.e. as opposed to being invoked via URL request by a web app client )
    Support for optional email sending of message as well
    """

    def __init__(self, p_msgDict, p_fileRefLst=None, p_verbose=True, p_log=sys.stderr, p_email=True):

        if p_fileRefLst is None:
            p_fileRefLst = []

        Note.__init__(self, p_msgDict, p_fileRefLst, p_verbose, p_log)
        #
        self._bIsAutoMsg = True
        self._bIsNoteEmail = p_email
        self._msgDict["message_state"] = "livemsg"  # NOTE: this field is not part of the PdbxMessage data structure, and thus is not persisted to data file.
        self._msgDict["message_type"] = "archive_auto_noorig"  # Archive a note, but not original message
