##
# File:  EmHeaderUtils.py
# Date:  20-Oct-2015  J. Westbrook
#
# Update:
#       21-Feb-2016  jdw add releaseHeaderPdbx()
#       23-May-2018  ep  Update to V3 translator API and use logging
"""
Manage map header file operations -


"""
__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.07"

import sys

# import os.path
import traceback
import logging

# import shutil
# from wwpdb.utils.config.ConfigInfo import ConfigInfo
# from wwpdb.utils.config.ConfigInfoApp import ConfigInfoAppEm
# from mmcif_utils.trans.InstanceMapper import InstanceMapper
from wwpdb.utils.emdb.cif_emdb_translator.cif_emdb_translator import CifEMDBTranslator

#

logger = logging.getLogger(__name__)


class EmHeaderUtils(object):
    """
    Manage map header file operations -

    """

    def __init__(self, siteId, verbose=False, log=sys.stderr):
        pass
        # self.__lfh = log
        # self.__siteId = siteId
        # self.__cI = ConfigInfo(self.__siteId)
        # self.__cIA = ConfigInfoAppEm(self.__siteId)
        # self.__mappingFilePath = self.__cIA.get_emd_mapping_file_path()

    # def __mkdir(self, path):
    #     if not os.path.isdir(path):
    #         os.makedirs(path, 0o755)

    # def releaseHeader(self, filePath, emdbId):
    #     ok = False
    #     try:
    #         logger.info("starting for %s", filePath)
    #         upId = str(emdbId).upper()
    #         pth = os.path.join(self.__cI.get("SITE_ARCHIVE_STORAGE_PATH"), "for_release", "emd", upId, "header")
    #         self.__mkdir(pth)
    #         lcId = str(emdbId).lower()
    #         mod_lcId = lcId.replace("-", "_")
    #         fp = os.path.join(pth, mod_lcId + "_v3.xml")
    #         logger.info("copied %s to %s", filePath, fp)
    #         shutil.copyfile(filePath, fp)
    #         ok = True
    #     except:  # noqa: E722
    #         logger.exception("failing for %s", filePath)

    #     return ok

    # def releaseHeaderPdbx(self, filePath, emdbId):
    #     ok = False
    #     try:
    #         logger.info("starting for %s", filePath)
    #         upId = str(emdbId).upper()
    #         pth = os.path.join(self.__cI.get("SITE_ARCHIVE_STORAGE_PATH"), "for_release", "emd", upId)
    #         self.__mkdir(pth)
    #         lcId = str(emdbId).lower()
    #         fp = os.path.join(pth, lcId + ".cif")
    #         logger.info("copied %s to %s", filePath, fp)
    #         shutil.copyfile(filePath, fp)
    #         ok = True
    #     except:  # noqa: E722
    #         logger.exception("failing for %s", filePath)

    #     return ok

    # def transEmd(self, inpFilePath, outFilePath, mode="src-dst", tags=None):
    #     if tags is None:
    #         tags = []

    #     ok = False
    #     try:
    #         im = InstanceMapper(verbose=True, log=sys.stderr)
    #         im.setMappingFilePath(self.__mappingFilePath)
    #         if tags != []:
    #             im.setFilterTagList(tags)
    #         ok = im.translate(inpFilePath, outFilePath, mode=mode)
    #     except:  # noqa: E722
    #         logger.exception("failing for %s", inpFilePath)

    #     return ok

    def transHeader(self, inpFilePath, outFilePath, logFilePath, validateXml=True):
        ok = False
        logging.info("Starting conversion for %s", inpFilePath)
        #
        try:
            translator = CifEMDBTranslator()
            translator.set_logger_logging(log_error=True, error_log_file_name=logFilePath)
            translator.read_emd_map_v2_cif_file()
            if validateXml:
                translator.translate_and_validate(in_cif=inpFilePath, out_xml=outFilePath)
            else:
                translator.translate(in_cif=inpFilePath, out_xml=outFilePath)
            # This will close the output file
            translator.write_logger_logs(write_error_log=True)
            if translator.is_translation_log_empty:
                ok = True
            else:
                ok = False
        except:  # noqa: E722  pylint: disable=bare-except
            logger.exception("Map header translation failed for %s", inpFilePath)
            se = traceback.format_exc()
            fOut = open(logFilePath, "w")
            fOut.write("Exception during XML production\n")
            fOut.write(se)
            fOut.close()

        return ok
