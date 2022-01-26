##
#
# File:    PdbxDataIo.py
# Author:  R. Sala
# Date:    02-Feb-2012
# Version: 0.001
# Updates:
#    2012-02-02    RPS    Created.
#    2012-04-02    RPS    Updated to address incorrect sequence of calls against PdbxPersist in setItemValue()
#                         Improved handling of cases where datafile being processed does not contain data corresponding
#                         to cif category being requested for display/edit.
#                         Also, corrected errors in applying dictionary metadata in cases of of transposed tables.
#    2012-04-03    RPS    Instantiating PdbxDictionaryInfo only when necessary to improve performance.
#    2012-04-05    RPS    Updated __filterRsltSet() to enable proper maintenance of "true row indices" throughout any
#                            manipulation of row order on front-end.
#                         Corrected instance where PdbxPersist.fetchObject() was being used instead of fetchOneObject()
#    2012-04-06    RPS    Introduced support for adding new record into cif category/DataTable
#    2012-04-09    RPS    Updated to continue processing when cif category in datafile but not found in meta dictionary.
#                         Added attribute to allow enable/disable of transposed tables feature.
#    2012-04-10    RPS    Introduced support for deleting a record.
#    2012-04-16    RPS    Method for filtering resultsets (as per search filter provided in UI) now case-insensitive.
#                         Correction in setItemValue for proper handling in cases of non-transposed vs transposed tables.
#    2012-04-17    RPS    Introduced support for validation of data being submitted as edits to given cif category.attribute
#    2012-04-18    RPS    Updated for more efficient use of PdbxDictionaryInfo object during validation of proposed edits.
#    2012-04-22    RPS    Introduced support for writing out edited cif data to output file.
#    2012-04-23    RPS    Changes in anticipation of integration with WFM environment.
#    2012-04-26    RPS    Corrected errors in handling of "filesource"
#    2012-04-26    RPS    Corrected for redundant instantiation of PdbxIoAdapter for purposes of reading cif datafile
#    2012-04-26    JDW    Updated PDBx dictionary path to a more portable location.  This needs to be obtained from
#                         the configuration class.
#    2012-05-08    RPS    Updated to incorporate boundary checking validation as per John Westbrook code.
#    2012-06-26    RPS    Introduced getDataStorePath() convenience method.
#                         Now copying cif datafiles used for canned examples into session directory for any local processing needs.
#    2012-07-27    RPS    getCategoryRowList() updated to accommodate column specific search filtering
#    2012-07-27    RPS    Now using PdbxDictionaryViewInfo class to obtain config details for customizing user interface.
#    2012-08-21    RPS    Updates required for proper integration with WFM.
#    2012-08-30    RPS    Now getting SITE_CIF_EDITOR_UI_CONFIG_FILE_PATH from ConfigInfoData.
#    2012-08-30    RPS    Now getting SITE_MMCIF_DICT_FILE_PATH from ConfigInfoData.
#    2012-09-25    RPS    Now generating empty placeholders for cif items and/or entire cif categories when corresponding
#                          data is required but not provided in submitted coordinate file.
#    2012-09-27    RPS    Accommodating new context/view config for annotation/AV2.
#    2012-10-18    RPS    Added __getConfigViewId() and supporting new viewID of "AV3" for Entity Fixer purposes.
#    2013-02-12    RPS    Navigation menu changed from vertical accordion style to horizontal toolbar display,
#                         which involved use of pdbx_v2 package instead of pdbx.
#                         Supporting simultaneous display of >1 DataTable.
#                         Enforcing read-only behavior for given items in a cif category as per cif view config file.
#    2013-02-14    RPS    Added functionality to allow for drop-down choices that launch simultaneous viewing of >1 DataTable
#    2013-02-26    RPS    Introduced support for "undo"-ing edits.
#    2013-03-08    RPS    Fixed bug affecting generati of proper column display order during handling of cases where cif category
#                          is not originally in datafile and so must be provided via "skeleton" category generation.
#    2013-03-11    RPS    Updated to accommodate "_ALT" metadata (e.g. for enums, boundary constraints) which is used
#                          in precedence over non-"_ALT" metadata
#    2013-03-15    RPS    Augmented handling of validation so that reason for failure reported back to front end.
#                            Also accommodating different display behavior based on a cif categories row cardinality as specified in
#                            view config file.
#    2013-03-18    RPS    Moved handling of record sorting from EditorDepict.py to this module to correct for erroneous sorting behavior.
#    2013-03-18    RPS    addNewRow() --> piloting strategy of "auto-increment" behavior for 'ordinal' item in 'citation_author" category.
#    2013-03-19    RPS    setItemValue() --> piloting strategy of "auto-increment" behavior on insertions for 'citation_author' and 'audit_author' categories.
#    2013-04-04    RPS    Updated to correct bug in boundary validation logic.
#    2013-04-24    RPS    Introduced support for identifying and checking for "mandatory" cif items (i.e. items that require non-null value).
#                            Augmented handling of boundary validation to discern between "soft" and "hard" limit violations.
#    2013-05-17    RPS    Removed now obsolete code that had been in place for constructing "transposed view" datatables via server-side strategy.
#                             Front-end now bears primary responsibility for doing this.
#    2013-06-04    RPS    Improved handling of "undo" actions. New strategy for handling cardinality constraints.
#    2013-06-20    RPS    getEntryTitle() method added.
#    2013-06-26    RPS    __setMenuConfigTypes() updated to properly handle scenario where toplevel menu choice equates to display of single category.
#    2013-12-04    RPS    Introduced support for viewing all "Other Categories"
#                            Added auto-increment/populate for primary key ordinal IDs when adding new rows/creating skeleton category.
#    2014-02-04    RPS    Added auto-decrement ability for certain ordinal ID fields. Added "entity.id", "entity_poly.entity_id", "struct_ncs_ens.id",
#                            "pdbx_refine_tls_group.id" to list of IDs requiring auto-increment/decrement
#    2014-02-13    RPS    "pdbx_refine_tls_group.id","struct_ncs_ens.id","struct_ncs_dom.id","struct_ncs_dom.pdbx_ens_id","struct_ncs_dom_lim.dom_id",
#                            "struct_ncs_dom_lim.pdbx_component_id","struct_ncs_dom_lim.pdbx_ens_id" now not auto-populated when generating skeletonCategory
#    2014-02-17    RPS    setItemValue() and deleteRow() methods updated to handle non-integer values gracefully when making comparisons needed for ordinal ID
#                            adjustments for auto-incr/decrement operations.
#    2014-02-24    RPS    Added support for handling requests to skip link/site/helix/sheet calculations.
#    2014-03-03    RPS    Now purging rows where all significant items have non-values in cases of certain cif categories.
#    2014-03-11    RPS    Fix required for purging of skeleton rows in situations where > 1 skeleton row exists.
#    2014-03-11    RPS    adding 'diffrn_radiation_wavelength' and 'refine_ls_shell' to list of categories for which skeleton rows are purged.
#    2014-03-12    RPS    adding "pdbx_database_related","database_PDB_caveat" to list of categories for which skeleton rows are purged.
#                            Workaround put in to deal with "pdbx_database_related" being unique when purging skeleton categories in that its single
#                            non-primary key field may in fact be null.
#    2014-03-18    RPS    adding 'pdbx_struct_assembly_prop' to list of categories for which skeleton rows are purged.
#    2014-03-24    RPS    Replacing use of PdbxPyIoAdapter with use of PdbxCoreIoAdapter
#                            Now keeping track of any skeleton categories created so that these can be explicitly cleaned up if still empty after annotator is done.
#    2014-04-02    RPS    Fix bug relating to use of PdbxCoreIoAdapter and handling of int vs string values persisted to database.
#    2014-04-23    RPS    Improved warning messages generated on validation checks against mmCIF dictionary.
#    2014-06-05    RPS    Updated with improved features for providing annotator with information regarding violation of dictionary constraints.
#    2014-06-09    RPS    Added "pdbx_database_PDB_obs_spr.pdb_id", "pdbx_database_PDB_obs_spr.replace_pdb_id" to autoIncrementExclude list.
#    2014-07-09    RPS    Introduced changes that will eventually support "insertRow" functionality, editing of editor view config files, and EM and NMR views.
#    2014-07-16    RPS    Fixed bug in __orderAuthors()
#    2014-07-31    RPS    Implemented special handling for boundary validation of CIF category items that may be in comma separated values list form such as
#                            "diffrn_source.pdbx_wavelength_list" Will add to this list as other such items are encountered.
#    2014-09-04    RPS    Deriving path for EM and NMR editor config files via ConfigInfo class.
#    2014-09-19    RPS    Changed strategy for making snapshots to support rollbacks. An initial zero-index snapshot had already been made when user
#                            action invokes first call to have datatables populated in the browser. The pre-existing zero-index snapshot serves as readily
#                            available initial rollback point, and thus allows us to make snapshots *after* any edit actions so user does not have to wait
#                            for snapshot completion for edit action roundtrip to be completed and allow user to interact with screen again.
#    2014-10-08    RPS    Added "reflns_shell.pdbx_ordinal" to list of items for which ordinal ID field is automatically generated and incremented/decremented
#    2014-12-15    RPS    Added "software.pdbx_ordinal" to list of items for which ordinal ID field is automatically generated and incremented/decremented.
#    2014-12-19    RPS    "unspecified" set as default for "pdbx_database_related" in "__createSkeletonCtgryContainer" context as well.
#    2015-02-06    ZF     Added loading model cif file into da_internal database in doExport function.
#    2015-03-19    RPS    Consolidated code for handling auto-increment/decrement of ordinal IDs
#    2015-03-30    RPS    "struct_ncs_dom.id" no longer handled for auto increment/decrement. And questionable rows in "struct_ncs_dom" no longer automatically
#                            purged on exit from CIF editor session.
#    2015-04-01    RPS    Adding "solvent repositioning" to types of calculations that can be skipped.
#    2015-04-15    RPS    Introducing support for CIF Editor self-Config UI.
#                            Introducing support for different experimental methods.
#    2015-06-12    RPS    Added call to self.__getSortAscColIndex() in getTblConfigDict() to relieve front-end of burden for determining column on which to sort ascending (if any)
#    2015-06-16    RPS    Added self.propagateTitle() for copying title data between "struct" and "citation" categories
#    2015-07-06    RPS    Added self.getEntryAccessionIds() to support handling of different experimental methods
#    2015-09-03    RPS    Incorporating use of wwpdb.apps.editormodule.config.EditorConfig
#    2016-02-29    RPS    Updated to treat "ELECTRON CRYSTALLOGRAPHY" in same manner as "ELECTRON MICROSCOPY" exp method
#    2016-03-02    RPS    __regexValidation() and setItemValue() updated to accommodate handling of unicode characters when allowed per
#                            EditorConfig.itemsAllowingUnicodeAccommodation list
#    2017-02-19    EP     Major changes to move to central configuration file
#    2017-03-29    EP     Correct invocation from entity transformer for building PRD
#    2017-05-22    EP     For regular expression matching - allow per item override to allow gui to accept
#    2017-10-26    EP     Order em_author_list properly
#    2018-06-28    EP     Start to introduce logging.  Provide timing data. Adjust lock retry time on persist storage as was causing bottlenecks.
##
"""
Encapsulates pdbx.persist.PdbxPersist functionality for parsing and manipulating Pdbx cif datafile
data for transport between required sources/destinations
Serves needs for displaying on front-end and
persisting in backend for Pdbx/WFM data storage

"""
__docformat__ = "restructuredtext en"
__author__ = "Raul Sala"
__email__ = "rsala@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import sys
import time
import os
import os.path
import shutil
import re

from mmcif_utils.persist.PdbxPersist import PdbxPersist
from mmcif.io.IoAdapterCore import IoAdapterCore

from wwpdb.utils.config.ConfigInfo import ConfigInfo
from mmcif_utils.persist.PdbxDictionaryInfo import PdbxDictionaryInfo, PdbxDictionaryInfoStore, PdbxDictionaryViewInfo
from wwpdb.apps.editormodule.io.EditorDataImport import EditorDataImport
from wwpdb.apps.editormodule.io.PdbxMasterViewDictionary import PdbxMasterViewDictionary
from wwpdb.apps.editormodule.config.EditorConfig import EditorConfig
from wwpdb.apps.editormodule.config.AccessConfigCifFiles import get_display_view_info_master_cif, get_display_view_info_cif
from wwpdb.utils.db.DBLoadUtil import DBLoadUtil
from mmcif.api.DataCategory import DataCategory
from wwpdb.utils.config.ConfigInfoApp import ConfigInfoAppCommon

import logging

logger = logging.getLogger(__name__)


