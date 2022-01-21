import csv

from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
import dbm.gnu
import pickle
import json
global count_host_ids_written


def prepare_csv_cell(csv_cell, csv_column, present_csv_cell_as_json=False):
    if csv_cell is None:
        csv_cell = ""
    elif 'DATE' in csv_column:  # Prepare dates for use in Excel or Database
        csv_cell = csv_cell.replace("T", " ").replace("Z", "")
    elif 'ASSET_GROUP_IDS' in csv_column:  # Prepare IDS for use in Excel
        csv_cell = csv_cell.replace(",", "\n")
    elif not isinstance(csv_cell, str):  # Flatten Nested XML into String
        if present_csv_cell_as_json:
            csv_cell = json.dumps(csv_cell)
        else:
            flatten = etld_lib_functions.flatten_nest(csv_cell)
            csv_cell = ""
            for key in flatten.keys():
                csv_cell = f"{csv_cell}{key}:{flatten[key]}\n"
    return csv_cell


def host_list_to_csv():  # Create CSV File from Shelve Database
    global count_host_ids_written
    host_list_csv_file = etld_lib_config.host_list_csv_file     # Output CSV File
    csv_columns = etld_lib_config.host_list_csv_columns()         # Host List Columns
    count_host_ids_written = 0
    counter_obj = \
        etld_lib_functions.DisplayCounterToLog(display_counter_at=10000,
                                               logger_func=etld_lib_functions.logger.info,
                                               display_counter_log_message="count host list records written to csv")
    csv_headers = {}
    for header in csv_columns:
        csv_headers[header] = ""
    try:
        with open(host_list_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            csv_row = csv_headers.copy()
            # Iterate through Shelve Database
            with dbm.gnu.open(str(etld_lib_config.host_list_shelve_file), 'rf') as shelve_database:
                shelve_database_item = shelve_database.firstkey()
                while shelve_database_item is not None:
                    host_list_item = pickle.loads(shelve_database[shelve_database_item])
                    for csv_column in csv_columns:  # Iterate through expected columns (contract)
                        if csv_column in host_list_item.keys():  # Iterate through columns found in Shelve
                            host_list_item[csv_column] = prepare_csv_cell(
                                                         host_list_item[csv_column], csv_column,
                                                         etld_lib_config.host_list_present_csv_cell_as_json)
                            truncated_field_list = ""
                            csv_row[csv_column], truncated_field_list = \
                                etld_lib_functions.truncate_csv_cell(
                                                  max_length=etld_lib_config.host_list_csv_truncate_cell_limit,
                                                  csv_cell=host_list_item[csv_column],
                                                  truncated_field_list=truncated_field_list,
                                                  csv_column=csv_column)
                        else:
                            csv_row[csv_column] = ""  # Ensure blank is added to each required empty field
                    # Write CSV row, Prepare for next row.
                    writer.writerow(csv_row)
                    count_host_ids_written += 1
                    counter_obj.display_counter_to_log()
                    csv_row = csv_headers.copy()
                    shelve_database_item = shelve_database.nextkey(shelve_database_item)
        counter_obj.display_final_counter_to_log()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error in File: {__file__} Line: {etld_lib_functions.lineno()}")
        etld_lib_functions.logger.error(f"Error writing to file: {str(host_list_csv_file)}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def start_msg_host_list_csv():
    etld_lib_functions.logger.info(f"start")


def end_msg_host_list_csv():
    global count_host_ids_written
    etld_lib_functions.log_file_info(etld_lib_config.host_list_shelve_file, 'input file')
    etld_lib_functions.log_dbm_info(etld_lib_config.host_list_shelve_file)
    etld_lib_functions.log_file_info(etld_lib_config.host_list_csv_file)
    etld_lib_functions.logger.info(f"end")


def host_list_csv():
    host_list_to_csv()


def main():
    start_msg_host_list_csv()
    host_list_csv()
    end_msg_host_list_csv()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_csv')
    etld_lib_config.main()
    main()
