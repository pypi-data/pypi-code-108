import csv
import shelve
import time
import json

from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions

global kb_cve_qid_list # Holds csv-> qid dictionary
global count_qids_written_to_shelve


def prepare_csv_cell(csv_cell, csv_column, qid, present_csv_cell_as_json=False):
    discarded_data = ""
    if csv_cell is None:
        csv_cell = ""
    elif 'DATETIME' in csv_column:  # Prepare dates for use in Excel or Database
        csv_cell = csv_cell.replace("T", " ").replace("Z", "")
    elif csv_column == 'CVE_LIST':
        if present_csv_cell_as_json:
            discarded_data = kb_update_cve_qid_list(csv_cell, qid)
            csv_cell = json.dumps(csv_cell)
        else:
            csv_cell = kb_update_cve_qid_list(csv_cell, qid)
    elif not isinstance(csv_cell, str):  # Flatten Nested XML into String
        if present_csv_cell_as_json:
            csv_cell = json.dumps(csv_cell)
        else:
            flatten = etld_lib_functions.flatten_nest(csv_cell)
            csv_cell = ""
            for key in flatten.keys():
                csv_cell = f"{csv_cell}{key}:{flatten[key]}\n"

    return csv_cell


def kb_create_csv_from_shelve(no_truncation=False):
    global kb_cve_qid_list
    global count_qids_written_to_shelve
    count_qids_written_to_shelve = 0
    counter_obj = \
        etld_lib_functions.DisplayCounterToLog(display_counter_at=10000,
                                               logger_func=etld_lib_functions.logger.info,
                                               display_counter_log_message=
                                               "count knowledgebase records written to csv")
    kb_cve_qid_list = {}
    kb_csv_file = str(etld_lib_config.kb_csv_file)

    csv_columns = etld_lib_config.kb_csv_columns()
    csv_headers = {}
    for header in csv_columns:
        csv_headers[header] = ""
    try:
        with open(kb_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            csv_record = csv_headers.copy()
            # Iterate through Shelve Database
            with shelve.open(str(etld_lib_config.kb_shelve_file), flag='r') as shelve_database:
                for shelve_database_item in shelve_database:
                    kb_item = shelve_database[shelve_database_item]
                    truncated_field_list = "" # Column Name, Length
                    for csv_column in csv_columns:
                        if csv_column in kb_item.keys():
                            kb_item[csv_column] = prepare_csv_cell(kb_item[csv_column], csv_column, kb_item['QID'],
                                                                   etld_lib_config.kb_present_csv_cell_as_json)
                            csv_record[csv_column] = kb_item[csv_column]
                            csv_record[csv_column], truncated_field_list = \
                                etld_lib_functions.truncate_csv_cell(
                                                  max_length=etld_lib_config.kb_csv_truncate_cell_limit,
                                                  csv_cell=kb_item[csv_column],
                                                  truncated_field_list=truncated_field_list,
                                                  csv_column=csv_column)
                        else:
                            if csv_column == 'TRUNCATED_FIELD_LIST':
                                kb_item[csv_column] = truncated_field_list
                                csv_record[csv_column] = kb_item[csv_column]
                            else:
                                csv_record[csv_column] = ""

                    writer.writerow(csv_record)
                    count_qids_written_to_shelve = count_qids_written_to_shelve + 1
                    counter_obj.display_counter_to_log()
                    csv_record = csv_headers.copy()
        counter_obj.display_final_counter_to_log()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error in File: {__file__} Line: {etld_lib_functions.lineno()}")
        etld_lib_functions.logger.error(f"Error writing to file: {str(kb_csv_file)}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def kb_create_cve_qid_shelve():
    global kb_cve_qid_list
    # Write cve -> QID List to shelve.  dumb.dbm has issues.
    try:
        with shelve.open(str(etld_lib_config.kb_cve_qid_map_shelve), flag='n') as kb_cve_qid_list_shelve:
            for i in range(3):
                try:
                    kb_cve_qid_list_shelve.update(kb_cve_qid_list)
                    break
                except Exception as e:
                    time.sleep(2)
                    etld_lib_functions.logger.info(f"Retry writing to {str(etld_lib_config.kb_cve_qid_map_shelve)} ")
                    if i > 2:
                        etld_lib_functions.logger.error(f"Error in File: {__file__} Line: {etld_lib_functions.lineno()}")
                        etld_lib_functions.logger.error(f"Error writing to {str(etld_lib_config.kb_cve_qid_map_shelve)} ")
                        etld_lib_functions.logger.error(f"Exception: {e}")
    except Exception as e:
        etld_lib_functions.logger.error(f"Error writing to file: {str(etld_lib_config.kb_cve_qid_map_shelve)}, "
                              f"please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def kb_update_cve_qid_list(kb_item, qid):
    global kb_cve_qid_list
    kb_cve_list_return = ""
    if 'CVE' in kb_item.keys():
        for key in kb_item['CVE']:
            if isinstance(key, dict):
                kb_cve_list_return = f"{kb_cve_list_return}{key['ID']}\n"
            elif isinstance(key, str):
                kb_cve_list_return = kb_item['CVE']['ID']
        for cve in kb_cve_list_return.splitlines():
            if cve in kb_cve_qid_list:
                kb_cve_qid_list[cve] = f"{kb_cve_qid_list[cve]};{qid}"
            else:
                kb_cve_qid_list[cve] = f"{qid}"
    return kb_cve_list_return


def start_msg_kb_csv():
    etld_lib_functions.logger.info(f"start")


def end_msg_kb_csv():
    global count_qids_written_to_shelve
    etld_lib_functions.logger.info(f"count rows written to csv: {count_qids_written_to_shelve:,}")
    etld_lib_functions.log_file_info(etld_lib_config.kb_shelve_file, 'input file')
    etld_lib_functions.log_dbm_info(etld_lib_config.kb_shelve_file)
    etld_lib_functions.log_file_info(etld_lib_config.kb_csv_file)

    etld_lib_functions.logger.info(f"count rows written to cve to qid shelve: {len(kb_cve_qid_list):,}")
    etld_lib_functions.log_file_info(etld_lib_config.kb_shelve_file, 'input file')
    etld_lib_functions.log_dbm_info(etld_lib_config.kb_shelve_file)
    etld_lib_functions.log_file_info(etld_lib_config.kb_cve_qid_map_shelve)

    etld_lib_functions.logger.info(f"end")


def kb_csv():
    kb_create_csv_from_shelve()
    kb_create_cve_qid_shelve()


def main():
    start_msg_kb_csv()
    kb_csv()
    end_msg_kb_csv()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='kb_load_csv')
    etld_lib_config.main()
    main()