class PdbxDataIo(object):
    def __init__(self, reqObj, verbose=False, log=sys.stderr):
        self.__reqObj = reqObj
        self.__lfh = log
        self.__verbose = verbose
        self.__debug = False
        self.__editCifViewConfig = False
        self.__defView = None
        self.__defMethodView = None
        self.__retrySeconds = 0.1

        self.__context = str(self.__reqObj.getValue("context"))
        self.__expMethodList = (self.__reqObj.getValue("expmethod").replace('"', "")).split(",") if (len(self.__reqObj.getValue("expmethod").replace('"', "")) > 1) else []
        #
        if self.__verbose and self.__debug:
            for value in self.__expMethodList:
                logger.info("value found in self.__expMethodList: %s", value)
        #
        configFileProvided = self.__reqObj.getValue("configFilePath")
        #
        self.__sObj = self.__reqObj.newSessionObj()
        self.__sessionPath = self.__sObj.getPath()
        #
        self.__cI = ConfigInfo()
        self.__cICommon = ConfigInfoAppCommon()
        #
        self.__pathPdbxDictFile = self.__cICommon.get_mmcif_next_dictionary_file_path()
        #
        logger.info("configFileProvided is: %s", configFileProvided)

        self.__masterPathViewFile = get_display_view_info_master_cif()

        # Sent back to client - and returned...
        defView = self.__reqObj.getValue("defview")
        if self.__verbose:
            logger.info("defview %s", defView)

        if defView:
            self.__setDefMethodView(method=None, view=defView)

        # If configFileProvided is set - use that. Otherwise hardcoded name
        self.__pathViewFile = None
        if configFileProvided and len(configFileProvided) > 1:
            self.__pathViewFile = configFileProvided
        else:
            if self.__context in ["emtesting", "em"]:
                self.__setDefMethodView(method="EM")
            if self.__context in ["nmrtesting", "nmr"]:
                self.__setDefMethodView(method="NMR")
            if self.__context == "editorconfig":
                self.__pathViewFile = "/net/wwpdb_da/da_top/resources/pdbx_display_view_info_CIFEDITOR.cif"
                self.__editCifViewConfig = True
            if self.__context == "entityfix":
                self.__pathViewFile = get_display_view_info_cif()
        #
        if self.__verbose:
            logger.info("path to view config file is: %s", self.__pathViewFile)
            logger.info("path to view __pathPdbxDictFile is: %s", self.__pathPdbxDictFile)
        #
        self.__pdbxDictStore = None
        self.__pathPdbxDataFile = None
        #
        # self.__pdbxReader = None
        self.__containerList = []
        #
        self.__dataBlockName = None
        self.__entryTitle = None
        self.__entryAccessionIdsLst = None
        self.__entryExptlMethodsLst = None
        #
        self.__dbFilePath = os.path.join(self.__sessionPath, "dataFile.db")
        self.__dictDbFilePath = os.path.join(self.__sessionPath, "mmcifDict.db")
        self.__sessionSnapShotsPath = os.path.join(self.__sessionPath, "snapshots")
        ####################################################################
        # below attributes for accommodating "transposed tables" behavior #
        self.__bUseTransposedTables = False
        self.__settingsNeedingColIdxTrnsfrm = [
            "COLUMN_BOUNDARY_VALUES",
            "COLUMN_BOUNDARY_VALUES_ALT",
            "COLUMN_REGEX",
            "COLUMN_REGEX_ALT",
            "COLUMN_ENUMS",
            "COLUMN_ENUMS_ALT",
            "COLUMN_DEFAULT_VALUES",
            "MANDATORY_COLUMNS",
            "MANDATORY_COLUMNS_ALT",
            "COLUMN_DESCRIPTIONS",
            "COLUMN_DESCRIPTIONS_ALT",
            "COLUMN_DISPLAY_ORDER",
            "COLUMN_DISPLAY_NAMES",
            "PRIMARY_KEYS",
            "COLUMN_TYPES",
            "COLUMN_TYPES_ALT",
            "COLUMN_EXAMPLES",
            "COLUMN_EXAMPLES_ALT",
        ]
        #####################################################################################################################################
        #
        self.__skltnLstFlPath = os.path.join(self.__sessionPath, "skeletonCategoryList.txt")
        #
        self.__setup()

    def __setup(self):
        try:
            if os.access(self.__dbFilePath, os.R_OK):
                myPersist = PdbxPersist(self.__verbose, self.__lfh, retrySeconds=self.__retrySeconds)
                myInd = myPersist.getIndex(dbFileName=self.__dbFilePath)
                containerNameList = myInd["__containers__"]
                self.__dataBlockName = containerNameList[0][0]
                if self.__verbose:
                    logger.info("successfully obtained datablock name as: %s, from %s", self.__dataBlockName, self.__dbFilePath)
            self.__setUpSnapShotsArea()

        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                logger.info("problem recovering data into PdbxPersist from db file at: %s", self.__dbFilePath)
            logger.exception("Failure in __setup")

    def __setUpSnapShotsArea(self):
        try:
            if not os.path.isdir(self.__sessionSnapShotsPath):
                os.mkdir(self.__sessionSnapShotsPath, 0o777)
                if os.access(self.__sessionSnapShotsPath, os.R_OK):
                    if self.__verbose:
                        logger.info("dataFileSnapShot area read accessible at: %s", self.__sessionSnapShotsPath)

        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                logger.info("problem creating snapshots area at: %s", self.__sessionSnapShotsPath)
            logger.exception("In setting up snap short area")

    def __setPdbxDataFilePath(self):
        dataFile = str(self.__reqObj.getValue("datafile"))
        fileSource = str(self.__reqObj.getValue("filesource"))
        if self.__verbose:
            logger.info("datafile is:%s", dataFile)
        #
        bIsWorkflow = self.__isWorkflow()
        #
        if bIsWorkflow:
            depDataSetId = self.__reqObj.getValue("identifier")
            if self.__verbose:
                logger.info("Starting.")
                #
                if bIsWorkflow:
                    logger.info("+++ SITE_ID is: %s.", self.__cI.get("SITE_PREFIX"))
                    logger.info("+++ deposition data set id is: %s.", depDataSetId)
            #
            edtrDI = EditorDataImport(self.__reqObj, verbose=self.__verbose, log=self.__lfh)

            # path to file as held in WFM area
            wfmPdbxFilePath = edtrDI.getModelPdxFilePath()
            #
            if self.__verbose:
                logger.info("+++ - model file path  %s", wfmPdbxFilePath)
            # Local path details - i.e. for processing within given session
            lclPdbxFileName = depDataSetId + "-model.cif"
            lclPdbxFilePath = os.path.join(self.__sessionPath, lclPdbxFileName)
            #
            try:
                ############################################################################################################
                # Make local copy of coordinate file
                ############################################################################################################
                if wfmPdbxFilePath is not None and os.access(wfmPdbxFilePath, os.R_OK):
                    shutil.copyfile(wfmPdbxFilePath, lclPdbxFilePath)
                    self.__pathPdbxDataFile = lclPdbxFilePath
                #
            except:  # noqa: E722 pylint: disable=bare-except
                if self.__verbose:
                    logger.info("+++- pre-processing of pdbx data file %s, failed for deposition id:  %s", self.__pathPdbxDataFile, depDataSetId)
                    logger.exception("Setting pdbxModelPath")
        else:  # non-"workflow" processsing
            if dataFile:
                sessionFilePath = os.path.join(self.__sessionPath, dataFile)
                #
                if fileSource and fileSource == "rcsb_dev":
                    # make copy of file in sessions directory for any access/processing required by front-end
                    devDataExamplesPath = os.path.join("/wwpdb/source/python/wwpdb/apps/editormodule/data/", dataFile)
                    shutil.copyfile(devDataExamplesPath, sessionFilePath)
                #
                self.__pathPdbxDataFile = sessionFilePath

        logger.info("+++- pdbx data file path is: %s", self.__pathPdbxDataFile)

    def getPdbxDataFilePath(self):
        if self.__pathPdbxDataFile is not None and os.access(self.__pathPdbxDataFile, os.R_OK):
            return self.__pathPdbxDataFile
        else:
            dataFile = str(self.__reqObj.getValue("datafile"))
            if self.__verbose:
                logger.info("-- datafile is:%s", dataFile)
            #
            bIsWorkflow = self.__isWorkflow()
            #
            if bIsWorkflow:
                depDataSetId = self.__reqObj.getValue("identifier")
                if self.__verbose:
                    logger.info("+++Starting.")
                    #
                    if bIsWorkflow:
                        logger.info("SITE_ID is: %s.", self.__cI.get("SITE_PREFIX"))
                        logger.info("deposition data set id is: %s.", depDataSetId)
                #
                # Local path details - i.e. for processing within given session
                lclPdbxFileName = depDataSetId + "-model.cif"
                lclPdbxFilePath = os.path.join(self.__sessionPath, lclPdbxFileName)
                #
                if os.access(lclPdbxFilePath, os.R_OK):
                    self.__pathPdbxDataFile = lclPdbxFilePath
                    return self.__pathPdbxDataFile
                else:
                    logger.error("could not find/access pdbx data file path at: %s", lclPdbxFilePath)
                    return None

            # Should never get here
            logger.info("Leaving and pdbx data file path is: %s", self.__pathPdbxDataFile)
            return self.__pathPdbxDataFile

    def initializeDataStore(self):
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        self.__setPdbxDataFilePath()
        #
        try:
            #########################################################################################################
            # parse model cif file and determine blockname
            #########################################################################################################
            if self.__pathPdbxDataFile is not None and os.access(self.__pathPdbxDataFile, os.R_OK):
                pdbxReader = IoAdapterCore(verbose=self.__verbose)
                self.__containerList = pdbxReader.readFile(inputFilePath=self.__pathPdbxDataFile, enforceAscii=True)

                iCountNames = len(self.__containerList)
                assert iCountNames == 1, "initializeDataStore -- expecting containerNameList to have single member but list had %s members" % iCountNames
                #
                if sys.version_info[0] < 3:
                    self.__dataBlockName = self.__containerList[0].getName().encode("utf-8")
                else:
                    self.__dataBlockName = self.__containerList[0].getName()
                logger.info("Datablock name %r", self.__dataBlockName)
                logger.info("--------------------------------------------")
                logger.info("identified datablock name %s in sample pdbx data file at: %s", self.__dataBlockName, self.__pathPdbxDataFile)
                #
            else:
                if self.__verbose:
                    logger.info("pdbx data file not found/accessible at: %s", self.__pathPdbxDataFile)
        #
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                logger.error("problem processing pdbx data file at: %s", self.__pathPdbxDataFile)
            logger.exception("problem processing file")

        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            myPersist.setContainerList(self.__containerList)
            myPersist.store(self.__dbFilePath)

            if self.__verbose:
                logger.info("shelved cif data to %s", self.__dbFilePath)
            if self.__editCifViewConfig:
                self.__entryTitle = ""
            else:
                self.__entryTitle = self.getEntryTitle(myPersist)
                self.__entryAccessionIdsLst = self.getEntryAccessionIds(myPersist)
                self.__entryExptlMethodsLst = self.__getEntryExptlList(myPersist)

        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("In shelving")

        return self.__dataBlockName, self.__entryTitle, self.__entryAccessionIdsLst

    def getEntryAccessionIds(self, p_pdbxPersist):

        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        accessionIdsLst = []
        try:
            ctgryObj = p_pdbxPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, "pdbx_depui_entry_details")
            #
            if ctgryObj:
                fullRsltSet = ctgryObj.getRowList()
                iTotalRecords = len(fullRsltSet)

                if self.__verbose and self.__debug:
                    logger.info("fullRsltSet obtained as: %r", fullRsltSet)

                assert iTotalRecords == 1, " getEntryAccesionIds expecting 'pdbx_depui_entry_details' category to contain a single record but had %s records" % iTotalRecords
                ctgryColList = (self.getCategoryColList("pdbx_depui_entry_details"))[1]
                if self.__verbose and self.__debug:
                    logger.info("ctgryColList obtained as: %r", ctgryColList)
                #
                for idx, name in enumerate(ctgryColList):

                    if name == "requested_accession_types":
                        if self.__verbose and self.__debug:
                            logger.info("found 'requested_accession_types' field at index: %s with value: %s", idx, (fullRsltSet[0])[idx])
                        accessionIdsLst = (fullRsltSet[0][idx]).split(",")
                        break

                logger.info("accessionIdsLst obtained as: %r", accessionIdsLst)

        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("Getting requested accession codes")

        return accessionIdsLst

    def getEntryTitle(self, p_pdbxPersist):
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        entryTitle = ""
        try:
            ctgryObj = p_pdbxPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, "struct")
            #
            if ctgryObj:
                fullRsltSet = ctgryObj.getRowList()
                iTotalRecords = len(fullRsltSet)

                if self.__verbose and self.__debug:
                    logger.info("fullRsltSet obtained as: %r", fullRsltSet)

                assert iTotalRecords == 1, "expecting 'struct' category to contain a single record but had %s records" % iTotalRecords
                ctgryColList = (self.getCategoryColList("struct"))[1]
                if self.__verbose and self.__debug:
                    logger.info("ctgryColList obtained as: %r", ctgryColList)
                #
                for idx, name in enumerate(ctgryColList):

                    if name == "title":
                        if self.__verbose and self.__debug:
                            logger.info("found 'title' field at index: %s with value: %s", idx, (fullRsltSet[0])[idx])
                        entryTitle = fullRsltSet[0][idx]
                        break

                logger.info("entryTitle obtained as: '%s'", entryTitle)
            else:
                if self.__verbose:
                    logger.info("'struct' category not present in the model data file")
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("Failure retreiving title")

        return entryTitle

    def __getEntryExptlList(self, p_pdbxPersist):

        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        exptlLst = []
        try:
            ctgryObj = p_pdbxPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, "exptl")
            #
            if ctgryObj:
                if ctgryObj.hasAttribute("method"):
                    idMethod = ctgryObj.getIndex("method")

                    for row in ctgryObj.getRowList():
                        method = row[idMethod]
                        exptlLst.append(method)

                logger.info("exptlLst obtained as: %r", exptlLst)
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("Failure to get experimental methods")

        return exptlLst

    def __setDefMethodView(self, method=None, view=None):
        """Sets the default view/method for the session"""
        if method:
            self.__defMethodView = method
        if view:
            self.__defView = view

    def getDefView(self):
        """Returns the default view to pass back to client"""
        return self.__defView

    def makeDataStoreSnapShot(self, p_editActnIndx):
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        snapShotFilePath = os.path.join(self.__sessionSnapShotsPath, "dataFileSnapShot_" + str(p_editActnIndx) + ".db")
        if int(p_editActnIndx) == 0:
            if self.__verbose and self.__debug:
                logger.info("-- p_editActnIndx is:  %s", p_editActnIndx)

            if os.access(snapShotFilePath, os.R_OK):
                if self.__verbose:
                    logger.info("skipping over creation of zero-index dataFileSnapShot b/c already exists at:  %s", snapShotFilePath)
                return
            else:
                if self.__verbose:
                    logger.info("zero-index dataFileSnapShot does not yet exist at:  %s", snapShotFilePath)
        #
        try:
            if self.__dbFilePath is not None and os.access(self.__dbFilePath, os.R_OK):
                if self.__sessionSnapShotsPath is not None and os.access(self.__sessionSnapShotsPath, os.R_OK):

                    shutil.copyfile(self.__dbFilePath, snapShotFilePath)

                    if os.access(snapShotFilePath, os.R_OK):
                        if self.__verbose:
                            logger.info("dataFileSnapShot successfully created at: %s", snapShotFilePath)
                    else:
                        if self.__verbose:
                            logger.info("problem creating dataFileSnapShot at: %s", snapShotFilePath)
        #
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                logger.info("problem creating dataFileSnapShot at: %s", snapShotFilePath)
            logger.exception("In making snaphot")

    def purgeDataStoreSnapShots(self, p_rewindIndex=None):
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        if self.__sessionSnapShotsPath is not None and os.access(self.__sessionSnapShotsPath, os.R_OK):
            if p_rewindIndex:
                snpShotFilePath = os.path.join(self.__sessionSnapShotsPath, "dataFileSnapShot_" + str(p_rewindIndex) + ".db")
                try:
                    if os.path.isfile(snpShotFilePath):
                        os.remove(snpShotFilePath)
                except:  # noqa: E722 pylint: disable=bare-except
                    if self.__verbose:
                        logger.info("problem removing dataFileSnapShot: %s", snpShotFilePath)
                    logger.exception("Failure in removal of snapshot")
            else:
                for snpShotFile in os.listdir(self.__sessionSnapShotsPath):
                    snpShotFilePath = os.path.join(self.__sessionSnapShotsPath, snpShotFile)
                    try:
                        if os.path.isfile(snpShotFilePath):
                            os.remove(snpShotFilePath)
                    except:  # noqa: E722 pylint: disable=bare-except
                        if self.__verbose:
                            logger.info("problem removing dataFileSnapShot at: %s", snpShotFilePath)
                        logger.exception("Issue removing dataFileSnapShot")
        else:
            if self.__verbose:
                logger.info("dataFileSnapShots directory not accessible at: %s", self.__sessionSnapShotsPath)

    def getDataStorePath(self):
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        try:
            if self.__dbFilePath is not None and os.access(self.__dbFilePath, os.R_OK):
                if self.__verbose:
                    logger.info("spersistent dataStore DB file accessible at %s", self.__dbFilePath)
                return self.__dbFilePath

            else:
                if self.__verbose:
                    logger.info("persistent dataStore DB file not found/accessible at %s", self.__dbFilePath)
                return None

        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("Failure in getDataStorePath")

    def initializeDictInfoStore(self):
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        try:
            pda = PdbxDictionaryInfo(dictPath=self.__pathPdbxDictFile, verbose=self.__verbose, log=self.__lfh)
            dInfo = pda.assembleByAttribute()
            #
            vda = PdbxDictionaryViewInfo(viewPath=self.__pathViewFile, verbose=self.__verbose, log=self.__lfh)

            # Override for default cases
            if self.__pathViewFile is None:
                dV = PdbxMasterViewDictionary()
                dV.read(self.__masterPathViewFile)
                # Set the experimental method
                if self.__defMethodView:
                    methods = self.__defMethodView
                else:
                    methods = dV.methodsToView(self.__entryExptlMethodsLst)

                viewContainer = dV.generateMethodsView(methods)
                # Fall back to a known config if unknown
                if not viewContainer:
                    logger.info("method not found in config: %s", methods)
                    methods = "X-RAY"
                    viewContainer = dV.generateMethodsView(methods)

                # Get default view
                view = dV.getDefaultViewName(methods)
                self.__setDefMethodView(method=methods, view=view)

                if viewContainer is not None:
                    vda.setFromViewContainer(viewContainer)
                #
            vInfo = vda.get()
            #
            self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)
            self.__pdbxDictStore.store(dbFileName=self.__dictDbFilePath, od=dInfo, ov=vInfo)

            if self.__verbose:
                logger.info("shelved dictionary of cif metadata to %s", self.__dictDbFilePath)

        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("in initializeDictInfoStore")

    def doExport(self, exprtDirPath, exprtFilePath):
        """Export updated cif data as file

        :Params:

            + ``exprtDirPath``: path indicating target directory destination
            + ``exprtFilePath``: path and filename indicating target file destination
        """
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        try:
            if os.access(self.__dbFilePath, os.R_OK) and os.access(exprtDirPath, os.R_OK):
                myPersist = PdbxPersist(self.__verbose, self.__lfh)

                self.__purgeSkeletonRows(myPersist)
                self.__orderAuthors("audit_author", myPersist)
                self.__orderAuthors("citation_author", myPersist)
                self.__orderAuthors("em_author_list", myPersist)
                myPersist.recover(self.__dbFilePath)
                #
                myWriter = IoAdapterCore(verbose=self.__verbose)
                cList = myPersist.getContainerList()
                success = myWriter.writeFile(outputFilePath=exprtFilePath, containerList=cList)
                #
                if success is not None and success is False:
                    if self.__verbose:
                        logger.info(" -- WARNING: problem exporting updated cif file to %s", exprtFilePath)
                    return False

                else:
                    # 2015-02-06, ZF -- loading archive model cif file into da_internal database
                    fileSource = str(self.__reqObj.getValue("filesource")).strip().lower()
                    if fileSource in ["archive", "wf-archive", "wf_archive"]:
                        dbLoader = DBLoadUtil(reqObj=self.__reqObj, verbose=self.__verbose, log=self.__lfh)
                        dbLoader.doLoading([exprtFilePath])
                    # ZF, end DB loading
                    if self.__verbose:
                        logger.info("-- exported updated cif file to %s", exprtFilePath)
                    return True
                #
            else:
                return False
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                logger.info("-- export of updated cif file to %s FAILED.", exprtFilePath)
            logger.exception("Exporting model")

    def getCtgryNavConfig(self):
        """get list of navigation menu config settings"""
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        configList = []
        #
        currViewId = self.__getConfigViewId()

        if not self.__pdbxDictStore:
            self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)

        rView = self.__pdbxDictStore.fetchViewObject(dbFileName=self.__dictDbFilePath)
        dictViewInfo = PdbxDictionaryViewInfo(viewPath=None, verbose=self.__verbose, log=self.__lfh)
        dictViewInfo.set(viewObj=rView)
        #
        topLevelMenuList = dictViewInfo.getDisplayMenuList(viewId=currViewId)
        # topLevelMenuList corresponds to values in "pdbx_display_view_category_info.category_menu_display_name" for the given view ID, serve as primary headings
        logger.info("-- topLevelMenuList obtained as %r", topLevelMenuList)
        # e.g. +PdbxDataIo.getCtgryNavConfig() -- topLevelMenuList obtained as ['Deposition', 'Related DB/Entry', 'Citation', 'Caveat', 'Entity Description',
        #                      'Polymer Source', 'Data Collection', 'Reflection/Refinement Data']

        menuTypeDict = self.__setMenuConfigTypes(currViewId, topLevelMenuList, dictViewInfo)

        for indx, topLevelMenuChoice in enumerate(topLevelMenuList):
            configDict = {}
            dropDwnDisplLst = []
            noDropDwnDict = {}
            menuType = menuTypeDict[topLevelMenuChoice]
            #
            configDict["id"] = indx
            configDict["dsply_lbl"] = topLevelMenuChoice
            configDict["dsply_typ"] = menuType
            #
            descriptors = dictViewInfo.getCategoryGroupListInMenu(viewId=currViewId, menuName=topLevelMenuChoice)
            # descriptors is a list of display-friendly labels for subheadings when dropdown choices under primary heading are desired

            if menuType == "dropdown":
                # in case of "dropdown" menu types, we use descriptors list as list of labels for the dropdown choices
                for idx, dropDwnLbl in enumerate(descriptors):

                    if idx > 0 and (dropDwnLbl == descriptors[idx - 1]):
                        continue

                    categoryDict = {}

                    # getting list of categories (in user-friendly display label form)
                    ctgryDisplLbls = dictViewInfo.getDisplayCategoryListInGroup(viewId=currViewId, menuName=topLevelMenuChoice, groupName=dropDwnLbl)

                    for ctgryDisplLbl in ctgryDisplLbls:
                        # in this for-loop will only get more than one ctgryDisplLbl if there is a "combined" display of > 1 cif category for the given dropDwnLbl
                        ctgryNm = dictViewInfo.getCategoryName(viewId=currViewId, menuName=topLevelMenuChoice, categoryGroupName=dropDwnLbl, categoryDisplayName=ctgryDisplLbl)
                        ctgryCrdnlty = dictViewInfo.getCategoryCardinality(
                            viewId=currViewId, menuName=topLevelMenuChoice, categoryGroupName=dropDwnLbl, categoryDisplayName=ctgryDisplLbl
                        )
                        categoryDict[ctgryDisplLbl] = (ctgryNm, ctgryCrdnlty)

                    dropDwnDisplLst.append((dropDwnLbl, categoryDict))

                #
                configDict["dropdown_display_labels"] = dropDwnDisplLst
            #
            elif menuType == "no_dropdown":
                # in case of "nodropdown" menu types, items in descriptors list serve only as keys to get corresponding category names (values can serve as user-friendly labels)
                for memberLbl in descriptors:
                    ctgryLst = ""
                    ctgryDsplNmLst = ""
                    ctgryCrdnltyLst = ""

                    # getting list of categories (in user-friendly display label form)
                    ctgryDisplLbls = dictViewInfo.getDisplayCategoryListInGroup(viewId=currViewId, menuName=topLevelMenuChoice, groupName=memberLbl)

                    for idx, ctgryDisplLbl in enumerate(ctgryDisplLbls):
                        separator = ""
                        if idx > 0:
                            separator = "+"
                        ctgryNm = dictViewInfo.getCategoryName(viewId=currViewId, menuName=topLevelMenuChoice, categoryGroupName=memberLbl, categoryDisplayName=ctgryDisplLbl)
                        ctgryCrdnlty = dictViewInfo.getCategoryCardinality(
                            viewId=currViewId, menuName=topLevelMenuChoice, categoryGroupName=memberLbl, categoryDisplayName=ctgryDisplLbl
                        )

                        ctgryLst += separator + ctgryNm
                        ctgryDsplNmLst += separator + ctgryDisplLbl
                        ctgryCrdnltyLst += separator + ctgryCrdnlty

                    key = ctgryDsplNmLst.replace(" ", "%20")  # use urlencode style
                    noDropDwnDict[key] = (ctgryLst, ctgryCrdnltyLst)
                #
                configDict["no_dropdown_dict"] = noDropDwnDict

            configList.append(configDict)
        #
        if self.__debug:
            logger.info("-- navigation menu configList obtained as %r", configList)
            # """ e.g. +PdbxDataIo.getCtgryNavConfig() -- navigation menu configList obtained as
            #  [
            #     {'no_dropdown_dict': {'Title+Entry%20status+Entry%20Authors+Contact%20Authors+Processing%20notes': ('struct+pdbx_database_status+audit_author+pdbx_contact_author+pdbx_database_proc', 'unit+unit+multi+multi+multi')},  # noqa:E501
            #      'id': 0,
            #      'dsply_lbl': 'Deposition',
            #      'dsply_typ': 'no_dropdown'},

            #     {'no_dropdown_dict': {'Related%20Entries+TargetTrack+SG%20Project+Methods%20Development': ('pdbx_database_related+entity_poly+pdbx_SG_project+pdbx_database_status', 'multi+multi+multi+multi')},  # noqa:E501
            #      'id': 1,
            #      'dsply_lbl': 'Related DB/Entry',
            #      'dsply_typ': 'no_dropdown'},

            #     {'no_dropdown_dict': {'Citation+Citation%20Authors+Entry%20Authors': ('citation+citation_author+audit_author', 'multi+multi+multi')},
            #      'id': 2,
            #      'dsply_lbl': 'Citation',
            #      'dsply_typ': 'no_dropdown'},

            #     {'no_dropdown_dict': {'Caveat': ('database_PDB_caveat', 'multi')},
            #      'id': 3,
            #      'dsply_lbl': 'Caveat',
            #      'dsply_typ': 'no_dropdown'},

            #     {'no_dropdown_dict': {'Entity%20Description+Polymer%20Synonym+Entity%20Chain+Entity%20Mapping+Depositor%20Entity%20Mapping+Struct%20Keywords+Other%20Details+Entity%20Features+Title': ('entity+entity_name_com+entity_poly+struct_ref+pdbx_struct_ref_seq_depositor_info+struct_keywords+pdbx_entry_details+pdbx_depui_entity_features+struct', 'multi+multi+multi+multi+multi+multi+multi+multi+unit')},  # noqa:E501
            #      'id': 4,
            #      'dsply_lbl': 'Entity Description',
            #      'dsply_typ': 'no_dropdown'},

            #     {'no_dropdown_dict': {'Genetically%20Engineered+Naturally%20Obtained+Synthesized': ('entity_src_gen+entity_src_nat+pdbx_entity_src_syn', 'multi+multi+multi')},
            #      'id': 5,
            #      'dsply_lbl': 'Polymer Source',
            #      'dsply_typ': 'no_dropdown'},

            #     {'no_dropdown_dict': {'exptl_crystal_grow+exptl_crystal+Temperature+diffrn_source+diffrn_radiation+diffrn_radiation_wavelength+Detector+Software': ('exptl_crystal_grow+exptl_crystal+diffrn+diffrn_source+diffrn_radiation+diffrn_radiation_wavelength+diffrn_detector+software', 'multi+multi+multi+multi+multi+multi+multi+multi')},  # noqa:E501
            #      'id': 6,
            #      'dsply_lbl': 'Data Collection',
            #      'dsply_typ': 'no_dropdown'},

            #     {'no_dropdown_dict': {'Overall%20Data+Highest%20Resolution%20Shell+Overall%20Refinement%20Data+Highest%20Resolution%20Refinement%20Shell': ('reflns+reflns_shell+refine+refine_ls_shell', 'unit+multi+multi+multi')},  # noqa:E501
            #      'id': 7,
            #      'dsply_lbl': 'Reflection/Refinement Data',
            #      'dsply_typ': 'no_dropdown'}

            # ]
            # """
        #

        return configList

    def __getCurrentSkeletonCategories(self):
        skltnCtgryLst = []

        if os.access(self.__skltnLstFlPath, os.R_OK):
            try:
                ifh = open(self.__skltnLstFlPath, "r")
                for line in ifh:
                    ctgryName = line.strip()
                    if ctgryName not in skltnCtgryLst:
                        if self.__verbose:
                            logger.info("-- Adding category '%s' to skltnCtgryLst, %r", ctgryName, skltnCtgryLst)
                        skltnCtgryLst.append(ctgryName)
                ifh.close()
            except:  # noqa: E722 pylint: disable=bare-except
                logger.exception("Unknown error __getCurrentSkeletonCategories")
        #
        return skltnCtgryLst

    def checkForMandatoryItems(self):
        """get list of category.items which are mandatory but which are currently missing non-null values"""
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        myPersist = PdbxPersist(self.__verbose, self.__lfh)
        #
        categoryList = []
        missingMndtryItemsDict = {"violation_map": {}}
        categoryHndldList = []
        #
        ctgryRqstd = self.__reqObj.getValue("cifctgry")
        #
        categoryList = self.__getCategoryListForCurrentContext()
        #
        skltnCtgryList = self.__getCurrentSkeletonCategories()
        #
        for curCtgryNm, ctgryDisplLbl, topLevelMenuChoice in categoryList:

            # proceed only if haven't handled the category and category is not one of the artificial skeleton constructs
            if curCtgryNm not in categoryHndldList and curCtgryNm not in skltnCtgryList:
                categoryHndldList.append(curCtgryNm)

                if (ctgryRqstd != "all" and ctgryRqstd == curCtgryNm) or (ctgryRqstd == "all"):
                    ctgryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, curCtgryNm)
                    if ctgryObj:
                        bFoundViolation = False
                        newViolMapDict = {"top_menu_label": "", "col_names": [], "data_positions": [], "violation_msgs": []}

                        # get cif meta data from dictionary
                        catObjDict = self.getTblConfigDict(curCtgryNm, ctgryDisplLbl)
                        ctgryColList = (self.getCategoryColList(curCtgryNm))[1]
                        mandatoryColLst = (
                            catObjDict["MANDATORY_COLUMNS_ALT"]
                            if (catObjDict["MANDATORY_COLUMNS_ALT"] and len(catObjDict["MANDATORY_COLUMNS_ALT"]) > 0)
                            else catObjDict["MANDATORY_COLUMNS"]
                            if (catObjDict["MANDATORY_COLUMNS"] and len(catObjDict["MANDATORY_COLUMNS"]) > 0)
                            else []
                        )

                        if self.__debug:
                            logger.debug("-- mandatoryColLst for %s obtained as %r", curCtgryNm, mandatoryColLst)
                        #
                        fullRsltSet = ctgryObj.getRowList()
                        #
                        for colIdx in mandatoryColLst:
                            for rowIdx, record in enumerate(fullRsltSet):
                                try:
                                    if record[colIdx] and (len(record[colIdx]) < 1 or record[colIdx] == "?"):
                                        colDisplName = catObjDict["COLUMN_DISPLAY_NAMES"].get(colIdx, ctgryColList[colIdx])
                                        if self.__debug:
                                            logger.debug("---- DEBUG ---- Missing non-null value for mandatory item %s in category %s", colDisplName, curCtgryNm)
                                        #
                                        if len(newViolMapDict["top_menu_label"]) < 1:
                                            newViolMapDict["top_menu_label"] = topLevelMenuChoice

                                        if colDisplName not in newViolMapDict["col_names"]:
                                            newViolMapDict["col_names"].append(colDisplName)

                                        newViolMapDict["data_positions"].append((rowIdx, colIdx))

                                        bFoundViolation = True

                                        if self.__debug:
                                            logger.debug(
                                                "--- DEBUG ---- Current rowIdx is '%s', colIdx is '%s', and missingMndtryItemsDict is now '%r'",
                                                rowIdx,
                                                colIdx,
                                                missingMndtryItemsDict,
                                            )

                                except:  # noqa: E722 pylint: disable=bare-except

                                    logger.info(
                                        "---- DEBUG ---- EXCEPTION: Current rowIdx is '%s', colIdx is '%s', and length of record is '%s' for category '%s'",
                                        rowIdx,
                                        colIdx,
                                        len(record),
                                        curCtgryNm,
                                    )
                                    logger.info("---- DEBUG ---- EXCEPTION: record is '%r'", record)
                                    logger.exception("checkMandatoryItems filauire")
                        #
                        if bFoundViolation:
                            missingMndtryItemsDict["violation_map"][curCtgryNm] = newViolMapDict

                    else:
                        if self.__debug:
                            logger.debug("---- DEBUG ---- category '%s' not found in deposited data", curCtgryNm)
        #
        return missingMndtryItemsDict

    def __getCategoryListForCurrentContext(self):

        currViewId = self.__getConfigViewId()

        categoryList = []

        if not self.__pdbxDictStore:
            self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)

        rView = self.__pdbxDictStore.fetchViewObject(dbFileName=self.__dictDbFilePath)
        dictViewInfo = PdbxDictionaryViewInfo(viewPath=None, verbose=self.__verbose, log=self.__lfh)
        dictViewInfo.set(viewObj=rView)
        #
        topLevelMenuList = dictViewInfo.getDisplayMenuList(viewId=currViewId)
        logger.info("-- topLevelMenuList obtained as %r", topLevelMenuList)
        #
        for topLevelMenuChoice in topLevelMenuList:

            descriptors = dictViewInfo.getCategoryGroupListInMenu(viewId=currViewId, menuName=topLevelMenuChoice)
            # descriptors is a list of display-friendly labels for user selections

            for idx, memberLbl in enumerate(descriptors):

                if idx > 0 and memberLbl == descriptors[idx - 1]:
                    continue

                # getting list of categories (in user-friendly display label form)
                ctgryDisplLbls = dictViewInfo.getDisplayCategoryListInGroup(viewId=currViewId, menuName=topLevelMenuChoice, groupName=memberLbl)

                for ctgryDisplLbl in ctgryDisplLbls:
                    ctgryNm = dictViewInfo.getCategoryName(viewId=currViewId, menuName=topLevelMenuChoice, categoryGroupName=memberLbl, categoryDisplayName=ctgryDisplLbl)
                    if ctgryNm not in categoryList:
                        categoryList.append((ctgryNm, ctgryDisplLbl, topLevelMenuChoice))
        #
        if self.__debug:
            logger.debug("-- categoryList obtained as %r", categoryList)
        return categoryList

    def getTblConfigDict(self, p_categoryNm, p_catDispLabel):
        """get dictionary of config settings for DataTable as defined via col index mappings

        :param `p_categoryNm`:  name of cif category
        :param `p_catDispLabel`:  display label used for the cif category and which may differ depending on current view context
                                    this parameter relates to UI config

        """

        start = time.time()

        logger.info("---------------------------------")
        logger.info("Starting for %s %s at %s", p_categoryNm, p_catDispLabel, time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        currViewId = self.__getConfigViewId()
        #
        if self.__verbose and self.__debug:
            logger.debug("  -- currViewId established as %s", currViewId)
        #
        configDict = {}
        #

        bOk, truCtgryColList = self.getCategoryColList(p_categoryNm)
        #
        if bOk:
            if not self.__pdbxDictStore:
                self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)

            ctgryMetaDict = self.__getCifCtgryMetaDict(p_categoryNm)

            # 2014-06-01: config keys currently supplied by PdbxDictionaryInfo class
            # COLUMN_BOUNDARY_VALUES = {}
            # COLUMN_BOUNDARY_VALUES_ALT = {}
            # COLUMN_DEFAULT_VALUES = {}
            # COLUMN_DESCRIPTIONS = {}
            # COLUMN_DESCRIPTIONS_ALT = {}
            # COLUMN_DISPLAY_NAMES = []
            # COLUMN_DISPLAY_ORDER = []
            # COLUMN_ENUMS = {}
            # COLUMN_ENUMS_ALT = {}
            # COLUMN_EXAMPLES = {}
            # COLUMN_EXAMPLES_ALT = {}
            # COLUMN_NAMES = []
            # COLUMN_REGEX = {}
            # COLUMN_REGEX_ALT = {}
            # COLUMN_TYPES = {}
            # COLUMN_TYPES_ALT = {}
            # DISPLAY_NAME = ''
            # MANDATORY_COLUMNS = []
            # MANDATORY_COLUMNS_ALT = []
            # PRIMARY_KEYS = []
            #
            if ctgryMetaDict:
                # if self.__verbose:
                #     logger.debug("-- ctgryMetaDict obtained as %r" % ctgryMetaDict.items())

                # here is where we begin configuring the "view" behavior based on what is in the view config file
                rView = self.__pdbxDictStore.fetchViewObject(dbFileName=self.__dictDbFilePath)
                dictViewInfo = PdbxDictionaryViewInfo(viewPath=None, verbose=self.__verbose, log=self.__lfh)
                dictViewInfo.set(viewObj=rView)

                #
                itemList = dictViewInfo.getItemList(viewId=currViewId, categoryDisplayName=p_catDispLabel, categoryName=p_categoryNm)
                # """ the itemList we get back above is derived from the config file
                #     and the view config file lists the cif items in order of desired display
                #     thus, in the itemList we now have a list of fully qualified cif item names in the order of desired display
                # """
                if len(itemList) > 0:
                    colNameList = []
                    #
                    if self.__verbose and self.__debug:
                        logger.info("-- itemList obtained as %r", itemList)
                    #
                    colDisplNameDict = {}
                    colReadOnlyFlgDict = {}
                    for itm in itemList:
                        # NOTE: itm is supplied by dictViewInfo as fully qualified [category_name].[category_attrib_name]
                        displNm = dictViewInfo.getItemDisplayName(viewId=currViewId, categoryDisplayName=p_catDispLabel, categoryName=p_categoryNm, itemName=itm)
                        attribName = self.__attributePart(itm)
                        colDisplNameDict[attribName] = displNm
                        colNameList.append(attribName)

                        readOnlyFlg = dictViewInfo.getItemReadOnlyFlag(viewId=currViewId, categoryDisplayName=p_catDispLabel, categoryName=p_categoryNm, itemName=itm)
                        colReadOnlyFlgDict[attribName] = readOnlyFlg
                    #
                    if self.__verbose:
                        logger.info("-- colDisplNameDict obtained as %r", list(colDisplNameDict.items()))
                    #
                    ctgryMetaDict["COLUMN_DISPLAY_ORDER"] = colNameList
                    ctgryMetaDict["COLUMN_DISPLAY_NAMES"] = colDisplNameDict
                    #
                    # NOTE: COLUMN_READ_ONLY_FLAG is key that the PdbxDataIo class is adding,
                    # i.e. not originally in the dictionary obtained from PdbxDictionaryInfoStore
                    ctgryMetaDict["COLUMN_READ_ONLY_FLAG"] = colReadOnlyFlgDict

                    if self.__verbose and self.__debug:
                        logger.info("-- ctgryMetaDict['COLUMN_DISPLAY_ORDER'] now is %r", ctgryMetaDict["COLUMN_DISPLAY_ORDER"])

                # now that we have list of attributes actually in the data via "truCtgryCollist" and expected display attributes via
                # ctgryMetaDict['COLUMN_DISPLAY_ORDER'], we can check if the deposited data did not contain attributes that annotator expects to see
                # and if so, generate empty value placeholders for the items in question
                ok = self.__generateMissingCtgryItems(p_categoryNm, truCtgryColList, ctgryMetaDict["COLUMN_DISPLAY_ORDER"])
                #

                if self.__debug:
                    logger.info("-- new truCtgryColList now: %r", truCtgryColList)
                    logger.info("-- success flag returned by __generateMissingCtgryItems is: %s", ok)

                ctgryMetaDict["COLUMN_DISPLAY_ORDER_AS_ITEM_NAMES"] = truCtgryColList
                ctgryMetaDict["SORT_ASC_COL_IDX"] = self.__getSortAscColIndex(p_categoryNm, truCtgryColList)

                # the meta dictionary for the category may have meta information for a given column currently encoded such that the given column
                # is referred to by textual name of the column, but the front-end needs to deal with the mappings via numerical positions of the columns
                # so we perform the necessary translation of textual descriptor to numerical index in the below block
                for key, data in ctgryMetaDict.items():
                    if key in self.__settingsNeedingColIdxTrnsfrm:
                        configDict[key] = self.__convertNamesToColIndxs(truCtgryColList, data)
                    else:
                        configDict[key] = data
                #
                # CONSIDER THIS POINT IN THE CODE FOR ADDITION OF SUPPLEMENTAL COLUMNS TO SUPPORT
                # "ADD-ON" FUNCTIONALITY NOT PROVIDED OUT OF BOX BY DATATABLES

                #
                if self.__debug:
                    logger.info("-- new configDict generated as %r", list(configDict.items()))
                #
            else:
                if self.__verbose:
                    logger.info("-- WARNING: no metaDict was available for '%s' so generating a dummy DataTable config stub for use by front end.", p_categoryNm)
                # generate a dummy DataTable config dictionary
                configDict = self.__getDataTblCnfgStub(truCtgryColList)

                # RPS, 2014-01-08: BELOW IS TEMPORARY CODE FOR PROTOTYPING SELF CONFIG UI
                if p_categoryNm == "pdbx_display_view_category_info":
                    configDict["COLUMN_DISPLAY_ORDER"] = [0, 1, 3, 2, 4, 5]
                    configDict["COLUMN_DISPLAY_NAMES"] = {1: "Primary Heading", 3: "Sub Heading"}

        end = time.time()
        logger.debug("%s Done -- in %s ms", p_categoryNm, (end - start) * 1000)

        return configDict

    def getCategoryColList(self, p_categoryNm):
        """Retrieval of list of attributes (i.e. columns) for given category
        If the category does not exist in the submitted datafile then create a
        skeleton category with a single row of placeholder '?'s

         :param `p_categoryNm`:    name of cif category for which column list being requested



        """
        start = time.time()
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

        rtrnList = []
        bSuccess = False
        myPersist = PdbxPersist(self.__verbose, self.__lfh, retrySeconds=self.__retrySeconds)

        try:
            categoryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, p_categoryNm)
            if categoryObj:
                bSuccess = True
                rtrnList = categoryObj.getAttributeList()
                #
                if self.__verbose:
                    logger.debug("-- Category name sought is: '%s' and true attrib list retrieved is:\n %s", p_categoryNm, rtrnList)
                #
            else:
                # if there was no data for given category name, then create placeholder category with single skeleton row
                if self.__verbose:
                    logger.debug("-- Category '%s' was not found in datafile so generating skeleton category.", p_categoryNm)
                #
                bSuccess, rtrnList = self.__createSkeletonCtgryContainer(myPersist, p_categoryNm)

        #
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("Getting ColList")
            if categoryObj is None:
                bSuccess, rtrnList = self.__createSkeletonCtgryContainer(myPersist, p_categoryNm)

        end = time.time()
        logger.debug("%s Done -- in %s ms", p_categoryNm, (end - start) * 1000)
        return bSuccess, rtrnList

    def getCategoryRowList(self, p_ctgryNm, p_iDisplayStart, p_iDisplayLength, p_sSrchFltr, p_colSearchDict):
        """Retrieval of records for a given category

        :param `p_ctgryNm`:            name of cif category for which list or records being requested
        :param `p_iDisplayStart`:      DataTables related parameter for indicating start index of record
                                         for set of records currently being retrieved for display on screen
        :param `p_iDisplayLength`:     DataTables related parameter for indicating limit of total records
                                        to be displayed on screen (i.e. only subset of entire resultset is being shown)
        :param `p_sSrchFltr`:          DataTables related parameter indicating search term against which records will be filtered
        :param `p_colSearchDict`:      DataTables related parameter indicating column-specific search term against which records will be filtered

        """
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        rtrnList = []
        iTotalRecords = iTotalDisplayRecords = 0

        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh, retrySeconds=self.__retrySeconds)
            #
            if self.__verbose:
                logger.info("Category name sought from [%s] is: '%s'", self.__dbFilePath, p_ctgryNm)
            #
            categoryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, p_ctgryNm)
            #
            # get entire dataset corresponding to the info in the datafile
            # that corresponds to the given cif category

            trueIndxdRcrdLst = []  # to serve as version of recordset that remembers exact row index of the given record
            fullRsltSet = categoryObj.getRowList()
            iTotalRecords = len(fullRsltSet)
            trueColList = categoryObj.getAttributeList()  # list of column names in order that accurately reflects the column order in the persisted data

            for trueRowIdx, rcrd in enumerate(fullRsltSet):
                # for each record we need to remember the true row index so that
                # we can tag the record with this data as it is manipulated in the front end
                # therefore if user submits an edit against this record we use this true row index
                # when registering updates for corresponding record in the persistent data store
                # cannot rely on any client-side row index which may incorrect due to reordering/filtering
                trueIndxdRcrdLst.append({trueRowIdx: rcrd})

            # we need to accommodate any search filtering taking place
            if p_sSrchFltr and len(p_sSrchFltr) > 1:
                filteredRsltSet = self.__filterRsltSet(trueIndxdRcrdLst, p_sGlobalSrchFilter=p_sSrchFltr)
                iTotalDisplayRecords = len(filteredRsltSet)
                rtrnList = filteredRsltSet
            else:
                # no search filter in place
                iTotalDisplayRecords = iTotalRecords
                rtrnList = trueIndxdRcrdLst

            # applying column specific filtering here
            if len(p_colSearchDict) > 0:
                fltrdRsltSet = self.__filterRsltSet(rtrnList, p_dictColSrchFilter=p_colSearchDict)
                iTotalDisplayRecords = len(fltrdRsltSet)
                rtrnList = fltrdRsltSet

            ##################################################################
            # we also need to accommodate any sorting requested by the user
            ##################################################################

            # number of columns selected for sorting --
            iSortingCols = int(self.__reqObj.getValue("iSortingCols")) if self.__reqObj.getValue("iSortingCols") else 0
            #
            ordL = []
            descL = []
            for i in range(iSortingCols):
                iS = str(i)
                idxCol = int(self.__reqObj.getValue("iSortCol_" + iS)) if self.__reqObj.getValue("iSortCol_" + iS) else 0
                sortFlag = self.__reqObj.getValue("bSortable_" + iS) if self.__reqObj.getValue("bSortable_" + iS) else "false"
                sortOrder = self.__reqObj.getValue("sSortDir_" + iS) if self.__reqObj.getValue("sSortDir_" + iS) else "asc"
                if sortFlag == "true":
                    # idxCol at this point reflects display order and not necessarily the true index of the column as it sits in persistent storage
                    # so can reference "mDataProp_[idxCol]" parameter sent by DataTables which will give true name of the column being sorted
                    colName = self.__reqObj.getValue("mDataProp_" + str(idxCol)) if self.__reqObj.getValue("mDataProp_" + str(idxCol)) else ""
                    colIndx = trueColList.index(colName)

                    if self.__verbose:
                        logger.info("-- colIndx for %s is %s as derived from trueColList is %r", colName, colIndx, trueColList)

                    ordL.append(colIndx)
                    if sortOrder == "desc":
                        descL.append(colIndx)
            #
            if len(ordL) > 0:
                rtrnList = self.__orderBy(rtrnList, ordL, descL)
            #
            if self.__verbose:
                logger.info("-- p_iDisplayStart is %s and p_iDisplayLength is %s", p_iDisplayStart, p_iDisplayLength)
            #

        except:  # noqa: E722 pylint: disable=bare-except
            logger.excepton("Error in getCategoryRowList")

        return (rtrnList[(p_iDisplayStart) : (p_iDisplayStart + p_iDisplayLength)], iTotalRecords, iTotalDisplayRecords)

    def checkForDictViolations(self):
        """get list of category.items which are currently in violation of dictionary constraints"""
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        myPersist = PdbxPersist(self.__verbose, self.__lfh)
        #
        categoryList = []
        violationsDict = {"violation_map": {}}
        categoryHndldList = []
        #
        ctgryRqstd = self.__reqObj.getValue("cifctgry")
        #
        categoryList = self.__getCategoryListForCurrentContext()
        #
        for curCtgryNm, ctgryDisplLbl, topLevelMenuChoice in categoryList:

            # proceed only if haven't handled the category
            if curCtgryNm not in categoryHndldList:
                categoryHndldList.append(curCtgryNm)

                if (ctgryRqstd != "all" and ctgryRqstd == curCtgryNm) or (ctgryRqstd == "all"):
                    ctgryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, curCtgryNm)
                    if ctgryObj:
                        bFoundViolation = False
                        newViolMapDict = {"top_menu_label": "", "col_names": [], "data_positions": [], "violation_msgs": []}

                        # get cif meta data from dictionary
                        catObjDict = self.getTblConfigDict(curCtgryNm, ctgryDisplLbl)
                        #
                        fullRsltSet = ctgryObj.getRowList()
                        #
                        attributeList = ctgryObj.getAttributeList()
                        if self.__verbose:
                            logger.info("-- Attribute list retrieved is: %s", str(attributeList))
                        #
                        for rowIdx, record in enumerate(fullRsltSet):
                            for colIdx, itemValue in enumerate(record):
                                try:
                                    if itemValue and (len(itemValue) > 0 and self.__isNotCifNull(itemValue)):
                                        truAttribName = attributeList[colIdx]
                                        colDisplName = catObjDict["COLUMN_DISPLAY_NAMES"].get(colIdx, attributeList[colIdx])
                                        #
                                        if not self.__pdbxDictStore:
                                            self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)
                                        #
                                        ctgryMetaDict = self.__getCifCtgryMetaDict(curCtgryNm)
                                        if ctgryMetaDict is None:
                                            if self.__debug:
                                                logger.debug("-- WARNING: failed to obtain ctgryMetaDict for '%s'", curCtgryNm)
                                        else:
                                            if self.__debug:
                                                logger.debug(" -- ctgryMetaDict obtained as %r", list(ctgryMetaDict.items()))
                                        #
                                        vldtnTstRslts = self.__validateAgainstDict(ctgryMetaDict, curCtgryNm, truAttribName, itemValue)
                                        if vldtnTstRslts["pass_regex_tst"] == "false" or vldtnTstRslts["pass_bndry_tst"] == "false":
                                            msg = ""

                                            if len(newViolMapDict["top_menu_label"]) < 1:
                                                newViolMapDict["top_menu_label"] = topLevelMenuChoice

                                            if colDisplName not in newViolMapDict["col_names"]:
                                                newViolMapDict["col_names"].append(colDisplName)
                                            newViolMapDict["data_positions"].append((rowIdx, colIdx))

                                            if vldtnTstRslts["pass_regex_tst"] == "false":
                                                msg = vldtnTstRslts["fail_msg_regex"]

                                            if vldtnTstRslts["pass_bndry_tst"] == "false":
                                                msg += vldtnTstRslts["fail_msg_bndry"]

                                            newViolMapDict["violation_msgs"].append(msg)

                                            bFoundViolation = True

                                            if self.__debug:
                                                logger.debug(
                                                    "---- DEBUG ---- Current rowIdx is '%s', colIdx is '%s', and violationsDict is now '%r'", rowIdx, colIdx, violationsDict
                                                )
                                #
                                except:  # noqa: E722 pylint: disable=bare-except
                                    logger.info(
                                        "---- DEBUG ---- EXCEPTION: Current rowIdx is '%s', colIdx is '%s', and length of record is '%s' for category '%s'",
                                        rowIdx,
                                        colIdx,
                                        len(record),
                                        curCtgryNm,
                                    )
                                    logger.info("---- DEBUG ---- EXCEPTION: record is '%r'", record)
                                    logger.exception("Excepton in checkForDictViolations")
                        #
                        if bFoundViolation:
                            violationsDict["violation_map"][curCtgryNm] = newViolMapDict

                    else:
                        if self.__debug:
                            logger.debug("---- DEBUG ---- category '%s' not found in deposited data.", curCtgryNm)
        #
        return violationsDict

    def validateItemValue(self, p_ctgryNm, p_newValue, p_rowIdx, p_colIdx):
        """Perform validation check of proposed edit for given cif category.attribute

        :param `p_ctgryNm`:        name of cif category for which update applies
        :param `p_newValue`:       value being submitted as updated data
        :param `p_rowIdx`:         row index of field being edited
        :param `p_colIdx`:         column index of field being edited

        """
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        rtrnDict = {}

        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            if self.__debug:
                logger.debug("++++++++++++ just before call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            ctgryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, p_ctgryNm)
            #
            if self.__debug:
                logger.debug("++++++++++++ just after call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            if ctgryObj.getRowCount() == 1 and self.__bUseTransposedTables:
                p_colIdx = p_rowIdx
                p_rowIdx = 0
                if self.__verbose:
                    logger.info("-- Category being updated '%s' is being treated as TRANSPOSED.", p_ctgryNm)
            #
            if self.__verbose:
                logger.info("Category name sought is '%s' and colIdx has value of: %s", p_ctgryNm, p_colIdx)
            #
            attributeList = ctgryObj.getAttributeList()
            if self.__verbose:
                logger.info("-- Attribute list retrieved is: %s", str(attributeList))
            #
            attributeNm = attributeList[p_colIdx]  # get name of category field using column index returned from client and mapped against attribute list held by the categoryObject
            if self.__verbose:
                logger.info("User has submitted update for category.item '%s.%s' with proposed value: '%r'", p_ctgryNm, attributeNm, p_newValue)
            #
            if not self.__pdbxDictStore:
                self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)
            #
            ctgryMetaDict = self.__getCifCtgryMetaDict(p_ctgryNm)
            if ctgryMetaDict is None:
                if self.__verbose:
                    logger.info("-- WARNING: failed to obtain ctgryMetaDict for '%s'", p_ctgryNm)
            else:
                if self.__debug:
                    logger.debug("-- ctgryMetaDict obtained as %r", list(ctgryMetaDict.items()))
                #
            rtrnDict = self.__validateAgainstDict(ctgryMetaDict, p_ctgryNm, attributeNm, p_newValue)
        #
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("validateItemValue")

        return rtrnDict

    def __validateAgainstDict(self, p_ctgryMetaDict, p_ctgryNm, p_attributeNm, p_value):
        rtrnDict = {}
        rtrnDict["pass_regex_tst"] = ""
        rtrnDict["pass_bndry_tst"] = ""
        bValueInCsvListForm = True if p_ctgryNm + "." + p_attributeNm in EditorConfig.itemsInCsvListForm else False
        regexAllowOverride = True if p_ctgryNm + "." + p_attributeNm in EditorConfig.itemsAllowingOverrideRegex else False

        #
        if p_ctgryMetaDict:
            rslt, msg = self.__regexValidation(p_ctgryMetaDict, p_ctgryNm, p_attributeNm, p_value)
            if rslt is True:
                rtrnDict["pass_regex_tst"] = "true"
            else:
                rtrnDict["pass_regex_tst"] = "false"
                rtrnDict["fail_msg_regex"] = msg.rstrip()
                rtrnDict["fail_typ_regex"] = "soft" if regexAllowOverride else "hard"

            #
            valuesList = p_value.split(",") if bValueInCsvListForm else [p_value]

            for value in valuesList:
                rslt, msg, vldtype = self.__boundaryValidation(p_ctgryMetaDict, p_ctgryNm, p_attributeNm, value)
                if rslt is True:
                    rtrnDict["pass_bndry_tst"] = "true"
                else:
                    rtrnDict["pass_bndry_tst"] = "false"
                    rtrnDict["fail_msg_bndry"] = msg.rstrip()
                    rtrnDict["fail_typ_bndry"] = vldtype
                    break  # cancel checking rest of values at first occurrence of boundary validation

        return rtrnDict

    def setItemValue(self, p_ctgryNm, p_newValue, p_rowIdx, p_colIdx):
        """Save updated value for given item to persistent store

        :param `p_ctgryNm`:        name of cif category for which update applies
        :param `p_newValue`:       value being submitted as updated data
        :param `p_rowIdx`:         row index of field being edited
        :param `p_colIdx`:         column index of field being edited

        """
        logger.info("--------------------------------------------\n")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        bSuccess = False
        #
        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            if self.__debug:
                logger.debug("++++++++++++ just before call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            ctgryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, p_ctgryNm)
            #
            if self.__debug:
                logger.debug("++++++++++++ just after call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            if ctgryObj.getRowCount() == 1 and self.__bUseTransposedTables:
                p_colIdx = p_rowIdx
                p_rowIdx = 0
                if self.__verbose:
                    logger.info("-- Category being updated '%s' is being treated as TRANSPOSED.", p_ctgryNm)
            #
            if self.__verbose:
                logger.info("-- Category name sought is '%s' and p_colIdx has value of: %s", p_ctgryNm, p_colIdx)
            #
            attributeList = ctgryObj.getAttributeList()
            if self.__verbose:
                logger.info("Attribute list retrieved is: %s", str(attributeList))
            #
            attributeNm = attributeList[
                p_colIdx
            ]  # get name of category field based using column index returned from client and mapped against attribute list held by the categoryObject # noqa; E501

            if EditorConfig.bAccommodatingUnicode and p_ctgryNm + "." + attributeNm in EditorConfig.itemsAllowingUnicodeAccommodation:
                # if we are handling unicode characters, submit new value to ascii safe conversion
                p_newValue = self.__encodeUtf8ToCif(p_newValue)
            #
            if self.__verbose:
                logger.info("-- About to update category '%s' with updated value for '%s' as '%s' for row index [%s]", p_ctgryNm, attributeNm, p_newValue, p_rowIdx)
            #
            logger.info("dbFilePath is: [%s] and dataBlockName is: '%s'", self.__dbFilePath, self.__dataBlockName)
            #
            if p_ctgryNm + "." + attributeNm in EditorConfig.autoIncrDecrList:
                fullRsltSet = ctgryObj.getRowList()
                self.__autoIncrementOrdinalId(fullRsltSet, p_colIdx, p_newValue, ctgryObj, attributeNm)

            #
            ctgryObj.setValue(p_newValue, attributeNm, p_rowIdx)
            #
            if self.__debug:
                logger.debug("++++++++++++ just before call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            bSuccess = myPersist.updateOneObject(ctgryObj, self.__dbFilePath, self.__dataBlockName)
            if self.__debug:
                logger.debug("++++++++++++ just after call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("In setItemValue")

        return bSuccess

    def addSkipCalcRequest(self, p_task):
        """
        :param `p_task`:        name of task for which "skip calculation" request being made
                              can be one of:

                                link | site | helix | sheet | solventpos


        """
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        bSuccess = False
        rowToAdd = []
        cifCtgryNm = "pdbx_data_processing_status"

        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            if self.__debug:
                logger.debug("++++++++++++ just before call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            ctgryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, cifCtgryNm)
            #
            if self.__debug:
                logger.debug("++++++++++++ just after call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            if ctgryObj is None:
                if not self.__pdbxDictStore:
                    self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)
                #
                ctgryMetaDict = self.__getCifCtgryMetaDict(cifCtgryNm)
                #
                ctgryObj = DataCategory(cifCtgryNm)
                dicAttributeList = ctgryMetaDict["COLUMN_NAMES"]
                for dicattributeNm in dicAttributeList:
                    if self.__debug:
                        logger.debu("++++++++++++ building skeleton cifCategory container with attribute: %s", dicattributeNm)
                    #
                    ctgryObj.appendAttribute(dicattributeNm)

            #
            attributeList = ctgryObj.getAttributeList()
            #
            if self.__verbose:
                logger.info("-- Attribute list retrieved is: %s", str(attributeList))
            #
            for attributeNm in attributeList:

                if attributeNm == "task_name":
                    valueToSupply = "solvent position" if p_task == "solventpos" else p_task
                elif attributeNm == "status":
                    valueToSupply = "skip"
                #
                rowToAdd.append(valueToSupply)

            #
            if self.__verbose:
                logger.info("-- About to update category '%s' with new row as %r", cifCtgryNm, rowToAdd)
            #
            ctgryObj.append(rowToAdd)
            #
            if self.__debug:
                logger.debug("++++++++++++ just before call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            bSuccess = myPersist.updateOneObject(ctgryObj, self.__dbFilePath, self.__dataBlockName)
            if self.__debug:
                logger.debug("++++++++++++ just after call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("In adding skip")

        return bSuccess

    def rmSkipCalcRequest(self, p_task):
        """delete row corresponding to skip calc request from persistent store

        :param `p_task`:        name of task for which "skip calculation" request being made
                              can be one of:

                                link | site | helix | sheet | solventpos

        """
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        bSuccess = False
        cifCtgryNm = "pdbx_data_processing_status"

        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            if self.__debug:
                logger.info("++++++++++++ just before call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            ctgryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, cifCtgryNm)
            #
            if self.__debug:
                logger.info("++++++++++++ just after call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            rowList = ctgryObj.getRowList()

            attributeList = ctgryObj.getAttributeList()
            if self.__verbose:
                logger.info("-- Attribute list retrieved is: %s", str(attributeList))
            #
            colIdx = None
            rowIdx = None
            rowBeingDeleted = None
            p_task = "solvent position" if p_task == "solventpos" else p_task
            #
            for index, attributeNm in enumerate(attributeList):
                if attributeNm == "task_name":
                    colIdx = index
                    break

            if colIdx is not None:
                for idx, record in enumerate(rowList):
                    try:
                        taskName = record[colIdx]
                        if taskName.lower() == p_task.lower():
                            rowIdx = idx
                            break

                    except ValueError:
                        if self.__verbose and self.__debug:
                            logger.info(
                                "ValueError found when comparing '%s' with '%s' so comparison not used to determine need for readjusting values of ordinal id field.",
                                record[colIdx],
                                taskName,
                            )
                        continue

                if rowIdx is not None:
                    rowBeingDeleted = rowList.pop(rowIdx)

            if self.__verbose:
                logger.info("About to update category '%s' by deleting row #%s, %r", cifCtgryNm, rowIdx, rowBeingDeleted)
            #
            ctgryObj.setRowList(rowList)

            if self.__debug:
                logger.info("++++++++++++just before call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            bSuccess = myPersist.updateOneObject(ctgryObj, self.__dbFilePath, self.__dataBlockName)
            if self.__debug:
                logger.info("++++++++++++ just after call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("Failure in rmSkipCalcRequest")

        return bSuccess

    def checkSkipCalcRequest(self, p_task):
        """delete row corresponding to skip calc request from persistent store

        :param `p_task`:        name of task for which "skip calculation" request being made
                              can be one of:

                                link | site | helix | sheet

        """
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        bSkipRequested = False
        cifCtgryNm = "pdbx_data_processing_status"

        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            if self.__debug:
                logger.info("++++++++++++just before call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            ctgryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, cifCtgryNm)
            #
            if self.__debug:
                logger.info("+++++++++++ just after call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            if ctgryObj:
                rowList = ctgryObj.getRowList()

                attributeList = ctgryObj.getAttributeList()
                if self.__verbose:
                    logger.info("-- Attribute list retrieved is: %s", str(attributeList))
                #
                colIdx = None
                rowIdx = None
                p_task = "solvent position" if p_task == "solventpos" else p_task
                #
                for index, attributeNm in enumerate(attributeList):
                    if attributeNm == "task_name":
                        colIdx = index
                        break

                if colIdx is not None:
                    for idx, record in enumerate(rowList):
                        try:
                            taskName = record[colIdx]
                            if taskName.lower() == p_task.lower():
                                rowIdx = idx
                                break

                        except ValueError:
                            if self.__verbose and self.__debug:
                                logger.info(
                                    "-- ValueError found when comparing '%s' with '%s' so comparison not used to determine need for readjusting values of ordinal id field.",
                                    record[colIdx],
                                    taskName,
                                )
                            continue

                    if rowIdx is not None:
                        bSkipRequested = True

                if self.__verbose:
                    logger.info("-- '%s' did contain request to skip calculation for %s", cifCtgryNm, p_task)
                #

        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("In checkSkipCalcRequest")

        return bSkipRequested

    def addNewRow(self, p_ctgryNm):
        """add new "dummy" row to persistent store, "dummy" row will then be returned to client for population with real data

        :param `p_ctgryNm`:        name of cif category for which update applies

        """
        logger.info("--------------------------------------------\n")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        bSuccess = False
        rowToAdd = []

        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            if self.__debug:
                logger.debug("++++++++++++just before call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            ctgryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, p_ctgryNm)
            #
            if self.__debug:
                logger.debug("++++++++++++ just after call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            attributeList = ctgryObj.getAttributeList()
            #
            if self.__verbose:
                logger.info("+-- Attribute list retrieved is: %s", str(attributeList))
            #
            if not self.__pdbxDictStore:
                self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)
            #
            if self.__debug:
                logger.debug("++++++++++++just after existence check/creation of PdbxDictionary at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

            ctgryMetaDict = self.__getCifCtgryMetaDict(p_sCtgryName=p_ctgryNm, p_bCreateStub=True)

            if self.__debug:
                logger.info("+ -- ctgryMetaDict['COLUMN_DEFAULT_VALUES'] obtained as %r", ctgryMetaDict["COLUMN_DEFAULT_VALUES"])
                logger.info("-- ctgryMetaDict['PRIMARY_KEYS'] obtained as %r", ctgryMetaDict["PRIMARY_KEYS"])
            #
            rowToAdd = self.__genRowOfDefaultValues(p_ctgryNm, ctgryMetaDict, attributeList, "addNewRow", ctgryObj)

            #
            if self.__verbose:
                logger.info("-- About to update category '%s' with new row as %r", p_ctgryNm, rowToAdd)
            #
            ctgryObj.append(rowToAdd)
            #
            if self.__debug:
                logger.info("++++++++++++ just before call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            bSuccess = myPersist.updateOneObject(ctgryObj, self.__dbFilePath, self.__dataBlockName)
            if self.__debug:
                logger.info("++++++++++++ just before call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("addNewRow Failure")

        return bSuccess

    def __genRowOfDefaultValues(self, p_ctgryNm, p_ctgryMetaDict, p_attributeList, p_context, p_ctgryObj=None, p_ordinalId=None, p_cloneDict=None):
        """This method handles the creation of empty "placeholder" rows for a given category.
        It is called when:
            = a new row is added/inserted to an instance of a category that holds pre-existing data
            = a "skeleton" category instance is being created (b/c the category is required for population but was not in the depositor's datafile)
                and hence the "skeleton" instance requires the creation of its sole placeholder row

        :Params:
            :param `p_ctgryNm`:        name of cif category for which update applies
            :param `p_ctgryMetaDict`:  dictionary of cif metatdata
            :param `p_attributeList`:         row index of field being edited
            :param `p_context`:         whether method is being called in order to "addNewRow" | "insertRow" | "__createSkeletonCtgryContainer"
            :param `p_ctgryObj`:        object reference to the cif category being manipulated
            :param `p_ordinalId`:        if supplied, indicates request to use the given ordinal ID# for identifying the row during an INSERT operation
            :param `p_cloneDict`:        currently only used when CIF Editor is being used to edit the CIF Editor config file (itself a cif data file)
                                            the clone dictionary contains datapoints to be duplicated as desired when creating new copies of rows being inserted

        :Returns:
            rowToAdd --> list representing the new row being added
        """

        rowToAdd = []
        excludeList = list(EditorConfig.autoIncrExclList)
        if p_context == "__createSkeletonCtgryContainer":
            excludeList.extend(
                ["entity_src_nat.entity_id", "entity_src_gen.entity_id", "pdbx_entity_src_syn.entity_id", "pdbx_entity_src_syn.pdbx_src_id", "database_PDB_caveat.id"]
            )
            excludeList.extend(
                [
                    "pdbx_refine_tls_group.id",
                    "struct_ncs_ens.id",
                    "struct_ncs_dom.id",
                    "struct_ncs_dom.pdbx_ens_id",
                    "struct_ncs_dom_lim.dom_id",
                    "struct_ncs_dom_lim.pdbx_component_id",
                    "struct_ncs_dom_lim.pdbx_ens_id",
                    "struct_mon_prot_cis.pdbx_id",
                ]
            )
        #
        for index, attributeNm in enumerate(p_attributeList):
            # here we will build a new placeholder row using default values for each attribute if defined in the dictionary for given column
            defaultVal = p_ctgryMetaDict["COLUMN_DEFAULT_VALUES"].get(attributeNm, "?")

            # below, in case of specific cif items, defaultVal is reassigned via special handling
            if p_ctgryNm + "." + attributeNm == "pdbx_database_related.content_type" and p_context in ["addNewRow", "insertRow", "__createSkeletonCtgryContainer"]:
                defaultVal = "unspecified"
            elif p_ctgryNm + "." + attributeNm in EditorConfig.autoIncrDecrList:
                # 2013-03-18, RPS: interim handling for auto-increment of ordinal field for citation_author category
                # should explore ways to accommodate this via config file
                if p_context == "__createSkeletonCtgryContainer":
                    defaultVal = "1"
                elif p_context == "insertRow":
                    defaultVal = p_ordinalId
                else:
                    defaultVal = self.__getNextOrdinalValue(p_ctgryObj, attributeNm)
            elif ("id" in attributeNm) and (attributeNm in p_ctgryMetaDict["PRIMARY_KEYS"]):
                if p_ctgryNm + "." + attributeNm not in excludeList:
                    defaultVal = "1" if p_context == "__createSkeletonCtgryContainer" else self.__getNextOrdinalValue(p_ctgryObj, attributeNm)
                    logger.info("-- value of ID to be assigned as autoincrement  for '%s.%s' is: %s.", p_ctgryNm, attributeNm, defaultVal)
                #
                else:
                    logger.info("-- '%s.%s' is in exclusion list when called in context of '%s', so not autoincremented.", p_ctgryNm, attributeNm, p_context)
                #
                if "entry_id" in attributeNm:  # examples ['pdbx_database_proc.entry_id','atom_sites.entry_id']
                    defaultVal = str(self.__reqObj.getValue("identifier")).upper()
                    logger.info(" -- value of ID to be auto-assigned for '%s.%s' is: %s.", p_ctgryNm, attributeNm, defaultVal)
            elif (
                p_ctgryNm + "." + attributeNm in ["pdbx_entity_src_syn.pdbx_alt_source_flag", "pdbx_database_related.content_type"]
            ) and p_context == "__createSkeletonCtgryContainer":
                defaultVal = "?"

            elif p_ctgryNm in ["pdbx_display_view_category_info", "pdbx_display_view_item_info"] and p_cloneDict:
                if attributeNm in p_cloneDict["itemsList"]:
                    defaultVal = p_cloneDict["referenceRow"][index]
            #
            rowToAdd.append(defaultVal)

        return rowToAdd

    def deleteRows(self, p_ctgryNm, p_rowIdx, p_iNumRows=None):
        """delete row from persistent store

        :param `p_ctgryNm`:       name of cif category for which update applies
        :param `p_rowIdx`:        index of row at which to start deleting
        :param `p_iNumRows`:      number of rows to delete

        """
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        bSuccess = False
        sErrMsg = ""
        iLastRowDeleted = None

        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            if self.__debug:
                logger.debug("++++++++++++ just before call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            ctgryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, p_ctgryNm)
            #
            if self.__debug:
                logger.debug("++++++++++++ just after call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            rowBeingDeleted = None  # will end up being populated with last row being popped in for-loop below
            rowList = ctgryObj.getRowList()
            for n in range(p_iNumRows):
                rowBeingDeleted = rowList.pop(p_rowIdx)
                iLastRowDeleted = n + 1
                if self.__verbose:
                    logger.info("+ -- About to update category '%s' by deleting row #%s, %r", p_ctgryNm, p_rowIdx + n, rowBeingDeleted)
            #
            ctgryObj.setRowList(rowList)

            ################################################
            # here we are undertaking special handling for certain cif items that require auto *decrement* of ordinal ID values to reflect the loss of a row

            if p_ctgryNm in EditorConfig.autoIncrDecrDict:
                attributeList = ctgryObj.getAttributeList()
                if self.__verbose:
                    logger.info("-- Attribute list retrieved is: %s", str(attributeList))
                #
                colIdx = None

                attributeNm = 0
                for index, attributeNm in enumerate(attributeList):
                    if EditorConfig.autoIncrDecrDict[p_ctgryNm] == attributeNm:
                        colIdx = index
                        break

                if colIdx is not None:
                    autoDecrementNeeded = False

                    deletedOrdinalValue = rowBeingDeleted[colIdx]

                    for idx, record in enumerate(rowList):
                        try:
                            ordinalId = int(record[colIdx])
                            if ordinalId == (int(deletedOrdinalValue) + 1):
                                autoDecrementNeeded = True
                                break

                        except ValueError:
                            if self.__verbose and self.__debug:
                                logger.debug(
                                    "-- ValueError found when comparing '%s' with '%s' so comparison not used to determine need for readjusting values of ordinal id field",
                                    record[colIdx],
                                    deletedOrdinalValue,
                                )
                            continue

                    if autoDecrementNeeded:
                        for idx, record in enumerate(rowList):
                            ordinalId = int(record[colIdx])
                            if ordinalId >= (int(deletedOrdinalValue) + 1):
                                ctgryObj.setValue(str(ordinalId - p_iNumRows), attributeNm, idx)

            ################################################

            if self.__debug:
                logger.debug("++++++++++++ just before call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            bSuccess = myPersist.updateOneObject(ctgryObj, self.__dbFilePath, self.__dataBlockName)
            if self.__debug:
                logger.debug("++++++++++++ just after call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        except IndexError:
            if self.__verbose:
                sErrMsg = "Request to delete %s rows but only %s remain from originating row" % (p_iNumRows, iLastRowDeleted)
                logger.info("%s in category '%s'", sErrMsg, p_ctgryNm)

        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("deleteRows failure")

        return bSuccess, sErrMsg

    def insertRows(self, p_ctgryNm, p_rowIdx, p_relativePos="after", p_cloneList=None, p_iNumRows=None):
        """insert a new row

        :param `p_ctgryNm`:       name of cif category for which update applies
        :param `p_rowIdx`:        index of lead row being added
        :param `p_relativePos`:    before | after given p_rowIdx
        :param `p_cloneList`:    list indicating which items are to be cloned from adjacent row
        :param `p_iNumRows`:      number of rows to insert

        """
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        bSuccess = False
        cloneDict = None

        try:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            if self.__debug:
                logger.info("++++++++++++just before call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            ctgryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, p_ctgryNm)
            #
            if self.__debug:
                logger.info("++++++++++++just after call to myPersist.fetchOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            attributeList = ctgryObj.getAttributeList()
            rowList = ctgryObj.getRowList()
            #
            if self.__verbose:
                logger.info("+-- Current row is: %r", rowList[p_rowIdx])

            if not self.__pdbxDictStore:
                self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)
            #
            ctgryMetaDict = self.__getCifCtgryMetaDict(p_sCtgryName=p_ctgryNm, p_bCreateStub=True)
            #
            if p_cloneList:
                cloneDict = {}
                cloneDict["itemsList"] = p_cloneList
                cloneDict["referenceRow"] = rowList[p_rowIdx]

            for n in range(p_iNumRows):

                newOrdinalId = str(p_rowIdx + (n + 2))

                newRow = self.__genRowOfDefaultValues(p_ctgryNm, ctgryMetaDict, attributeList, "insertRow", ctgryObj, p_ordinalId=newOrdinalId, p_cloneDict=cloneDict)

                ################################################
                # here we are undertaking special handling for certain cif items that require auto increment of ordinal ID values to reflect new row being inserted

                if p_ctgryNm in EditorConfig.autoIncrDecrDict:
                    colIdx = None
                    targetAttrNm = None
                    for index, attributeNm in enumerate(attributeList):
                        if EditorConfig.autoIncrDecrDict[p_ctgryNm] == attributeNm:
                            colIdx = index
                            targetAttrNm = attributeNm
                            break

                    if colIdx is not None:
                        self.__autoIncrementOrdinalId(rowList, colIdx, newOrdinalId, ctgryObj, targetAttrNm)

                ################################################

                insertBeforeIndx = p_rowIdx if p_relativePos == "before" else (p_rowIdx + (n + 1))
                rowList.insert(insertBeforeIndx, newRow)
                if self.__verbose:
                    logger.info("+ -- About to update category '%s' by inserting row, %r,\n%s row#%s", p_ctgryNm, newRow, p_relativePos, (p_rowIdx + n))
            #
            ctgryObj.setRowList(rowList)

            if self.__debug:
                logger.info("++++++++++++ just before call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
            bSuccess = myPersist.updateOneObject(ctgryObj, self.__dbFilePath, self.__dataBlockName)
            if self.__debug:
                logger.info("++++++++++++ just before call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
            #
        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("Failure in insertRows")

        return bSuccess

    def __autoIncrementOrdinalId(self, p_recordset, p_colIdx, p_newValue, p_ctgryObj, p_attributeNm):
        """This method handles


        :Params:
            :param `p_recordset`:
            :param `p_colIdx`:
            :param `p_newValue`:
            :param `p_ctgryObj`:        object reference to the cif category being manipulated
            :param `p_attributeNm`:


        :Returns:

        """
        autoIncrementNeeded = False

        for idx, record in enumerate(p_recordset):
            try:
                ordinalId = int(record[p_colIdx])

                if ordinalId == int(p_newValue):
                    autoIncrementNeeded = True
                    logger.info("-- autoIncrementNeeded set to True.")
                    break

            except ValueError:
                if self.__verbose and self.__debug:
                    logger.info("-- therefore '%s' is not used to determine need for readjusting values of ordinal id field.", record[p_colIdx])
                continue

        try:
            if autoIncrementNeeded:
                logger.info("-- autoIncrementNeeded needed so updating recordset.")
                for idx, record in enumerate(p_recordset):
                    ordinalId = int(record[p_colIdx])
                    if ordinalId >= int(p_newValue):
                        p_ctgryObj.setValue(str(ordinalId + 1), p_attributeNm, idx)

        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("In incrementing ordinals")
            logger.info("-- failed for '%s'.", p_attributeNm)

    def undoEdits(self, p_cifCtgry, p_rewindIndex):
        """undo change(s)

        :param `p_cifCtgry`:       name of cif category
        :param `p_rewindIndex`:    indicates index of snapshot to restore on incremental undo

        """
        logger.info("--------------------------------------------")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        bSuccess = False
        #
        if self.__verbose:
            logger.info("p_rewindIndex is: %s", p_rewindIndex)

        rewindToSnapShotFilePath = os.path.join(self.__sessionSnapShotsPath, "dataFileSnapShot_" + str(p_rewindIndex) + ".db")

        try:
            if os.access(rewindToSnapShotFilePath, os.F_OK):

                myPersist = PdbxPersist(self.__verbose, self.__lfh)
                #
                if self.__verbose:
                    logger.info("-- Reverting to prior state just for category: '%s'", p_cifCtgry)
                #
                categoryObj = myPersist.fetchOneObject(rewindToSnapShotFilePath, self.__dataBlockName, p_cifCtgry)
                #
                bSuccess = myPersist.updateOneObject(categoryObj, self.__dbFilePath, self.__dataBlockName)

            else:
                if self.__verbose:
                    logger.info("problem accessing dataFileSnapShot file at: %s\n", rewindToSnapShotFilePath)
        #
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                logger.info("problem reverting db file at [%s] to prior state just for category '%s'.", self.__dbFilePath, p_cifCtgry)
            logger.exception("Failure in reverting db file")
        #

        return bSuccess

    # #####################################   HELPER FUNCTIONS   #################################################

    def __getSortAscColIndex(self, p_categoryNm, p_truCtgryColList):

        sortAscIdx = None
        sortTargetColName = EditorConfig.sortColDict[p_categoryNm] if p_categoryNm in EditorConfig.sortColDict else None

        if sortTargetColName:
            for idx, colName in enumerate(p_truCtgryColList):
                if colName == sortTargetColName:
                    sortAscIdx = idx

        returnIdx = sortAscIdx if (sortAscIdx and sortAscIdx >= 0) else -1

        return returnIdx

    def __isNotCifNull(self, p_value):
        if p_value == "." or p_value == "?":
            return False
        else:
            return True

    def __getCifCtgryMetaDict(self, p_sCtgryName, p_bCreateStub=False):
        """
        obtain dictionary of meta data for given cif category

        :param `p_sCtgryName`:     name of cif category
        :param `p_bCreateStub`:    if the given cif catgory is not represented in
                                   the CIF dictionary then create a skeleton stub

        """

        rtrnDict = self.__pdbxDictStore.fetchOneObject(dbFileName=self.__dictDbFilePath, objectName=p_sCtgryName)

        if (rtrnDict is None) and p_bCreateStub:
            rtrnDict = {}
            rtrnDict["COLUMN_BOUNDARY_VALUES"] = {}
            rtrnDict["COLUMN_BOUNDARY_VALUES_ALT"] = {}
            rtrnDict["COLUMN_DEFAULT_VALUES"] = {}
            rtrnDict["COLUMN_DESCRIPTIONS"] = {}
            rtrnDict["COLUMN_DESCRIPTIONS_ALT"] = {}
            rtrnDict["COLUMN_DISPLAY_NAMES"] = []
            rtrnDict["COLUMN_DISPLAY_ORDER"] = []
            rtrnDict["COLUMN_ENUMS"] = {}
            rtrnDict["COLUMN_ENUMS_ALT"] = {}
            rtrnDict["COLUMN_EXAMPLES"] = {}
            rtrnDict["COLUMN_EXAMPLES_ALT"] = {}
            rtrnDict["COLUMN_NAMES"] = []
            rtrnDict["COLUMN_REGEX"] = {}
            rtrnDict["COLUMN_REGEX_ALT"] = {}
            rtrnDict["COLUMN_TYPES"] = {}
            rtrnDict["COLUMN_TYPES_ALT"] = {}
            rtrnDict["DISPLAY_NAME"] = ""
            rtrnDict["MANDATORY_COLUMNS"] = []
            rtrnDict["MANDATORY_COLUMNS_ALT"] = []
            rtrnDict["PRIMARY_KEYS"] = []

            if p_sCtgryName == "pdbx_display_view_category_info":
                rtrnDict["COLUMN_NAMES"] = [
                    "view_id",
                    "category_menu_display_name",
                    "category_name",
                    "category_group_display_name",
                    "category_display_name",
                    "category_cardinality",
                ]
            elif p_sCtgryName == "pdbx_display_view_item_info":
                rtrnDict["COLUMN_NAMES"] = ["view_id", "category_display_name", "item_name", "item_display_name", "read_only_flag"]

        return rtrnDict

    def __getDataTblCnfgStub(self, p_ctgryColList=None):
        """
        creating skeleton dictionary to be used for configuring DataTable on front-end.

        this is necessary when we encounter cif categories for which there may be no meta dictionary information

        """

        dataTblCnfgDict = {}
        #
        # create empty congif dict
        dataTblCnfgDict["DISPLAY_NAME"] = []
        dataTblCnfgDict["COLUMN_NAMES"] = p_ctgryColList if p_ctgryColList else []
        dataTblCnfgDict["COLUMN_DISPLAY_NAMES"] = {}
        dataTblCnfgDict["PRIMARY_KEYS"] = []
        dataTblCnfgDict["MANDATORY_COLUMNS"] = []
        dataTblCnfgDict["MANDATORY_COLUMNS_ALT"] = []
        dataTblCnfgDict["COLUMN_DISPLAY_ORDER"] = [x for x in range(0, len(p_ctgryColList))] if p_ctgryColList else []
        dataTblCnfgDict["COLUMN_TYPES"] = {}
        dataTblCnfgDict["COLUMN_TYPES_ALT"] = {}
        dataTblCnfgDict["COLUMN_ENUMS"] = {}
        dataTblCnfgDict["COLUMN_ENUMS_ALT"] = {}
        dataTblCnfgDict["COLUMN_DESCRIPTIONS"] = {}
        dataTblCnfgDict["COLUMN_DESCRIPTIONS_ALT"] = {}
        dataTblCnfgDict["COLUMN_EXAMPLES"] = {}
        dataTblCnfgDict["COLUMN_EXAMPLES_ALT"] = {}
        dataTblCnfgDict["COLUMN_REGEX"] = {}
        dataTblCnfgDict["COLUMN_REGEX_ALT"] = {}
        dataTblCnfgDict["COLUMN_BOUNDARY_VALUES"] = {}
        dataTblCnfgDict["COLUMN_BOUNDARY_VALUES_ALT"] = {}
        dataTblCnfgDict["COLUMN_DEFAULT_VALUES"] = {}
        dataTblCnfgDict["COLUMN_READ_ONLY_FLAG"] = {}

        return dataTblCnfgDict

    def __getNextOrdinalValue(self, p_ctgryObj, p_attributeNm):

        logger.info("--------------------------------------------\n")
        logger.info("Starting at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        try:
            fullRsltSet = p_ctgryObj.getRowList()

            ctgryNm = p_ctgryObj.getName()

            if self.__verbose and self.__debug:
                logger.debug("-- ctgryNm obtained as: %s", ctgryNm)
                logger.debug("-- fullRsltSet obtained as: %r", fullRsltSet)

            ctgryColList = (self.getCategoryColList(ctgryNm))[1]
            if self.__verbose and self.__debug:
                logger.debug("ctgryColList obtained as: %r", ctgryColList)
            #
            desiredIdx = None
            for idx, name in enumerate(ctgryColList):

                if name == p_attributeNm:
                    if self.__verbose and self.__debug:
                        logger.debug("-- '%s' field corresponds to index: [%s]", p_attributeNm, idx)

                    desiredIdx = idx
                    break
            #
            currentMax = 0
            for i, record in enumerate(fullRsltSet):
                if self.__verbose and self.__debug:
                    logger.debug("-- for row #%s, record[%s] is '%s'", i, desiredIdx, record[desiredIdx])
                try:
                    if int(record[desiredIdx]) > int(currentMax):
                        currentMax = int(record[desiredIdx])
                except ValueError:
                    if self.__verbose and self.__debug:
                        logger.debug("-- therefore '%s' is not used to determine current max value of ordinal id field.", record[desiredIdx])

            logger.info("currentMax obtained as: '%s'", currentMax)

        except:  # noqa: E722 pylint: disable=bare-except
            logger.exception("__getNextOrdinalValue")

        return str(int(currentMax) + 1)

    def __orderBy(self, sortlist, orderby=None, desc=None):
        """orderBy(sortlist, orderby, desc) >> List

        @sortlist: list to be sorted
        @orderby: list of indices of columns for which sorting will be performed
        @desc: list of indices of columns for which sorting will be performed in descending fashion"""

        if orderby is None:
            orderby = []
        if desc is None:
            desc = []

        if self.__verbose and self.__debug:
            for entry in sortlist:
                dtype = type(entry)
                logger.debug("-- entry in sortlist is of type '%s' and its content is: %r \n", dtype, entry)

        allIntDict = {}
        for colIndx in orderby:
            allIntDict[colIndx] = True
            for dictEntry in sortlist:
                try:
                    int((list(dictEntry.items()))[0][1][colIndx])
                except:  # noqa: E722 pylint: disable=bare-except
                    allIntDict[colIndx] = False
                    if self.__verbose and self.__debug:
                        logger.debug("-- instance of colIndx '%s' found to be non integer value.", colIndx)
                    break

        for colIndx in reversed(orderby):
            if allIntDict[colIndx]:
                # The cell-var-from-loop is probably real error - code never worked
                sortlist.sort(key=lambda dictEntry: int((list(dictEntry.items()))[0][1][colIndx]), reverse=(colIndx in desc))  # pylint: disable=cell-var-from-loop
            else:
                sortlist.sort(key=lambda dictEntry: (list(dictEntry.items()))[0][1][colIndx], reverse=(colIndx in desc))  # pylint: disable=cell-var-from-loop

        return sortlist

    def __setMenuConfigTypes(self, p_currViewId, p_topLevelMenuList, p_dictViewInfo):

        menuTypeDict = {}
        bCombined = None
        for topLevelMenuChoice in p_topLevelMenuList:  # topLevelMenuChoice is the descriptor of the individual choices in "navigation" menu bar at top of page
            dropDownLst = p_dictViewInfo.getCategoryGroupListInMenu(viewId=p_currViewId, menuName=topLevelMenuChoice)
            # for each topLevelMenuChoice there can be an associated dropDownLst of descriptors that form the potential choices in a drop-down list
            # each descriptor has one-to-one relationship with a single cif category to be shown for potential editing

            bCombined = True
            # bCombined is flag to indicate whether clicking on given choice will result in the display of more than one cif category in the editor's main pane,
            # i.e. combined/simulatenous viewing of > 1 cif category

            drpDwnName = ""

            if len(dropDownLst) > 1:
                # if there is more than one descriptor in dropDownLst we check for two situations:
                # 1). if they are all equivalent to each other then there is no need to display several drop-down choices that all have the same label,
                #     and so this indicates that the corresponding cif categories are to be shown via user clicking on the topLevelMenuChoice (i.e. no drop-down list required)
                # 2). if one descriptor differs from the previous then this warrants the display of a drop-down list with distinct drop-down choices underneath
                #     the topLevelMenuChoice

                # The way the pdbx_display_view_info.cif config file is composed, the above two scenarios are the only *intended* possibilities
                # Acknowledging that this handling is non-intuitive and warrants a re-examination of the structure of the cif file governing editor display config
                # as current use/expectations of the UI have evolved to stray from the original design/strategy/purpose of the cif config file.
                #
                for idx, drpDwnName in enumerate(dropDownLst):
                    if idx > 0:
                        if drpDwnName != dropDownLst[idx - 1]:
                            # if one of the descriptors differs from the previous then we have distict drop down labels to display, i.e. *not* combined
                            bCombined = False
            else:
                # else there was only one descriptor in the dropDownLst, so no other descriptor choice to combine with
                bCombined = False

            if bCombined and (topLevelMenuChoice == drpDwnName):
                # if combined/simultaneous viewing is current case and the dropDwnName is same as topLevelMenuChoice then silly to show drop-down list with single choice/descriptor that
                # is equivalent to topLevelMenuChoice, so just need topLevelMenuChoice to be actionable upon click (i.e. no drop-down needed)
                menuTypeDict[topLevelMenuChoice] = "no_dropdown"
            else:
                menuTypeDict[topLevelMenuChoice] = "dropdown" if len(dropDownLst) > 1 else "no_dropdown"

        return menuTypeDict

    def __getConfigViewId(self):

        if self.__verbose and self.__debug:
            for value in self.__expMethodList:
                logger.info("value found in self.__expMethodList: %s", value)

        emViewModel = str(self.__reqObj.getValue("emmodelview"))

        # if( self.__context is None or len(self.__context)==0 ):
        #    currViewId = "AV1"  #default view
        # elif ( self.__context in ["emtesting", "em"] ) or ( "ELECTRON MICROSCOPY" in self.__expMethodList ) or ( "ELECTRON CRYSTALLOGRAPHY" in self.__expMethodList )#:
        #         currViewId = "EM2" if( emViewModel == "n" or emViewModel == "") else "EM1"
        #        elif ( self.__context in ["nmrtesting", "nmr"] ) or ( "SOLID-STATE NMR" in self.__expMethodList ) or ( "SOLUTION NMR" in self.__expMethodList ):
        #            currViewId = "NMR1"
        # if self.__context == "summaryreport":
        #    currViewId = "AV1"

        # Context summaryreport from wf
        if self.__defView:
            currViewId = self.__defView
        elif self.__context == "annotation":
            currViewId = "AV2"
        elif self.__context == "entityfix":
            currViewId = "AV3"
        elif self.__context == "editorconfig":
            currViewId = "CE1"
        else:
            currViewId = "AV1"  # default view

        # EM specific swicthing
        if currViewId == "EM1":
            if emViewModel == "n" or emViewModel == "":
                currViewId = "EM2"

        if self.__verbose:
            logger.info("returning currViewId as: %s", currViewId)
        return currViewId

    def __purgeSkeletonRows(self, p_myPersist):
        """ "skeleton" rows are those that rows that were never updated with real data, and should be purged.
        these rows could have resulted either from the CIF editor's actions of creating "skeleton" categories for those that did not originally
        exist in the datafile, OR these rows could have come in as "junk" rows from the deposition process
        """
        bSuccess = True

        if not self.__pdbxDictStore:
            self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)
        #
        #  the purgeSkeletonRowList is a list of categories for which "junk" rows are to be deleted,
        #  regardless of whether or not the CIF editor created the row as a dummy placeholder
        #
        purgeCategoryList = list(EditorConfig.purgeSkeletonRowList)
        #
        if os.access(self.__skltnLstFlPath, os.R_OK):
            try:
                ifh = open(self.__skltnLstFlPath, "r")
                for line in ifh:
                    ctgryName = line.strip()
                    if ctgryName not in purgeCategoryList:
                        if self.__verbose:
                            logger.info("Adding category '%s' to purgeCategoryList, %r", ctgryName, purgeCategoryList)
                        purgeCategoryList.append(ctgryName)
                ifh.close()
            except:  # noqa: E722 pylint: disable=bare-except
                logger.exception("In __purgeSkeltonRows")
        #
        # Get list of categories in file
        cindex = p_myPersist.getIndex(self.__dbFilePath)
        storectgries = cindex.get(self.__dataBlockName, None)
        logger.debug("Categories present %s", storectgries)
        #
        for cifCtgryNm in purgeCategoryList:

            if storectgries is not None and cifCtgryNm not in storectgries:
                logger.debug("Skip purge of %s as not present", cifCtgryNm)
                continue

            ctgryObj = p_myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, cifCtgryNm)
            #
            if ctgryObj:
                logger.debug("Purge category %s", cifCtgryNm)
                # can use attributeList here
                ctgryMetaDict = self.__getCifCtgryMetaDict(p_sCtgryName=cifCtgryNm, p_bCreateStub=True)
                #
                primaryKeyListFrmDict = ctgryMetaDict["PRIMARY_KEYS"]
                defaultValuesFrmDict = ctgryMetaDict["COLUMN_DEFAULT_VALUES"]
                #
                excludeList = list(EditorConfig.autoIncrExclList)
                excludeList.extend(
                    ["entity_src_nat.entity_id", "entity_src_gen.entity_id", "pdbx_entity_src_syn.entity_id", "pdbx_entity_src_syn.pdbx_src_id", "database_PDB_caveat.id"]
                )
                excludeList.extend(
                    [
                        "pdbx_refine_tls_group.id",
                        "struct_ncs_ens.id",
                        "struct_ncs_dom.id",
                        "struct_ncs_dom.pdbx_ens_id",
                        "struct_ncs_dom_lim.dom_id",
                        "struct_ncs_dom_lim.pdbx_component_id",
                        "struct_ncs_dom_lim.pdbx_ens_id",
                        "struct_mon_prot_cis.pdbx_id",
                    ]
                )
                # excludeList is list of items that are excluded from "auto-increment" feature for ordinal IDs and we need to know about these
                # here because these cannot be used as evidence of "cif-null" values when we judge whether or not an item was updated with real data.
                #
                rowList = ctgryObj.getRowList()
                #
                attributeList = ctgryObj.getAttributeList()
                #
                attribDict = {}
                rowsBeingDeleted = []
                #
                for iNdx, attributeNm in enumerate(attributeList):
                    attribDict[iNdx] = attributeNm

                for rowIdx, record in enumerate(rowList):
                    bRemoveRow = True

                    for colIdx, value in enumerate(record):
                        bSpecialTreatmentAttribute = False
                        attributeNm = attribDict[colIdx]
                        defaultVal = ctgryMetaDict["COLUMN_DEFAULT_VALUES"].get(attributeNm, "none")
                        if cifCtgryNm + "." + attributeNm == "pdbx_database_related.content_type":
                            defaultVal = "unspecified"  # RPS, 2014-12-19 --> NOTE: THIS SHOULD ACTUALLY BE DONE VIA A DICTIONARY UPDATE
                        #
                        if (cifCtgryNm + "." + attributeNm in EditorConfig.autoIncrDecrList) or (
                            ("id" in attributeNm) and (attributeNm in primaryKeyListFrmDict) and (cifCtgryNm + "." + attributeNm not in excludeList)
                        ):
                            bSpecialTreatmentAttribute = True
                            # i.e. specialTreatment means that these were autoincremented as is default behavior for ordinal ID items
                        #
                        if value != "?" and value != "." and not bSpecialTreatmentAttribute:
                            if defaultVal == "none":
                                bRemoveRow = False
                            elif value != defaultVal:
                                bRemoveRow = False
                    #
                    if bRemoveRow:
                        if self.__debug:
                            logger.debug("bRemoveRow is '%s' so adding rowIdx [%s] to rowsBeingDeleted, %r for cifCtgryNm, '%s'", bRemoveRow, rowIdx, rowsBeingDeleted, cifCtgryNm)
                            #
                        if rowIdx not in rowsBeingDeleted:
                            rowsBeingDeleted.append(rowIdx)

                if len(rowsBeingDeleted) > 0:
                    for rowIndx in reversed(rowsBeingDeleted):
                        rowBeingDeleted = rowList.pop(rowIndx)

                        if self.__verbose:
                            logger.info("Going to update category '%s' by deleting row #%s, %r", cifCtgryNm, rowIndx, rowBeingDeleted)
                            logger.info("Attribute list retrieved from ctgryObj is: %s", str(attributeList))
                            logger.info("Primary key list retrieved from metaDict is: %s", str(primaryKeyListFrmDict))

                            logger.info("Default Values retrieved from metaDict is: %r", defaultValuesFrmDict)
                    #
                    ctgryObj.setRowList(rowList)

                    bSuccess = p_myPersist.updateOneObject(ctgryObj, self.__dbFilePath, self.__dataBlockName)
                    if self.__debug:
                        logger.debug("++++++++++++ just after call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
                    #
                else:
                    if self.__verbose:
                        logger.info("NO rows being deleted for category '%s'", cifCtgryNm)

        return bSuccess

    def __orderAuthors(self, p_ctgryName, p_myPersist):
        """enforce ordering of authors based on pdbx_ordinal values"""
        bSuccess = True

        if not self.__pdbxDictStore:
            self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)
        #
        if p_ctgryName == "audit_author":
            targetAttributeNm = "pdbx_ordinal"
        elif p_ctgryName == "citation_author":
            targetAttributeNm = "ordinal"
        elif p_ctgryName == "em_author_list":
            targetAttributeNm = "ordinal"

        ctgryObj = p_myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, p_ctgryName)
        #
        if ctgryObj:
            rowList = ctgryObj.getRowList()
            #
            attributeList = ctgryObj.getAttributeList()
            #
            indxOrdinal = -1
            for iNdx, attributeNm in enumerate(attributeList):
                if attributeNm == targetAttributeNm:
                    indxOrdinal = iNdx
                    break

            if indxOrdinal >= 0:
                rowList.sort(key=lambda authorRecord: int(authorRecord[indxOrdinal]))
                ctgryObj.setRowList(rowList)
                bSuccess = p_myPersist.updateOneObject(ctgryObj, self.__dbFilePath, self.__dataBlockName)
                if self.__debug:
                    logger.debug("++++++++++++ just after call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
                    logger.debug("++++++++++++ just after call to myPersist.updateOneObject and bSuccess is %s", bSuccess)
                #
            else:
                if self.__verbose:
                    logger.info("unable to identify '%s.%s' in data.", p_ctgryName, targetAttributeNm)
        else:
            if self.__verbose:
                logger.info("'%s' category not found in data.", p_ctgryName)

        return bSuccess

    def propagateTitle(self, p_targetCtgry):
        """copy title to/from citation from/to struct"""
        if os.access(self.__dbFilePath, os.R_OK):

            origTitleValue = None
            bSuccess = True
            myPersist = PdbxPersist(self.__verbose, self.__lfh)

            if not self.__pdbxDictStore:
                self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)
            #
            targetAttributeNm = "title"
            if p_targetCtgry == "struct":
                srcCtgry = "citation"
            elif p_targetCtgry == "citation":
                srcCtgry = "struct"

            srcCtgryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, srcCtgry)
            targetCtgryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, p_targetCtgry)
            #
            if srcCtgryObj:
                srcRowList = srcCtgryObj.getRowList()
                #
                srcAttributeList = srcCtgryObj.getAttributeList()
                #
                indxSrcTitle = -1
                indxSrcId = -1
                for iNdx, attributeNm in enumerate(srcAttributeList):
                    if attributeNm == targetAttributeNm:
                        indxSrcTitle = iNdx
                    if srcCtgry == "citation":
                        if attributeNm == "id":
                            indxSrcId = iNdx

                if indxSrcTitle >= 0:
                    for _rowNum, row in enumerate(srcRowList):
                        if indxSrcId >= 0:
                            if row[indxSrcId] == "primary":
                                srcTitleValue = row[indxSrcTitle]
                        else:
                            srcTitleValue = row[indxSrcTitle]

                    if self.__verbose:
                        logger.info("title '%s' from source category '%s' obtained", srcTitleValue, srcCtgry)

                    targetRowList = targetCtgryObj.getRowList()
                    #
                    targetAttributeList = targetCtgryObj.getAttributeList()
                    #
                    idxTargetTitle = -1
                    idxTargetId = -1
                    targetRowNmbr = 0
                    for idx, attribNm in enumerate(targetAttributeList):
                        if attribNm == targetAttributeNm:
                            idxTargetTitle = idx
                        if p_targetCtgry == "citation":
                            if attribNm == "id":
                                idxTargetId = idx

                    if idxTargetTitle >= 0:

                        for rowNmbr, record in enumerate(targetRowList):
                            if idxTargetId >= 0:
                                if record[idxTargetId] == "primary":
                                    targetTitleValue = record[idxTargetTitle]
                                    targetRowNmbr = rowNmbr
                            else:
                                targetTitleValue = record[idxTargetTitle]

                        if self.__verbose:
                            logger.inf("title '%s' from target category '%s' obtained from row# %s", targetTitleValue, p_targetCtgry, targetRowNmbr)

                        origTitleValue = targetTitleValue
                        targetCtgryObj.setValue(srcTitleValue, targetAttributeNm, targetRowNmbr)

                        bSuccess = myPersist.updateOneObject(targetCtgryObj, self.__dbFilePath, self.__dataBlockName)
                        #
                else:
                    if self.__verbose:
                        logger.info("unable to identify '%s.%s' in data.", srcCtgry, targetAttributeNm)
            else:
                if self.__verbose:
                    logger.info("'%s' category not found in data.", srcCtgry)

        return bSuccess, origTitleValue

    def __createSkeletonCtgryContainer(self, p_myPersist, p_ctgryNm):

        bSuccess = False
        rtrnList = []
        # localExclList = ["entity_src_nat.entity_id", "entity_src_gen.entity_id", "pdbx_entity_src_syn.entity_id"]
        # localExclList = ["pdbx_refine_tls_group"]  <--- add category names to this list to prevent skeleton row from being auto provided
        localExclList = ["TESTING"]

        if not self.__pdbxDictStore:
            self.__pdbxDictStore = PdbxDictionaryInfoStore(verbose=self.__verbose, log=self.__lfh)
        #
        # ctgryMetaDict = self.__pdbxDictStore.fetchOneObject(dbFileName=self.__dictDbFilePath,objectName=p_ctgryNm)
        ctgryMetaDict = self.__getCifCtgryMetaDict(p_sCtgryName=p_ctgryNm, p_bCreateStub=True)
        #
        aCatObj = DataCategory(p_ctgryNm)
        rowToAdd = []
        attributeList = ctgryMetaDict["COLUMN_NAMES"]
        for attributeNm in attributeList:
            if self.__debug:
                logger.debug("++++++++++++ building skeleton cifCategory container with attribute: %s", attributeNm)
            #
            aCatObj.appendAttribute(attributeNm)

        rowToAdd = self.__genRowOfDefaultValues(p_ctgryNm, ctgryMetaDict, attributeList, "__createSkeletonCtgryContainer")

        if p_ctgryNm not in localExclList:
            aCatObj.append(rowToAdd)
        bSuccess = p_myPersist.updateOneObject(aCatObj, self.__dbFilePath, self.__dataBlockName)
        if self.__debug:
            logger.debug("just after call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        #
        if bSuccess:
            ofh = open(self.__skltnLstFlPath, "a")
            ofh.write("%s\n" % p_ctgryNm)
            ofh.close()
            #
            rtrnList = aCatObj.getAttributeList()

        return bSuccess, rtrnList

    def __generateMissingCtgryItems(self, p_categoryNm, p_ctgryColList, p_attribsForDisplay):

        bSuccess = False
        bUpdateRequired = False
        attribsToAdd = []
        #
        if self.__verbose:
            logger.info("p_attribsForDisplay is: %r", p_attribsForDisplay)
        for attribName in p_attribsForDisplay:
            if attribName not in p_ctgryColList:
                if self.__verbose:
                    logger.info("identified missing attrib '%s' for category '%s'", attribName, p_categoryNm)
                bUpdateRequired = True
                p_ctgryColList.append(attribName)
                attribsToAdd.append(attribName)
        #
        if bUpdateRequired:
            myPersist = PdbxPersist(self.__verbose, self.__lfh)
            #
            if self.__verbose:
                logger.info("Need to supply placeholder(s) for missing cif items for category: '%s'", p_categoryNm)
            #
            categoryObj = myPersist.fetchOneObject(self.__dbFilePath, self.__dataBlockName, p_categoryNm)
            #
            for attribNm in attribsToAdd:
                categoryObj.appendAttributeExtendRows(attribNm)
            fullRsltSet = categoryObj.getRowList()
            #
            if self.__debug:
                logger.debug("fullRsltSet is now %r", fullRsltSet)
            #
            bSuccess = myPersist.updateOneObject(categoryObj, self.__dbFilePath, self.__dataBlockName)
            if self.__debug:
                logger.debug("++++++++++++ just after call to myPersist.updateOneObject at %s", time.strftime("%Y %m %d %H:%M:%S", time.localtime()))
        else:
            bSuccess = True
        #
        return bSuccess

    def __convertNamesToColIndxs(self, p_ctgryColList, p_data):
        """Convert attribute name oriented config data to colIndex oriented form
        This is needed because cif data from datafiles is organized such that order of columns/attributes
        is arbitrary and so we cannot assume that column ordering in the datafile will match order of columns/attributes
        that is used in the metadictionary definitions for a given category.
        So must match metadata from dictionary to given columns in the datafile based on name and not column position.

         :param `p_data`:  list or dictionary of category/table config details specified relative to column names
                         this info is obtained from the dictionary
         :param `p_ctgryColList`:     list of cif category attributes identified in the data file.

        """
        rtrnData = None
        colNameToIdxDict = {}
        # generate dictionary mapping of column name to column index for data from the datafile
        for idx, name in enumerate(p_ctgryColList):
            colNameToIdxDict[name] = idx

        # if self.__verbose:
        #    logger.info("colNameToIdxDict generated as %r\n", colNameToIdxDict.items())

        # using the dictionary generated above to generate col index oriented version of the config details
        if type(p_data) is list:
            rtrnData = []
            for colName in p_data:
                if colName in colNameToIdxDict:
                    # NOTE: should address cases where colName is specified by dictionary but not present in the data
                    rtrnData.append(colNameToIdxDict[colName])

        elif type(p_data) is dict:
            rtrnData = {}
            for colName, val in p_data.items():
                if colName in colNameToIdxDict:
                    # NOTE: again, should address cases where colName is specified by dictionary but not present in the data
                    rtrnData[colNameToIdxDict[colName]] = val

        return rtrnData

    def __encodeUtf8ToCif(self, p_content):
        """Encoding unicode/utf-8 content into cif friendly ascii"""
        text = p_content.encode("ascii", "xmlcharrefreplace")
        if sys.version_info[0] > 2:
            text = text.decode("ascii")
        return text

    def __regexValidation(self, p_ctgryMetaDict, p_ctgryNm, p_attributeNm, p_newValue):
        """Perform validation check of proposed edit against regular expression constraints for the given
        cif category.attribute

         :param `p_ctgryMetaDict`:  dictionary of cif metatdata
         :param `p_ctgryNm`:        name of cif category for which update applies
         :param `p_attributeNm`:    name of attribute in category for which update applies
         :param `p_newValue`:       value being submitted as updated data

        """
        #
        bPasses = False
        sAsciiSafeMsg = ""
        #
        if EditorConfig.bAccommodatingUnicode and p_ctgryNm + "." + p_attributeNm in EditorConfig.itemsAllowingUnicodeAccommodation:
            p_newValue = self.__encodeUtf8ToCif(p_newValue)
        #
        regexDict = p_ctgryMetaDict["COLUMN_REGEX_ALT"] if len(p_ctgryMetaDict["COLUMN_REGEX_ALT"]) > 0 else p_ctgryMetaDict["COLUMN_REGEX"]
        regEx = regexDict.get(p_attributeNm, None)
        if regEx:
            regEx += "$"
            if self.__debug:
                logger.debug("COLUMN_REGEX(_ALT) obtained for '%s.%s' as %r", p_ctgryNm, p_attributeNm, regEx)
            #
            regExPttrn = re.compile(regEx)
            matchObj = regExPttrn.match(p_newValue)
            if matchObj:
                if self.__verbose:
                    logger.info("new value of '%r' passes validation against COLUMN_REGEX for '%s.%s' as %r", p_newValue, p_ctgryNm, p_attributeNm, regEx)
                bPasses = True
            else:
                if self.__verbose:
                    logger.info(" new value of '%r' failed validation against COLUMN_REGEX for '%s.%s' as %r", p_newValue, p_ctgryNm, p_attributeNm, regEx)
                bPasses = False

                # when failure occurs, we submit value to ascii safe conversion (uses XML char references to replace any unicode)
                # if converted value passes regex check, then indicates presence of offending non-ascii/unicode character
                if not EditorConfig.bAccommodatingUnicode:
                    newValueAsciiSafe = self.__encodeUtf8ToCif(p_newValue)
                    matchObjAsciiSafeCheck = regExPttrn.match(newValueAsciiSafe)
                    if matchObjAsciiSafeCheck:
                        sAsciiSafeMsg = "Non-ascii character in input. Please correct. "

        else:
            if self.__verbose:
                logger.info(" no COLUMN_REGEX(_ALT) defined for '%s.%s'", p_ctgryNm, p_attributeNm)
            #
            bPasses = True
        #

        return (bPasses, "New value, '" + p_newValue + "', does not satisfy expected data type and/or format. " + sAsciiSafeMsg)

    def __testIntBoundary(self, value, lB, uB, limitType):
        if "." in value:
            value = float(value)

        if lB == uB:
            if int(value) == int(lB):
                return (True, "pass")
            else:
                return (False, "")
        else:
            if lB != "." and int(value) < int(lB):
                return (False, "Submitted value of '" + str(value) + "' falls below " + limitType + " lower limit of: " + str(lB) + ".")
            if uB != "." and int(value) > int(uB):
                return (False, "Submitted value of '" + str(value) + "' exceeds " + limitType + " upper limit of: " + str(uB) + ".")
            return (True, "pass")

    def __testFloatBoundary(self, value, lB, uB, limitType):
        # this equivalence comparison is a bit dicey --
        if lB == uB:
            if float(value) == float(lB):
                return (True, "pass")
            else:
                return (False, "")
        else:
            if lB != "." and float(value) < float(lB):
                return (False, "Submitted value of '" + str(value) + "' falls below " + limitType + " lower limit of: " + lB + ".")
            if uB != "." and float(value) > float(uB):
                return (False, "Submitted value of '" + str(value) + "' exceeds " + limitType + " upper limit of: " + uB + ".")
            return (True, "pass")

    def __boundaryValidation(self, p_ctgryMetaDict, p_ctgryNm, p_attributeNm, p_newValue):
        """Perform validation check of proposed edit against boundary constraints for the given
        cif category.attribute

         :param `p_ctgryMetaDict`:  dictionary of cif metatdata
         :param `p_ctgryNm`:        name of cif category for which update applies
         :param `p_attributeNm`:    name of attribute in category for which update applies
         :param `p_newValue`:       value being submitted as updated data

        """
        #
        rtrnTupl = (True, "n.a.", "n.a.")  # default
        #
        failSummaryMsg = ""
        #
        try:
            bndryDictSoft = p_ctgryMetaDict["COLUMN_BOUNDARY_VALUES_ALT"] if len(p_ctgryMetaDict["COLUMN_BOUNDARY_VALUES_ALT"]) > 0 else None
            bndryDictHard = p_ctgryMetaDict["COLUMN_BOUNDARY_VALUES"] if len(p_ctgryMetaDict["COLUMN_BOUNDARY_VALUES"]) > 0 else None

            if bndryDictSoft is None and bndryDictHard is None:
                if self.__verbose:
                    logger.info("no COLUMN_BOUNDARY_VALUES(_ALT) defined for '%s.%s'", p_ctgryNm, p_attributeNm)

            else:
                if bndryDictHard:
                    if self.__verbose:
                        logger.info("Checking against 'hard' COLUMN_BOUNDARY_VALUES for '%s.%s'", p_ctgryNm, p_attributeNm)
                    #
                    rsltTupl = self.__checkAgainstBoundaries(p_ctgryNm, bndryDictHard, p_attributeNm, p_newValue, "hard")

                    if rsltTupl[0] is False:
                        failSummaryMsg = rsltTupl[1]
                        rtrnTupl = (False, failSummaryMsg, "hard")
                        return rtrnTupl
                    else:
                        if bndryDictSoft:
                            if self.__verbose:
                                logger.info("Checking against 'soft' COLUMN_BOUNDARY_VALUES_ALT for '%s.%s'", p_ctgryNm, p_attributeNm)

                            rsltTupl = self.__checkAgainstBoundaries(p_ctgryNm, bndryDictSoft, p_attributeNm, p_newValue, "soft")
                            if rsltTupl[0] is False:
                                failSummaryMsg = rsltTupl[1]
                                rtrnTupl = (False, failSummaryMsg, "soft")
                                return rtrnTupl
                else:
                    if self.__verbose:
                        logger.info("No 'hard' boundary limits for '%s.%s'", p_ctgryNm, p_attributeNm)
                    if bndryDictSoft:
                        if self.__verbose:
                            logger.info("Proceeding to check against 'soft' COLUMN_BOUNDARY_VALUES_ALT for '%s.%s'", p_ctgryNm, p_attributeNm)

                        rsltTupl = self.__checkAgainstBoundaries(p_ctgryNm, bndryDictSoft, p_attributeNm, p_newValue, "soft")
                        if rsltTupl[0] is False:
                            failSummaryMsg = rsltTupl[1]
                            rtrnTupl = (False, failSummaryMsg, "soft")
                            return rtrnTupl
            #
        except Exception as _e:  # noqa: F841
            rtrnTupl = (False, "Problem during validation of '" + p_newValue + "'.", "n.a")
            if self.__verbose:
                logger.exception("Issue during validation")
                logger.info("Problem during validation of new value of '%s' for '%s.%s'", p_newValue, p_ctgryNm, p_attributeNm)
        #
        return rtrnTupl

    def __checkAgainstBoundaries(self, p_ctgryNm, p_bndryDict, p_attributeNm, p_newValue, p_limitType):
        #
        rtrnTupl = (False, "'" + p_newValue + "' failed validation")  # default
        #
        failSummaryMsg = ""
        separator = ""
        #
        bList = p_bndryDict.get(p_attributeNm, None)
        if bList:
            try:
                for (lB, uB) in bList:
                    if len(failSummaryMsg) > 0:
                        separator = " "
                    if ((len(lB) > 1) and "." in lB) or ((len(uB) > 1) and "." in uB):
                        if self.__verbose and self.__debug:
                            logger.info("(checkBoundaryValues) testing constraint as float %s %s", lB, uB)
                        rtrnTupl = self.__testFloatBoundary(p_newValue, lB, uB, p_limitType)
                        if rtrnTupl[0] is True:
                            if self.__verbose:
                                logger.info(
                                    "new value of '%s' passes validation against float COLUMN_BOUNDARY_VALUES(_ALT) for '%s.%s' as %r", p_newValue, p_ctgryNm, p_attributeNm, bList
                                )
                            return rtrnTupl
                        elif rtrnTupl[0] is False:
                            if failSummaryMsg != rtrnTupl[1] and len(rtrnTupl[1]) > 1:  # to prevent duplicate messages
                                failSummaryMsg += separator + rtrnTupl[1]
                            if self.__verbose:
                                logger.info(
                                    "new value of '%s' failed validation against float COLUMN_BOUNDARY_VALUES(_ALT) of %r for '%s.%s' for reason: %s",
                                    p_newValue,
                                    bList,
                                    p_ctgryNm,
                                    p_attributeNm,
                                    failSummaryMsg,
                                )
                        #
                    else:
                        if self.__verbose and self.__debug:
                            logger.info("(checkBoundaryValues) testing constraint as integer %s %s", lB, uB)
                        rtrnTupl = self.__testIntBoundary(p_newValue, lB, uB, p_limitType)
                        if rtrnTupl[0] is True:
                            if self.__verbose:
                                logger.info(
                                    "new value of '%s' passes validation against integer COLUMN_BOUNDARY_VALUES(_ALT) for '%s.%s' as %r",
                                    p_newValue,
                                    p_ctgryNm,
                                    p_attributeNm,
                                    bList,
                                )
                            return rtrnTupl
                        elif rtrnTupl[0] is False:
                            if failSummaryMsg != rtrnTupl[1]:
                                failSummaryMsg += separator + rtrnTupl[1]
                            if self.__verbose:
                                logger.info(
                                    "new value of '%s' failed validation against integer COLUMN_BOUNDARY_VALUES(_ALT) of %r for '%s.%s' for reason: %s",
                                    p_newValue,
                                    bList,
                                    p_ctgryNm,
                                    p_attributeNm,
                                    failSummaryMsg,
                                )
                            #
            except Exception as _e:  # noqa: F841
                if self.__verbose:
                    logger.exception("In boundary check")
                    logger.info("new value of '%s' failed validation against COLUMN_BOUNDARY_VALUES(_ALT) for '%s.%s' as %r", p_newValue, p_ctgryNm, p_attributeNm, bList)
                rtrnTupl = (False, "New value of '" + p_newValue + "' failed validation.")
                #
        else:
            if self.__verbose:
                logger.info("no COLUMN_BOUNDARY_VALUES(_ALT) defined for '%s.%s'", p_ctgryNm, p_attributeNm)
            #
            rtrnTupl = (True, "n.a.")
        #
        if rtrnTupl[0] is False:
            rtrnTupl = (False, failSummaryMsg)
            if self.__verbose:
                logger.info(
                    "new value of '%s' failed validation against COLUMN_BOUNDARY_VALUES(_ALT) of %r for '%s.%s' for reason: %s",
                    p_newValue,
                    bList,
                    p_ctgryNm,
                    p_attributeNm,
                    failSummaryMsg,
                )
        return rtrnTupl

    def __filterRsltSet(self, p_rsltSetList, p_sGlobalSrchFilter=None, p_dictColSrchFilter=None):
        """Performs filtering of resultset. Accommodates two mutually-exclusive filter modes: global search and column specific search modes.

        :Params:
            :param `p_sGlobalSrchFilter`:      DataTables related parameter indicating global search term against which records will be filtered
            :param `p_dictColSrchFilter`:      DataTables related parameter indicating column-specific search term against which records will be filtered

        """
        fltrdList = []

        if p_sGlobalSrchFilter:
            if self.__verbose and self.__debug:
                logger.debug("performing global search for string '%s'", p_sGlobalSrchFilter)
            for trueIndxdRcrdDict in p_rsltSetList:
                _trueIndxKey, rcrdValue = (list(trueIndxdRcrdDict.items()))[0]
                for field in rcrdValue:
                    if p_sGlobalSrchFilter.lower() in str(field).lower():
                        fltrdList.append(trueIndxdRcrdDict)
                        break
        elif p_dictColSrchFilter:
            if self.__verbose and self.__debug:
                logger.debug("performing column-specific searches with search dictionary: %r", list(p_dictColSrchFilter.items()))
                logger.debug("performing column-specific searches against recordset: %r", p_rsltSetList)
            #
            bAllCriteriaMet = False
            for trueIndxdRcrdDict in p_rsltSetList:
                _trueRowIdx, rcrd = (list(trueIndxdRcrdDict.items()))[0]
                #
                for key in list(p_dictColSrchFilter.keys()):
                    if p_dictColSrchFilter[key].lower() in str(rcrd[key]).lower():
                        bAllCriteriaMet = True
                    else:
                        bAllCriteriaMet = False
                        break
                #
                if bAllCriteriaMet:
                    # again appending in form of dictionary as per explanation in block for global search filtering above
                    fltrdList.append(trueIndxdRcrdDict)

        return fltrdList

    def __isWorkflow(self):
        """Determine if currently operating in Workflow Managed environment

        :Returns:
            boolean indicating whether or not currently operating in Workflow Managed environment
        """
        #
        fileSource = str(self.__reqObj.getValue("filesource")).lower()
        #
        if fileSource and fileSource in ["archive", "wf-archive", "wf_archive", "wf-instance", "wf_instance"]:
            # if the file source is any of the above then we are in the workflow manager environment
            return True
        else:
            # else we are in the standalone dev environment
            return False

    def __attributePart(self, name):
        i = name.find(".")
        if i == -1:
            return None
        else:
            return name[i + 1 :]
