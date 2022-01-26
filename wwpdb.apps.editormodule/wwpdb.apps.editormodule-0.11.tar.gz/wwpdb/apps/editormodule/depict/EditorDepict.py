##
# File:  EditorDepict.py
# Date:  02-Feb-2012
# Updates:
#    2012-02-02    RPS    Created based on ChemCompDepict
#    2012-04-02    RPS    Updates related to adoption of accordion strategy for left-side navigation menu.
#                         Improved handling of cases where datafile being processed does not contain data corresponding
#                         to cif category being requested for display/edit.
#    2012-04-03    RPS    Updated to handle DataTables "aoColumns" and "sColumns" properties, needed for
#                          DataTable initialization in support of preserving column reordering settings when filtering/redrawing
#    2012-04-05    RPS    Updated to enable proper maintenance of "true row indices" throughout any
#                            manipulation of row order on front-end. (primarily affected __createDataTableAaDataList() method )
#    2012-04-06    RPS    Providing for display of cif categories in the datafile but not in standard list of categories provided
#                         to user via accordion nav menu.
#                         Introduced support for adding new record into cif category/DataTable
#    2012-04-10    RPS    Introduced support for deleting a record.
#    2012-04-26    RPS    Updates for improved handling of different input sources of cif file.
#    2012-04-30    RPS    'struct_site' category no longer member of 'Advisory and Remarks' topic group.
#    2012-05-08    RPS    Special handling put in place for 'pdbx_database_proc' category. Will need to revisit.
#    2012-05-15    RPS    Introduced support for custom jEditable calendar input type which leverages jQuery UI DatePicker
#    2012-06-28    RPS    Introduced support for launching of Jmol viewer relative to specific records selected via DataTable
#                         interface, such that Jmol scripting commands are customized based on cif category and row selected.
#    2012-07-13    RPS    Improved handling of long category names when used as labels in the left hand accordion navigation menu
#    2012-07-27    RPS    getDataTableTemplate() updated to accommodate column specific search filtering
#    2012-08-07    RPS    Now obtaining config details for left side navigation accordion menu via strategy using PdbxDataIo and
#                            cif formatted view configuration file.
#    2012-08-10    RPS    Introduced support for toggling between "Show All Fields" and "Show Priority Fields Only" views in the UI.
#                            Tweaks to help-text relating to selecting rows for action in the UI.
#    2012-09-13    RPS    Updated to adapt Jmol handling in workflow managed context.
#    2012-09-28    RPS    Propagating "context" request parameter as necessary at launch for use by other operations downstream.
#    2012-10-18    ZF     Added subdirectory attribute, setAbsolutePath function
#    2012-10-22    RPS    Adjusting upper limit for enumerated lists to be vended via dropdown vs. autocomplete UI controls.
#    2013-02-12    RPS    Navigation menu changed from vertical accordion style to horizontal toolbar display.
#                         Supporting simultaneous display of >1 DataTable.
#                         Enforcing read-only behavior for given items in a cif category as per cif view config file.
#    2013-02-14    RPS    Added functionality to allow for drop-down choices that launch simultaneous viewing of >1 DataTable
#    2013-02-26    RPS    Introduced support for "undo"-ing edits.
#    2013-03-11    RPS    Updated to accommodate "_ALT" metadata (e.g. for enums, boundary constraints) which is used
#                          in precedence over non-"_ALT" metadata
#    2013-03-15    RPS    Introduced support for sorting of columns when required for particular cif categories (e.g. citation authors)
#                          Also accommodating different display behavior based on a cif category's row cardinality as specified in
#                          view config file.
#    2013-03-18    RPS    Removing sorting functionality (moved to PdbxDataIo)
#    2013-03-18    RPS    Corrected bug in generation of "true" row indexes in self.__createDataTableAaDataList() method
#    2013-04-24    RPS    Introduced support for identifying and checking for "mandatory" cif items (i.e. items that require non-null value).
#    2013-05-01    RPS    Fixed bug in self.__genCtgryNavBar() affecting generation of "combo-viewing" drop-down choices.
#    2013-05-17    RPS    Removed now obsolete code that had been in place for constructing "transposed view" datatables via server-side strategy.
#                             Front-end now bears primary responsibility for doing this.
#    2013-06-05    RPS    Current requirements no longer require scrollnav navigation.
#                            Adopting new strategy for relaying cardinality meta data to the front end.
#    2013-06-11    RPS    Accommodating explicit config of input type for certain fields as per annotation team request. NOTE: this is currently a workaround
#                            for what should be handled via config file specifications.
#    2013-06-20    RPS    doRender() method updated to accommodate display of entry title.
#    2013-12-04    RPS    Re-introduced support for viewing all "Other Categories"
#    2013-12-06    RPS    Providing select_w_other behavior for 'struct_keywords.pdbx_keywords'
#    2014-02-04    RPS    Adjusting font-size of labels in "Other Categories" drop-down list, so that label fits within designated width.
#    2014-02-05    RPS    'exptl_crystal_grow.method' added to list of items requiring "select-with-other" drop-down functionality
#    2014-02-10    RPS    doRender updated to accommodate dep ID value passed as "identifier" query parameter when in context of AnnotMod launch (i.e. outside WF context).
#    2014-02-18    RPS    'pdbx_seq_one_letter_code' now set to provide editablility via textarea
#    2014-03-27    RPS     changes to __getAllCategoriesInDataFile() required for use of PdbxCoreIoAdapter instead of PdbxPyIoAdapter
#    2014-07-09    RPS    Introduced changes that will eventually support "insertRow" functionality, editing of editor view config files, and EM and NMR views.
#    2014-07-14    RPS    Enforcing "select_w_other" input type for 'nmr_exptl.type', 'nmr_exptl_sample.isotopic_labeling', 'nmr_sample_details.solvent_system'
#    2014-10-07    RPS    Introducing support for __itemsAllowingCifNullOption.
#    2014-10-14    RPS    Temporary workaround to allow "split" choice for "pdbx_data_base related.content_type"?
#    2015-04-15    RPS    Introducing support for CIF Editor self-Config UI.
#                            Updates as per upgrades in DataTables/jQuery versions used.
#    2015-05-06    RPS    Fixed bug in getDataTableTemplate(), occurring only in Chrome wherein parameter catDispLabel is passed in from Chrome without being
#                            URL decoded, thereby causing failures when this parameter's value is used as lookup key
#    2015-06-18    RPS    Updates to better separate use of "context" parameter from use of "expmethod"
#    2015-07-06    RPS    Introducing more support for handling EM experimental method.
#    2015-09-03    RPS    Added 'pdbx_database_status.methods_development_category' to self.__itemsAllowingCifNullOption
#    2015-09-03    RPS    Incorporating use of wwpdb.apps.editormodule.config.EditorConfig
#    2016-03-08    RPS    getDataTableTemplate() updated so that pdbxDataIo.purgeDataStoreSnapShots() moved out to EditorWebApp.__makeDataStoreSnapShot()
#    2016-09-13    RPS:   changes in support of migrating config for "arrReadOnlyCtgries" and "arrCanDeleteLastRowCtgries" to python source instead of having in front end files
#    2017-02-19    EP     transmit defview to client
#    2017-06-19    EP     add pdbx_audit_support.funding_organization to list of enumerations with other
#    2017-09-26    EP     add pdbx_nmr_ensemble.conformer_selection_criteria to list of enumerations with other
#    2018-06-28    EP     start to use logging. Cut down on output. Provide function timing.
##
"""
Base class for HTML depictions containing common HTML constructs.

"""
__docformat__ = "restructuredtext en"
__author__ = "Raul Sala"
__email__ = "rsala@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.02"

