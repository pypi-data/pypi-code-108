from dlgsheet.gsheet.api import get_tables, get_table_values
from dlgsheet.utils.to_object import nested_list_to_object
from dlgsheet.logger import logger
import json


def download_data_table(sheetname, filename=None, spreadsheetid=None,
                        credentials=None):

    sheets = get_tables(spreadsheetid=spreadsheetid, credentials=credentials)

    if (sheetname not in sheets):
        logger.error("sheet '" + sheetname +
                       "' not in spreadsheet.")
        return exit(-1)

    data = get_table_values(sheetname, spreadsheetid=spreadsheetid,
                            credentials=credentials)

    l_obj = nested_list_to_object(data)


def uploadTableFromDefaultFile(
        sheetname, tablename, spreadsheetid=None, credentials=None):
    filename = references[tablename]["backupfile"]

    uploadTableFromJSONFile(filename=filename, sheetname=sheetname,
                            tablename=tablename, spreadsheetid=spreadsheetid,
                            credentials=credentials)
    return


def uploadTableFromJSONFile(filename, sheetname,
                            tablename, spreadsheetid=None, credentials=None):
    with open(filename, 'r', encoding='utf8') as json_file:
        data = json.load(json_file)

    uploadTableFromObject(data, sheetname=sheetname, tablename=tablename,
                          spreadsheetid=spreadsheetid, credentials=credentials)


def uploadTableFromObject(obj, sheetname, tablename, spreadsheetid=None,
                          credentials=None, withheader=True):
    reference = references[tablename]
    info = fromJsonToList(
        obj, keys=reference["keys"], breakpoints=reference["breakpoints"])

    sheets = getTables(spreadsheetid=spreadsheetid, credentials=credentials)

    if (sheetname not in sheets):
        logger.warning("sheet '" + sheetname +
                       "' not in spreadsheet. Creating it")
        response = createTable(sheetname, spreadsheetid=spreadsheetid,
                               credentials=credentials)
        logger.debug(response)

    if(withheader):
        info = [reference["header"]] + info
    response = resetTableValues(sheetname, info, spreadsheetid=spreadsheetid,
                                credentials=credentials)
    logger.debug(response)
    return


if __name__ == "__main__":
    uploadTableFromDefaultFile("from_webpage", "commissions")
