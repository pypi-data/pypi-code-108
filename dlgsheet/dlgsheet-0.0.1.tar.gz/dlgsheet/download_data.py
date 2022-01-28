from pathlib import Path

from dlgsheet.gsheet.api import get_tables, get_table_values
from dlgsheet.utils.to_object import nested_list_to_object
from dlgsheet.logger import logger
from dlgsheet.save_data import save_to_json_file


def download_table_values(sheetname, filename=None, spreadsheetid=None,
                          credentials=None):

    sheets = get_tables(spreadsheetid=spreadsheetid, credentials=credentials)

    if (sheetname not in sheets):
        logger.error("sheet '" + sheetname +
                     "' not in spreadsheet.")
        return exit(-1)

    data = get_table_values(sheetname, spreadsheetid=spreadsheetid,
                            credentials=credentials)

    l_obj = nested_list_to_object(data["values"])

    if (filename is None):
        filename = sheetname + ".json"

    save_to_json_file(l_obj, filename)


def download_all_tables(foldername, spreadsheetid=None, credentials=None):

    folder = Path(foldername)

    sheets = get_tables(spreadsheetid=spreadsheetid, credentials=credentials)

    for sheetname in sheets:
        filename = sheetname + ".json"
        save_filename = folder / filename

        logger.info(
            "Downloading table '" +
            sheetname +
            "' to " +
            str(save_filename))

        data = get_table_values(sheetname, spreadsheetid=spreadsheetid,
                                credentials=credentials)

        l_obj = nested_list_to_object(data["values"])

        save_to_json_file(l_obj, save_filename)


if __name__ == "__main__":
    download_all_tables("output")