import os
import sys
import time

try:
    from urllib.parse import unquote as u_unquote
except ImportError:
    from urllib import unquote as u_unquote

from json import loads
from mmcif_utils.persist.PdbxPersist import PdbxPersist  # temporary for testing
from wwpdb.apps.editormodule.io.PdbxDataIo import PdbxDataIo
from wwpdb.apps.editormodule.config.EditorConfig import EditorConfig
from wwpdb.io.graphics.GraphicsContext3D import GraphicsContext3D
import logging

logger = logging.getLogger(__name__)


class EditorDepict(object):
    """Base class for HTML depictions contain definitions of common constructs."""

    def __init__(self, verbose=False, log=sys.stderr):
        """

        :param `verbose`:  boolean flag to activate verbose logging.
        :param `log`:      stream for logging.

        """
        self.__verbose = verbose
        self.__lfh = log
        self.__debug = False
        #
        self.absltSessionPath = None
        self.absltEdtrSessionPath = None
        self.rltvSessionPath = None
        #
        self.jmolCodeBase = os.path.join("/applets", "jmol")
        #
        #
        self.__navTabGroups = []
        self.__navTabGroup_Other = {"id": "other", "dsply_lbl": "Other Categories", "dsply_typ": "dropdown", "dropdown_display_labels": []}

    def doRenderDevProto(self, p_reqObj, p_bIsWorkflow, p_dataBlockName):
        """DEV - PROTOTYPING PURPOSE:
        Render HTML used as starter page/container for the General Annotation Editor interface
        Once this content is in the browser, AJAX calls are made to populate the page
        with content when needed.

        :Params:

            + ``p_reqObj``: Web Request object
            + ``p_bIsWorkflow``: boolean indicating whether or not operating in Workflow Manager environment
            + ``p_dataBlockName``: name of cif "datablock" which in context of entry datafiles refers to name of primary entity

        :Returns:
            ``oL``: output list consisting of HTML markup
        """
        oL = []
        #
        sessionId = p_reqObj.getSessionId()
        wfInstId = str(p_reqObj.getValue("instance")).upper()
        depId = str(p_reqObj.getValue("identifier"))
        classId = str(p_reqObj.getValue("classID")).lower()
        fileSource = str(p_reqObj.getValue("filesource")).lower()
        tmpltPath = p_reqObj.getValue("TemplatePath")
        dataFile = str(p_reqObj.getValue("datafile"))
        #
        if self.__verbose:
            logger.info(" -- datafile is:%s", dataFile)
        #
        if self.__verbose:
            logger.info("--------------------------------------------")
            logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            logger.info("identifier   %s", depId)
            logger.info("instance     %s", wfInstId)
            logger.info("file source  %s", fileSource)
            logger.info("sessionId  %s", sessionId)
        #
        ############################################################################
        # create dictionary of content that will be used to populate HTML template
        ############################################################################
        myD = {}
        myD["sessionid"] = sessionId
        myD["instance"] = wfInstId
        myD["classid"] = classId
        myD["filesource"] = fileSource
        # following params only for rcsb stand-alone version
        myD["caller"] = p_reqObj.getValue("caller")
        myD["filepath"] = p_reqObj.getValue("filePath")
        #
        if p_bIsWorkflow:
            myD["identifier"] = depId
        else:
            (_pth, fileName) = os.path.split(p_reqObj.getValue("filePath"))
            (fN, _fileExt) = os.path.splitext(fileName)
            if fN.upper().startswith("D_"):
                depDataSetId = fN.upper()
            elif fN.lower().startswith("rcsb"):
                depDataSetId = fN.lower()
            else:
                depDataSetId = "TMP_ID"
            myD["identifier"] = depDataSetId
        #
        myD["session_url_prefix"] = self.rltvSessionPath
        myD["datafile"] = dataFile
        myD["data_block_name"] = p_dataBlockName
        #
        oL.append(self.processTemplate(tmpltPth=tmpltPath, fn="editor_dev_proto_tmplt.html", parameterDict=myD))
        #
        return oL

    def doRender(self, p_reqObj, p_bIsWorkflow):
        """Render HTML used as starter page/container for the General Annotation Editor interface
        Once this content is in the browser, AJAX calls are made to populate the page
        with content when needed.

        :Params:

            + ``p_reqObj``: Web Request object
            + ``p_bIsWorkflow``: boolean indicating whether or not operating in Workflow Manager environment

        :Returns:
            ``oL``: output list consisting of HTML markup
        """
        oL = []
        #
        sessionId = p_reqObj.getSessionId()
        subdirectory = str(p_reqObj.getValue("subdirectory"))
        #
        wfInstId = str(p_reqObj.getValue("instance")).upper()
        depId = str(p_reqObj.getValue("identifier"))
        dataBlockName = str(p_reqObj.getValue("datablockname"))
        entryTitle = str(p_reqObj.getValue("entrytitle"))
        classId = str(p_reqObj.getValue("classID")).lower()
        fileSource = str(p_reqObj.getValue("filesource")).lower()
        tmpltPath = p_reqObj.getValue("TemplatePath")
        dataFile = str(p_reqObj.getValue("datafile"))
        context = str(p_reqObj.getValue("context"))
        # expMethodList = (p_reqObj.getValue("expmethod").replace('"', '')).split(",") if (len(p_reqObj.getValue("expmethod").replace('"', '')) > 1) else []
        emViewModel = str(p_reqObj.getValue("emmodelview"))
        defView = str(p_reqObj.getValue("defview"))

        #
        if self.__verbose:
            logger.info(" -- datafile is:%s", dataFile)
            logger.info(" -- context is:%s", context)
        #
        if len(context) < 1:
            context = None
        #
        if self.__verbose:
            logger.info("--------------------------------------------")
            logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            logger.info("identifier   %s", depId)
            logger.info("instance     %s", wfInstId)
            logger.info("file source  %s", fileSource)
            logger.info("sessionId  %s", sessionId)
        #
        ############################################################################
        # create dictionary of content that will be used to populate HTML template
        ############################################################################
        myD = {}
        myD["context"] = context
        myD["expmethod"] = p_reqObj.getValue("expmethod")
        myD["emtogglelabel"] = "Load Map+Model View" if (emViewModel == "n" or emViewModel == "") else "Load Map Only View"
        myD["currentemviewlbl"] = "Current View: Map Only" if (emViewModel == "n" or emViewModel == "") else "Current View: Map+Model"
        myD["emmodelview"] = emViewModel
        myD["sessionid"] = sessionId
        myD["subdirectory"] = subdirectory if (subdirectory is not None and len(subdirectory) > 1) else "none"
        myD["instance"] = wfInstId
        myD["classid"] = classId
        myD["filesource"] = fileSource
        # following params only for rcsb stand-alone version
        myD["caller"] = p_reqObj.getValue("caller")
        myD["filepath"] = p_reqObj.getValue("filePath")
        myD["readonlycategories"] = self.__getReadOnlyCategories()
        myD["allowdeletelastrow"] = self.__getCategoriesAllowingDeleteLastRow()
        #
        if p_bIsWorkflow:
            myD["identifier"] = depId
        else:
            if depId is not None and len(depId) > 1:
                myD["identifier"] = depId
            else:
                (_pth, fileName) = os.path.split(p_reqObj.getValue("filePath"))
                (fN, _fileExt) = os.path.splitext(fileName)
                if fN.upper().startswith("D_"):
                    depDataSetId = fN.upper()
                elif fN.lower().startswith("rcsb"):
                    depDataSetId = fN.lower()
                else:
                    depDataSetId = "TMP_ID"
                myD["identifier"] = depDataSetId
        #
        pdbxDataIo = PdbxDataIo(p_reqObj, self.__verbose, self.__lfh)
        self.__navTabGroups = pdbxDataIo.getCtgryNavConfig()
        #
        myD["session_url_prefix"] = self.rltvSessionPath
        myD["absolute_session_path"] = self.absltSessionPath
        myD["datafile"] = dataFile
        myD["data_block_name"] = dataBlockName
        myD["entry_title"] = entryTitle
        myD["defview"] = defView

        if p_bIsWorkflow:
            dataFile = pdbxDataIo.getPdbxDataFilePath()
        myD["ctgry_nav_bar"], myD["crdnlty_dict"] = self.__genCtgryNavBar(dataBlockName, fileSource, dataFile, p_bIsWorkflow, context)
        #
        if context:
            if context in ["emtesting", "em"]:
                myD["expmethod"] = "ELECTRON MICROSCOPY"  # DONE TO ALLOW FOR STANDALONE TESTING PURPOSES during which expmethod is not passed so relying on context
            if context in ["nmrtesting", "nmr"]:
                myD["expmethod"] = "SOLUTION NMR"  # DONE TO ALLOW FOR STANDALONE TESTING PURPOSES

            if context == "editorconfig":
                templateFileName = "editor_launch_tmplt_config.html"
            # elif( context in ["emtesting", "em"] ):
            # templateFileName = "editor_launch_tmplt_scrollnav.html"
            else:
                templateFileName = "editor_launch_tmplt.html"
        else:
            templateFileName = "editor_launch_tmplt.html"

        oL.append(self.processTemplate(tmpltPth=tmpltPath, fn=templateFileName, parameterDict=myD))
        #
        return oL

    def getJmolMarkup(self, p_reqObj, p_bIsWorkflow):
        """
        For given cif category, obtain html markup for rendering data in Jmol viewer

        :Params:

            + ``p_reqObj``: Web Request object

        :Returns:
            ``mrkpList``: output list consisting of HTML markup

        """
        tmpltPath = p_reqObj.getValue("TemplatePath")
        rltvSessPath = p_reqObj.getValue("RelativeSessionPath")
        dataFile = str(p_reqObj.getValue("datafile"))
        cifCtgry = p_reqObj.getValue("cifctgry")
        rowKeyValueJson = p_reqObj.getValue("row_key_value_json")
        rowIdx = p_reqObj.getValue("row_idx")
        #
        if p_bIsWorkflow:
            depDataSetId = p_reqObj.getValue("identifier")
            dataFile = depDataSetId + "-model.cif"
        #
        rowIdx = int(rowIdx.replace("row_", ""))
        rltvPathDataFile = os.path.join(rltvSessPath, dataFile)
        rcrdKeyValueDict = loads(rowKeyValueJson)
        #
        if self.__verbose:
            logger.info("-- dictionary of attributes for record transmitted from UI follows")
            for (key, value) in rcrdKeyValueDict.items():
                logger.info("-- dict[%s] : %s", key, value)
        #

        ###############################################################################################
        # get Jmol scripting commands pertinent context of given cif category
        ###############################################################################################
        gC = GraphicsContext3D(app3D="JMol", verbose=self.__verbose, log=self.__lfh)
        if cifCtgry == "struct_site":
            pdbxDataIo = PdbxDataIo(p_reqObj, self.__verbose, self.__lfh)
            dbFilePath = pdbxDataIo.getDataStorePath()
            if dbFilePath is not None:
                gC.setPersistStorePath(persistFilePath=dbFilePath)
        gcS = gC.getGraphicsContext(categoryName=cifCtgry, rowDictList=[rcrdKeyValueDict])

        ###############################################################################################
        # generating HTML that serves as markup for Jmol <object>
        ###############################################################################################
        myD = {}
        mrkpList = []

        myD["rowid"] = rowIdx
        myD["jmol_code_base"] = self.jmolCodeBase
        myD["3dpath"] = rltvPathDataFile
        myD["jmol_script_cmds"] = gcS

        mrkpList.append(self.processTemplate(tmpltPth=tmpltPath, fn="editor_jmol_tmplt.html", parameterDict=myD))

        return mrkpList

    # ####### BEGIN -- Specific to DataTable Implementation ##################
    # NOTE: consider encapsulating DataTable functionality as separate class

    def getJsonDataTable(self, p_reqObj, p_ctgryRcrdList, p_iDisplayStart, p_ctgryColList):  # pylint: disable=unused-argument
        """Generate contents of json object expected by DataTables for populating display
        table with data.

        :Params:

            + ``p_reqObj``: webapp request object
            + ``p_ctgryColList``: list of column names corresponding sequence of which corresponds to
                                sequence of fields in each record in p_recordList
            + ``p_ctgryRcrdList``: list of records corresponding to records obtained from datafile for given cif category
            + ``p_iDisplayStart``: DataTable parameter used by the plugin as index of first record in set actually being displayed on screen


        :Returns:
            ``rtrnDict``: dictionary of records for display on screen as complies with DataTables requirements for JSON object it expects from server
        """
        rtrnDict = {}

        sColumns = ""
        sComma = ""
        for idx, colName in enumerate(p_ctgryColList):
            if idx > 0:
                sComma = ","
            sColumns += sComma + colName
        #
        if self.__debug:
            logger.info("-- sColumns is: %r", sColumns)
        #
        rtrnDict["sColumns"] = sColumns

        aaDataList = self.__createDataTableAaDataList(p_ctgryColList, p_ctgryRcrdList, p_iDisplayStart)

        if self.__verbose and self.__debug:
            logger.debug("-- DEBUG -- aaDataList after call to createDataTableAaDataList is: %r", aaDataList)

        rtrnDict["aaData"] = aaDataList

        return rtrnDict

    def getDataTableTemplate(self, p_reqObj, p_cifCtgryNm, labelName=None):
        """
        For given cif category, obtain "staging" components to be used in
        preparation for loading webpage with DataTable:
                +  html skeleton template which will be populated by jQuery DataTables plugin
                +  dictionary

        :Params:

            + ``p_reqObj``: Web Request object
            + ``p_cifCtgryNm``: name of cif category for which data is being displayed
            + ``labelName``: Override label name from p_reqobj for multirequest

        :Returns:
            ``mrkpList``: output list consisting of HTML markup serving as skeleton starter template for DataTable
            ``catObjDict``: dictionary of display, config settings for DataTable

        """
        ###############################################################################################
        # FIRST: generating dictionary of configuration/display details defined per column
        ###############################################################################################

        start = time.time()

        logger.info("Starting %s", p_cifCtgryNm)

        catObjDict = {}

        if labelName:
            catDispLabel = labelName
        else:
            catDispLabel = p_reqObj.getValue("displabel")

        logger.debug("catDispLabel: %s", catDispLabel)
        context = str(p_reqObj.getValue("context"))

        if sys.version_info[0] < 3:
            catDispLabel = u_unquote(catDispLabel).decode(
                "utf8"
            )  # found the need to do this when Chrome browser being used, which for some reason does not URL decode the data as Firefox does  # noqa: E501
        else:
            catDispLabel = u_unquote(catDispLabel)  # Need to test chrome XXXX

        pdbxDataIo = PdbxDataIo(p_reqObj, self.__verbose, self.__lfh)
        catObjDict = pdbxDataIo.getTblConfigDict(p_cifCtgryNm, catDispLabel)  # note: to be used as Json Object when in webpage
        bOk, ctgryColList = pdbxDataIo.getCategoryColList(p_cifCtgryNm)

        if bOk:
            if len(catObjDict["COLUMN_DISPLAY_ORDER"]) > 0:
                self.__configureInputTypes(p_cifCtgryNm, catObjDict, ctgryColList)  # adjust for input types expected by DataTable/Jeditable

                # CONSIDER THIS POINT IN THE CODE FOR ADDITION OF SUPPLEMENTAL COLUMNS TO SUPPORT
                # "ADD-ON" FUNCTIONALITY NOT PROVIDED OUT OF BOX BY DATATABLES
                # ctgryColList.append(idx)

                # add other necessary key/values
                catObjDict["NAME"] = p_cifCtgryNm
                catObjDict["COLUMN_COUNT"] = len(ctgryColList)
                catObjDict["VLDT_ERR_FLAGS"] = {}  # {1: {0:('vldt_err'), 3:('bndry_err')}, 2: {1:('bndry_err'), 5:('vldt_err')} }
                catObjDict["VLDT_ERR_FLAG_COLS"] = list(catObjDict["VLDT_ERR_FLAGS"])

                # make config for non-"ALT" settings equivalent to "ALT" settings where necessary for UI purposes
                catObjDict["COLUMN_ENUMS"] = catObjDict["COLUMN_ENUMS_ALT"] if len(catObjDict["COLUMN_ENUMS_ALT"]) > 0 else catObjDict["COLUMN_ENUMS"]
                catObjDict["MANDATORY_COLUMNS"] = (
                    catObjDict["MANDATORY_COLUMNS_ALT"]
                    if (catObjDict["MANDATORY_COLUMNS_ALT"] and len(catObjDict["MANDATORY_COLUMNS_ALT"]) > 0)
                    else catObjDict["MANDATORY_COLUMNS"]
                    if (catObjDict["MANDATORY_COLUMNS"] and len(catObjDict["MANDATORY_COLUMNS"]) > 0)
                    else []
                )

                # provide DataTables "aoColumns" property to be used in initializing the DataTable
                # with set of known column names that it can use for keeping track of column ordering
                sNameList = []
                for colName in ctgryColList:
                    newSnameDict = {}
                    newSnameDict["mDataProp"] = colName
                    sNameList.append(newSnameDict)
                #
                catObjDict["DTBL_AOCOLUMNS"] = sNameList
                catObjDict["HIDDEN_COLUMNS"] = []
                catObjDict["PRIORITY_COLUMNS"] = list(catObjDict["COLUMN_DISPLAY_ORDER"])
                catObjDict["READ_ONLY_COLUMNS"] = []

                # traverse column list
                for idx, item in enumerate(ctgryColList):
                    # adjust columnn display order for any columns in datafile but not addressed by dictionary
                    if idx not in catObjDict["COLUMN_DISPLAY_ORDER"]:
                        catObjDict["HIDDEN_COLUMNS"].append(idx)
                        catObjDict["COLUMN_DISPLAY_ORDER"].append(idx)

                    # establish read-only columns list
                    if "COLUMN_READ_ONLY_FLAG" in catObjDict:
                        if item in catObjDict["COLUMN_READ_ONLY_FLAG"]:
                            if catObjDict["COLUMN_READ_ONLY_FLAG"][item] == "Y":
                                catObjDict["READ_ONLY_COLUMNS"].append(idx)
                    else:
                        catObjDict["READ_ONLY_COLUMNS"].append(idx)  # defaulting to read-only when cif category not in config dictionarys

                # CONSIDER THIS POINT IN THE CODE FOR ADDITION OF SUPPLEMENTAL COLUMNS TO SUPPORT
                # "ADD-ON" FUNCTIONALITY NOT PROVIDED OUT OF BOX BY DATATABLES
                # catObjDict['COLUMN_DISPLAY_ORDER'].append(idx)

                ###############################################################################################
                # SECOND: generating HTML that serves as markup starter skeleton to be populated by DataTables
                ###############################################################################################
                mrkpList = []
                srchHdrList = []  # separate list of markup representing <th> elements accommodating individual column search filtering

                classStr = ' class="cifdatatable"'

                mrkpList.append('<table id="' + p_cifCtgryNm + '_tbl"' + classStr + "><thead><tr>")

                for idx, item in enumerate(ctgryColList):
                    colName = catObjDict["COLUMN_DISPLAY_NAMES"].get(idx, item) if type(catObjDict["COLUMN_DISPLAY_NAMES"]) is dict else item
                    mrkpList.append('<th class="cifitemhdr" title="' + item + '">' + colName + "</th>")
                    srchHdrList.append('<th><input type="text" name="search_' + colName + '" value="Search ' + colName + '" class="search_init" /></th>')

                mrkpList.append('</tr><tr class="srch_hdrs displaynone">')
                mrkpList.append("".join(srchHdrList))
                # mrkpList.append('</tr></thead><tbody><tr></tr></tbody></table>')  THIS WAS FOUND TO BE PROBLEM IN DATATABLES 1.10!!!
                mrkpList.append("</tr></thead><tbody></tbody></table>")
                mrkpList.append(
                    '<br class="clearfloat"/><br /><div id="'
                    + p_cifCtgryNm
                    + '_record_actions"><input style="display: inline; font-size: .8em;" class="cifctgry_add_row '
                    + p_cifCtgryNm
                    + '_row_action" id="'
                    + p_cifCtgryNm
                    + '_add_row" name="'
                    + p_cifCtgryNm
                    + '" value="Add Record" type="button">'
                )  # noqa: E501
                mrkpList.append(
                    '<span class="select_for_action help" id="select_for_action_'
                    + p_cifCtgryNm
                    + '" style="padding-left: 20px;"><strong>RIGHT-click (or CTRL-click) on row to mark respective record for action.</strong></span>'
                )  # noqa: E501
                mrkpList.append(
                    '<span class="unselect help" id="unselect_'
                    + p_cifCtgryNm
                    + '" style="padding-left: 20px;"><strong>RIGHT-click (or CTRL-click) on row to unmark selected record for action.</strong></span>'
                )  # noqa: E501
                if context != "editorconfig":
                    mrkpList.append(
                        '<input style="display: inline; margin-left: 20px;  font-size: .8em;" class="cifctgry_delete_row '
                        + p_cifCtgryNm
                        + '_row_action onrowselect" id="'
                        + p_cifCtgryNm
                        + '_delete_row" name="'
                        + p_cifCtgryNm
                        + '" value="Delete Record" type="button">'
                    )  # noqa: E501
                # mrkpList.append('<input style="display: inline; margin-left: 20px;  font-size: .8em;" class="cifctgry_insert_row '+p_cifCtgryNm+'_row_action onrowselect" id="'+p_cifCtgryNm+'_insert_row" name="'+p_cifCtgryNm+'" value="Insert Record After" type="button">')  # noqa: E501
                mrkpList.append(
                    '<input style="display: inline; margin-left: 20px;  font-size: .8em;" class="jmol_view '
                    + p_cifCtgryNm
                    + '_row_action onrowselect" id="'
                    + p_cifCtgryNm
                    + '_jmol_view" name="'
                    + p_cifCtgryNm
                    + '" value="Load Record Into Viewer" type="button">'
                )  # noqa: E501
                mrkpList.append("</div>")
            else:
                mrkpList = ["<h3>The cif category, '" + p_cifCtgryNm + "', did exist in the datafile but none of the items desired for view were present.</h3>"]

        else:
            mrkpList = ["<h3>The datafile being processed did not contain any data corresponding to cif category, '" + p_cifCtgryNm + "'.</h3>"]
        # RETURNing both markup and config dictionary

        end = time.time()
        logger.info("Done -- in %s ms", (end - start) * 1000)

        return mrkpList, catObjDict

    # ####### END -- Specific to DataTable Implementation ##################

    # #####################################   HELPER FUNCTIONS   #################################################

    def __getReadOnlyCategories(self):
        returnStr = "["

        for idx, ctgryName in enumerate(EditorConfig.arrReadOnlyCtgries):
            separator = ""
            if idx > 0:
                separator = ", "
            returnStr += separator + '"' + ctgryName + '"'

        returnStr += " ]"

        return returnStr

    def __getCategoriesAllowingDeleteLastRow(self):
        returnStr = "["

        for idx, ctgryName in enumerate(EditorConfig.arrAllowLastRowDeleteCtgries):
            separator = ""
            if idx > 0:
                separator = ", "
            returnStr += separator + '"' + ctgryName + '"'

        returnStr += " ]"

        return returnStr

    def __configureInputTypes(self, p_cifCtgryNm, p_catObjDict, p_ctgryColList):
        """Process info from PdbxDictionaryInfo regarding column types and enums in order to establish
        type of inputs required on web page.

        :Params:

            + ``p_catObjDict``: dictionary of config settings defined per column of the data

        :Returns:
            ``p_catObjDict``: via side-effect, dictionary that was input is updated additional key/value pairs for 'INPUT_TYPES'
        """
        inputTypes = {}
        colTypes = p_catObjDict["COLUMN_TYPES_ALT"] if len(p_catObjDict["COLUMN_TYPES_ALT"]) > 0 else p_catObjDict["COLUMN_TYPES"]
        enumOpts = p_catObjDict["COLUMN_ENUMS_ALT"] if len(p_catObjDict["COLUMN_ENUMS_ALT"]) > 0 else p_catObjDict["COLUMN_ENUMS"]
        for idx, ctype in colTypes.items():
            # logger.debug("-- type for idx: [%s] is: %s" %(idx,type) )
            inputTypes[idx] = "text"

            if idx < len(p_ctgryColList):
                # not sure why yet, but had to enforce this check for category such as "atom_site" where index of "1" actually skipped,
                # so that indexing went to "30" went should only have been "29" in colTypes, therefore not a matching correlation between
                # colTypes "index" value and actual indexes in place for accessing elements in p_ctgryColList

                if ctype == "select" or (len(enumOpts) > 0 and idx in enumOpts):
                    # assuming here that if there are enum options, that type should be of selection list type
                    enumOpts[idx].sort(key=str.lower)

                    # 2013-06-11,RPS: accommodating annotator requests for special case behavior via coding one-offs below, BUT should
                    # establish way to accommodate these configurations via config file
                    if p_cifCtgryNm + "." + p_ctgryColList[idx] in [
                        "struct_keywords.pdbx_keywords",
                        "pdbx_reference_molecule.class",
                        "exptl_crystal_grow.method",
                        "pdbx_nmr_exptl.type",
                        "pdbx_nmr_exptl_sample.isotopic_labeling",
                        "pdbx_nmr_sample_details.solvent_system",
                        "pdbx_audit_support.funding_organization",
                        "pdbx_nmr_ensemble.conformer_selection_criteria",
                    ]:
                        # inputTypes[idx] = 'select'
                        inputTypes[idx] = "select_w_other"
                    elif len(enumOpts[idx]) > 35:
                        if (p_cifCtgryNm in ["entity_src_gen", "entity_src_nat"] and "scientific" in p_ctgryColList[idx]) or (
                            p_cifCtgryNm + "." + p_ctgryColList[idx] == "software.name"
                        ):  # noqa: E501
                            inputTypes[idx] = "autocomplete_w_other"
                        else:
                            inputTypes[idx] = "autocomplete"
                    else:
                        if (p_cifCtgryNm in ["entity_src_gen", "entity_src_nat"]) and ("scientific" in p_ctgryColList[idx]):
                            inputTypes[idx] = "select_w_other"
                        else:
                            inputTypes[idx] = "select"
                            if p_cifCtgryNm + "." + p_ctgryColList[idx] in EditorConfig.itemsAllowingCifNullOption:
                                enumOpts[idx].append("?")
                            if p_cifCtgryNm + "." + p_ctgryColList[idx] == "pdbx_database_related.content_type":
                                enumOpts[idx].extend(["split", "complete structure"])

                elif ("details" in p_ctgryColList[idx]) or ("description" in p_ctgryColList[idx]) or (p_ctgryColList[idx] == "pdbx_seq_one_letter_code"):
                    inputTypes[idx] = "textarea"
                elif ctype == "date-time":
                    inputTypes[idx] = ctype
                else:
                    inputTypes[idx] = "text"

        p_catObjDict["INPUT_TYPES"] = inputTypes

    # ####### BEGIN -- Specific to DataTable Implementation ##################

    def __createDataTableAaDataList(self, p_colList, p_recordList, p_iDisplayStart):  # pylint: disable=unused-argument
        """Generate contents of "aaData" json object expected by DataTables for populating display
        table with data.

        :Params:

            + ``p_colList``: list of column names sequence of which corresponds to
                                sequence of fields in each record in p_recordList
            + ``p_recordList``: list of records corresponding to records obtained from datafile for given cif category
            + ``p_iDisplayStart``: DataTable parameter used by the plugin as index of first record in set actually being displayed on screen


        :Returns:
            ``rtrnLst``: list of records for display on screen as complies with DataTables requirements for "aaData" object
        """
        if self.__verbose:
            logger.info("--------------------------------------------")
            logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        rtrnLst = []

        for indx, record in enumerate(p_recordList):
            if self.__verbose:
                logger.info("-- record[%s] is: %s", indx, record)
            #
            newRecordJsonObj = {}
            #

            # the record is itself a dictionary, which will consist of single key/value pair where the "key" represents true
            # row index of the cif record as it sits in persistent store and "value" is the cif record itself

            trueRowIndxKey, recordValue = list(record.items())[0]
            newRecordJsonObj["DT_RowId"] = "row_" + str(trueRowIndxKey)
            newRecordJsonObj["DT_RowClass"] = "dt_row"
            #
            for colName, itemValue in zip(p_colList, recordValue):
                newRecordJsonObj[colName] = itemValue
            #
            rtrnLst.append(newRecordJsonObj)

        return rtrnLst

    # ####### END -- Specific to DataTable Implementation ##################

    def __getAllCategoriesInDataFile(self, p_fileSource, p_dataFile, p_bIsWorkflow):  # pylint: disable=unused-argument

        if self.__verbose:
            logger.info("--------------------------------------------")
            logger.info("-- starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        ctgryList = []

        dbFilePath = os.path.join(self.absltSessionPath, "dataFile.db")
        myPersist = PdbxPersist(self.__verbose, self.__lfh)
        myInd = myPersist.getIndex(dbFileName=dbFilePath)
        containerNameList = myInd["__containers__"]
        for containerName, _containerType in containerNameList:
            for objName in myInd[containerName]:
                ctgryList.append(objName)

        if self.__verbose:
            logger.info("+++ completed at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        return ctgryList

    def __genCtgryNavBar(self, p_dataBlockName, p_fileSource, p_dataFile, p_bIsWorkflow, p_context):  # pylint: disable=unused-argument
        """Generate markup used to render the navigation menu bar.

        :Params:

            + ``p_dataBlockName``: identifier indicating cif datablock name
            + ``p_fileSource``: indicates whether working in Workflow Managed context or in RCSB DEV context
            + ``p_dataFile``: identifier for cif datafile serving as source for data being fed into the EditorMod



        :Returns:
            + resulting html markup in form of python list
            + string representing JavaScript definition of object defining cardinality for given cif category
        """
        hdrMrkpTmpltWthDrpDwns = r"""
        <li class="topnav"><a href="#">%(dsply_lbl)s&nbsp;<img src="/editormodule/images/arrow.png" width="20" height="12" /></a>
            <ul>
                %(drpdwn_chcs)s
            </ul>
        </li>
        """

        hdrMrkpTmpltNoDrpDwns = r"""
        <li class="topnav"><a href="#" class="multi_cifctgry_submit ctgrygrpid_%(id)s" id="%(ctgries)s" name="%(ctgry_disply_lbls)s" >%(dsply_lbl)s&nbsp;</a></li>
        """

        drpDwnMrkpTmplt_single = r"""<li><a href="#" class="cifctgry_submit ctgrygrpid_%(ctgrygrpid)s %(cardinality)s" id="submit-%(selectid)s" name="%(ctgry)s" style="font-size: %(font_size)s;" >%(drpdwn_displ_lbl)s</a></li>"""  # noqa: E501

        drpDwnMrkpTmplt_combo = r"""<li><a href="#" class="multi_cifctgry_submit ctgrygrpid_%(ctgrygrpid)s %(cardinality)s" id="%(ctgry)s" name="%(ctgry_disply_lbls)s" >%(drpdwn_displ_lbl)s</a></li>"""  # noqa: E501

        navTabGroups = self.__navTabGroups
        if p_context != "editorconfig":
            navTabGroups.append(self.__navTabGroup_Other)
        hdrLst = []
        hdrMrkp = ""
        stndrdCtgrySet = set()
        otherCtgriesLst = []
        crdnltyDict = {}
        crdnltyJavaScriptStr = ""
        #
        index = 0
        #
        for navTabGrp in navTabGroups:
            if navTabGrp["dsply_typ"] == "dropdown":
                drpDwnLst = []
                #
                if navTabGrp["id"] == "other":
                    # have to determine which categories are in datafile but not in established set of navigation groups
                    # so that we can create an "Other" navigation group for these
                    allCtgriesInDatafile = set(self.__getAllCategoriesInDataFile(p_fileSource, p_dataFile, p_bIsWorkflow))
                    otherCtgries = allCtgriesInDatafile.difference(stndrdCtgrySet)

                    # generate list of otherCtgries so we can sort for display
                    for _n in range(len(otherCtgries)):
                        otherCtgriesLst.append(otherCtgries.pop())
                    otherCtgriesLst.sort()
                    #
                    for ctgryName in otherCtgriesLst:
                        if ctgryName != "atom_site" and ctgryName != "atom_site_anisotrop":
                            thisTupl = (ctgryName, {ctgryName: (ctgryName, "unit")})
                            navTabGrp["dropdown_display_labels"].append(thisTupl)

                            if ctgryName not in crdnltyDict:
                                crdnltyDict[ctgryName] = "unit"

                for dropDwnDisplLbl, ctgryDict in navTabGrp["dropdown_display_labels"]:
                    ctgries = ""
                    ctgryDsplNmLst = ""
                    ctgryDisplyLbls = None
                    ctgryCrdnlties = ""
                    ctgryTuplLst = list(ctgryDict.items())

                    if len(ctgryTuplLst) > 1:
                        # this if condition indicates drop-down choice that calls for
                        # simultaneous viewing of > 1 DataTable, i.e. "combo" viewing

                        mrkpTmplt = drpDwnMrkpTmplt_combo

                        for idx, ctgryTupl in enumerate(ctgryTuplLst):
                            if self.__debug:
                                logger.debug("------ DEBUG ------ combo drop-down choice found. ctgryTupl is: %r", ctgryTupl)
                            separator = ""
                            if idx > 0:
                                separator = "+"
                            ctgryDisplLbl = ctgryTupl[0]  # first member of tuple is diplay label for user selection which in 99% cases corresponds to a single cif category
                            ctgryNm = ctgryTupl[1][0]  # second member of tuple is itself a tuple with its first member being the category's true name
                            ctgryCrdnlty = ctgryTupl[1][1]  # second member of tuple is itself a tuple with its second member being the cardinality
                            ctgries += separator + ctgryNm
                            ctgryDsplNmLst += separator + ctgryDisplLbl
                            ctgryCrdnlties += separator + ctgryCrdnlty

                            stndrdCtgrySet.add(ctgryNm)

                        ctgryDisplyLbls = ctgryDsplNmLst.replace(" ", "%20")  # use urlencode style

                    else:
                        mrkpTmplt = drpDwnMrkpTmplt_single
                        ctgries = ctgryTuplLst[0][1][0]
                        ctgryCrdnlties = ctgryTuplLst[0][1][1]

                        stndrdCtgrySet.add(ctgries)  # in this case ctgries is really just one category
                    #
                    inputMrkp = self.__generateDropDownMarkup(ctgries, ctgryCrdnlties, dropDwnDisplLbl, navTabGrp["id"], mrkpTmplt, index, ctgryDisplyLbls)
                    drpDwnLst.append(inputMrkp)
                    index += 1
                #
                grpDict = navTabGrp.copy()
                grpDict["drpdwn_chcs"] = "\n".join(drpDwnLst)
                hdrMrkp = hdrMrkpTmpltWthDrpDwns % grpDict

            else:  # no dropdown list for the top level menu choice
                # """{'no_dropdown_dict': {'Genetically%20Engineered+Naturally%20Obtained+Synthesized': ('entity_src_gen+entity_src_nat+pdbx_entity_src_syn', 'multi+multi+multi')},
                # 'id': 5,
                # 'dsply_lbl': 'Polymer Source',
                # 'dsply_typ': 'no_dropdown'},"""

                hdrDict = navTabGrp.copy()

                ctgryNmLst = []
                crdnltyStr = ""
                crdnltyLst = []
                crdnltyJavaScriptStr = "{ "

                if navTabGrp["id"] != "other":

                    for key, tupl in navTabGrp["no_dropdown_dict"].items():
                        hdrDict["ctgry_disply_lbls"] = key
                        hdrDict["ctgries"] = tupl[0]
                        crdnltyStr = tupl[1]

                        ctgryNmLst = hdrDict["ctgries"].split("+")
                        crdnltyLst = crdnltyStr.split("+")

                        for (ctgryName, crdnlty) in zip(ctgryNmLst, crdnltyLst):
                            if ctgryName not in crdnltyDict:
                                crdnltyDict[ctgryName] = crdnlty

                            stndrdCtgrySet.add(ctgryName)

                else:  # 2014-01-07, RPS: verify-->we'll never get here b/c "other" currently hardcoded to "dropdown" type, so can remove

                    # have to determine which categories are in datafile but not in established set of navigation groups
                    # so that we can create an "Other" navigation group for these
                    allCtgriesInDatafile = set(self.__getAllCategoriesInDataFile(p_fileSource, p_dataFile, p_bIsWorkflow))
                    otherCtgries = allCtgriesInDatafile.difference(stndrdCtgrySet)

                    # generate list of otherCtgries so we can sort for display
                    for _n in range(len(otherCtgries)):
                        otherCtgriesLst.append(otherCtgries.pop())
                    otherCtgriesLst.sort()
                    #
                    hdrDict["ctgry_disply_lbls"] = hdrDict["ctgries"] = "+".join(otherCtgriesLst)

                    for ctgryName in otherCtgriesLst:
                        if ctgryName not in crdnltyDict:
                            crdnltyDict[ctgryName] = "unit"
                #

                for idx, (ctgryName, crdnlty) in enumerate(crdnltyDict.items()):
                    separator = ""
                    if idx > 0:
                        separator = ", "
                    crdnltyJavaScriptStr += separator + '"' + ctgryName + '": ' + '"' + crdnlty + '"'
                crdnltyJavaScriptStr += " }"

                hdrMrkp = hdrMrkpTmpltNoDrpDwns % hdrDict

            hdrLst.append(hdrMrkp)

        return "\n".join(hdrLst), crdnltyJavaScriptStr

    def setSessionPaths(self, p_reqObj):
        """Establish absolute/relative paths to be used for storing/accessing session-related data

        :Params:
            ``p_reqObj``: Web Request object
        """
        sessionMgr = p_reqObj.getSessionObj()

        # ### absolute paths ####
        absSessPth = sessionMgr.getPath()
        # absolute path used for referencing session directory content from back end
        self.absltSessionPath = absSessPth

        # ### relative paths #####
        rltvSessPth = sessionMgr.getRelativePath()
        # relative path used for referencing session directory content from front end
        self.rltvSessionPath = rltvSessPth

    def setAbsolutePath(self, absSessPth):
        """Establish absolute path to be used for storing/accessing session-related data

        :Params:
            ``absSessPth``: absolute path
        """
        # absolute path used for referencing session directory content from back end
        self.absltSessionPath = absSessPth

    def isWorkflow(self, p_reqObj):
        """Determine if currently operating in Workflow Managed environment"""
        #
        fileSource = str(p_reqObj.getValue("filesource")).lower()
        #
        if fileSource in ["archive", "wf-archive", "wf_archive", "wf-instance", "wf_instance"]:
            # if the file source is any of the above then we are in the workflow manager environment
            return True
        else:
            # else we are in the standalone dev environment
            return False

    def processTemplate(self, tmpltPth, fn, parameterDict=None):
        """Read the input HTML template data file and perform the key/value substitutions in the
        input parameter dictionary.
        """
        if parameterDict is None:
            parameterDict = {}

        fPath = os.path.join(tmpltPth, fn)
        with open(fPath, "r") as ifh:
            sIn = ifh.read()
        return sIn % parameterDict

    def truncateForDisplay(self, content, maxlength=20, suffix="..."):
        """Obtain truncated version of long identifiers for display purposes (e.g. in comparison panel)"""
        if content is not None:
            if len(content) <= maxlength:
                return content
            else:
                return content[: maxlength + 1] + suffix
        else:
            return ""

    def __generateDropDownMarkup(self, p_ctgries, p_ctgryCrdnlties, p_ctgryDisplNm, p_grpId, p_inputMrkpTmplt, p_index=None, p_ctgryDisplyLbls=None):
        inputMrkp = ""
        hlprDict = {}

        hlprDict["ctgry"] = p_ctgries
        hlprDict["cardinality"] = p_ctgryCrdnlties
        hlprDict["drpdwn_displ_lbl"] = p_ctgryDisplNm
        hlprDict["selectid"] = p_index
        hlprDict["ctgrygrpid"] = p_grpId
        #
        if p_ctgryDisplyLbls:
            hlprDict["ctgry_disply_lbls"] = p_ctgryDisplyLbls
        #
        hlprDict["font_size"] = self.__getFontSize(hlprDict["drpdwn_displ_lbl"])
        #
        inputMrkp = p_inputMrkpTmplt % hlprDict

        return inputMrkp

    def __getFontSize(self, p_displayLabel):
        if len(p_displayLabel) > 35:
            return ".75em"
        elif len(p_displayLabel) > 25:
            return ".8em"
        else:
            return ".9em"
