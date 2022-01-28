from optparse import OptionParser
import os
from pathlib import Path

from dlgsheet import config
from dlgsheet.logger import logger, levels, setLoggerLevel
from dlgsheet.gsheet.api import set_credentials
from dlgsheet.download_data import download_table_values, download_all_tables


usage = "usage: %prog [options] tablename"
parser = OptionParser(usage=usage, prog="dlgsheet")
parser.add_option("-l", "--log-level", dest="loglevel",
                  help="set log level. Available options: " + ",".join(levels))
parser.add_option("-c", "--credentials-file", dest="credentials",
                  help="set credentials file name", metavar="FILE")
parser.add_option("-o", "--output-file", dest="output",
                  help="save to output file", metavar="FILE")
parser.add_option("-d", "--output-folder", dest="output_folder",
                  help="save to output folder", metavar="FOLDER")
parser.add_option("-s", "--spreadsheet-id", dest="spreadsheetid",
                  help="set google spreadsheet id to write on")
parser.add_option("-t", "--sheetname", dest="sheetname",
                  help="set google sheetname to write on")

def main():

    (options, _ ) = parser.parse_args()

    if options.loglevel is not None:
        setLoggerLevel(options.loglevel)

    logger.debug(options)

    DEFAULT_FOLDER_NAME = "output"


    if(options.spreadsheetid is not None):
        spreadsheetid = options.spreadsheetid
    else:
        spreadsheetid = config.google["spreadsheetid"]

    if(not spreadsheetid):
        logger.error(
            '''No spreadsheetid defined, either via option --spreadsheet-id or
            environment variable GOOGLE_SPREADSHEET_ID.''')
        exit(-1)

    if(options.credentials is not None):
        credentials = options.credentials
        auth = set_credentials(credentials)
    else:
        credentials = config.google["credentialsfile"]
        logger.warning("No credentials file defined, usign default: " +
                       credentials)
        if(not Path(credentials).exists()):
            logger.error(
                "Default credentials file doesn't exist, skipping. "
                "Download the credentials file and save as 'key.json' "
                "or specify the name by the --credentials-file option."
            )
            exit(-1)
        auth = set_credentials(credentials)

    if(options.sheetname is not None):

        sheetname = options.sheetname
        defaultfilename = os.path.join(DEFAULT_FOLDER_NAME, sheetname + ".json")

        if(options.output is not None):
            filename = options.output
        else:
            filename = defaultfilename
            logger.warning(
                "Not file name provided via --output-file. Usign default: " +
                filename)

        logger.info("Downloading data from spreadsheet: " +
                    spreadsheetid + " from '" +
                    sheetname + "' to " + filename)
        download_table_values(sheetname, filename=filename,
                              spreadsheetid=spreadsheetid, credentials=auth)

        logger.info("Task finished")
        exit(0)

    if(options.output_folder is not None):
        foldername = options.output_folder
    else:
        foldername = DEFAULT_FOLDER_NAME
        logger.warning(
            "Not folder name provided via --output-folder. Usign default: " +
            foldername)

    logger.info("Downloading data from spreadsheet: " +
                spreadsheetid + " to folder " + foldername)
    download_all_tables(foldername=foldername,
                        spreadsheetid=spreadsheetid, credentials=auth)

    logger.info("Task finished")
