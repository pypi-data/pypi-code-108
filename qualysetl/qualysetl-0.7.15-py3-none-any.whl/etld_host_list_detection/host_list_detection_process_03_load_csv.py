import csv
import shelve
import json
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
global count_host_ids_written
global count_host_qids_written
global host_list_detection_item
global host_list_detection_csv_truncate_cell_limit
global host_list_detection_csv_file
global count_csv_records_written
global counter_obj


def prepare_host_info(csv_column, present_csv_cell_as_json=False):
    global host_list_detection_item
    # Prepare host_list_detection_item for csv row
    # Prepare Host List First, then at DETECTION_LIST
    if host_list_detection_item[csv_column] is None:
        host_list_detection_item[csv_column] = ""
    elif 'DATE' in csv_column:  # Prepare dates for use in Excel or Database
        host_list_detection_item[csv_column] = host_list_detection_item[csv_column].replace("T", " ").replace("Z", "")
    elif 'DETECTION_LIST' in csv_column:
        pass
    elif not isinstance(host_list_detection_item[csv_column], str):
        if present_csv_cell_as_json:
            host_list_detection_item[csv_column] = json.dumps(host_list_detection_item[csv_column])
        else:
            flatten = etld_lib_functions.flatten_nest(host_list_detection_item[csv_column])
            host_list_detection_item[csv_column] = ""
            for key in flatten.keys():
                host_list_detection_item[csv_column] = f"{host_list_detection_item[csv_column]}{key}:{flatten[key]}\n"


def prepare_csv_cell(csv_cell, csv_column, present_csv_cell_as_json=False):
    if csv_cell is None:
        csv_cell = ""
    elif 'DATE' in csv_column:  # Prepare dates for use in Excel or Database
        csv_cell = csv_cell.replace("T", " ").replace("Z", "")
    elif 'ASSET_GROUP_IDS' in csv_column:  # Prepare IDS for use in Excel
        if present_csv_cell_as_json:
            csv_cell = json.dumps(csv_cell)
        else:
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


def write_csv_detections_for_one_host(csv_column, csv_headers, writer, csv_detection_columns):
    global host_list_detection_item
    global count_host_ids_written
    global count_host_qids_written
    global count_csv_records_written
    global counter_obj

    def write_csv_host_list_detection_row():
        csv_row = csv_headers.copy()
        for csv_header in csv_headers:
            if csv_header in host_list_detection_item.keys():
                csv_row[csv_header] = \
                    prepare_csv_cell(host_list_detection_item[csv_header], csv_header,
                                     etld_lib_config.host_list_detection_present_csv_cell_as_json)
                csv_row[csv_header], truncated_field_list = etld_lib_functions.truncate_csv_cell(
                    max_length=etld_lib_config.host_list_detection_csv_truncate_cell_limit,
                    csv_cell=host_list_detection_item[csv_header],
                    truncated_field_list="",
                    csv_column=csv_header)
            else:
                csv_row[csv_header] = ""
        writer.writerow(csv_row)

    if 'DETECTION_LIST' in csv_column:
        detection_list = host_list_detection_item[csv_column]['DETECTION']
        if isinstance(detection_list, dict):
            detection_list_for_one = [detection_list]
            detection_list = detection_list_for_one
        for detection in detection_list:
            for csv_detection_column in csv_detection_columns:
                if csv_detection_column in detection.keys():
                    if detection[csv_detection_column] is None:
                        host_list_detection_item[csv_detection_column] = ""
                    elif 'DATE' in csv_detection_column:  # Prepare dates for use in Excel or Database
                        host_list_detection_item[csv_detection_column] = \
                            detection[csv_detection_column].replace("T", " ").replace("Z", "")
                    else:
                        host_list_detection_item[csv_detection_column] = detection[csv_detection_column]
                else:
                    host_list_detection_item[csv_detection_column] = ""
            # Write Host + One Detection
            write_csv_host_list_detection_row()
            count_host_qids_written += 1
            count_csv_records_written += 1
            counter_obj.display_counter_to_log()


def host_list_detection_to_csv():
    global count_host_ids_written
    global count_host_qids_written
    global host_list_detection_csv_truncate_cell_limit
    global host_list_detection_csv_file
    global host_list_detection_item
    global count_csv_records_written
    global counter_obj

    host_list_detection_csv_file = etld_lib_config.host_list_detection_csv_file
    host_list_detection_csv_truncate_cell_limit = int(etld_lib_config.host_list_detection_csv_truncate_cell_limit)

    csv_host_columns = etld_lib_functions.host_list_detection_csv_columns()
    csv_detection_columns = etld_lib_functions.host_list_detection_qid_csv_columns()
    count_host_ids_written = 0
    count_host_qids_written = 0
    count_csv_records_written = 0
    counter_obj = \
        etld_lib_functions.DisplayCounterToLog(display_counter_at=10000,
                                               logger_func=etld_lib_functions.logger.info,
                                               display_counter_log_message=
                                               "count host list detection records written to csv")

    csv_headers = {}
    for header in csv_host_columns:
        csv_headers[header] = ""
    for header in csv_detection_columns:
        csv_headers[header] = ""
    csv_headers.__delitem__('DETECTION_LIST')
    csv_headers_list = csv_headers.keys()

    try:
        with open(host_list_detection_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_headers_list, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            with shelve.open(str(etld_lib_config.host_list_detection_shelve_file), flag='r') as shelve_database:
                for shelve_database_item in shelve_database:
                    host_list_detection_item = shelve_database[shelve_database_item]
                    count_host_ids_written += 1
                    for csv_column in csv_host_columns:
                        if csv_column in host_list_detection_item.keys():
                            prepare_host_info(csv_column, etld_lib_config.host_list_detection_present_csv_cell_as_json)
                            write_csv_detections_for_one_host(csv_column, csv_headers,
                                                              writer, csv_detection_columns)
    except Exception as e:
        etld_lib_functions.logger.error(f"Error writing to file: {str(host_list_detection_csv_file)}, "
                              f"please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def start_msg_host_list_detection_csv():
    etld_lib_functions.logger.info(f"start")


def end_msg_host_list_detection_csv():
    global count_host_ids_written
    global count_host_qids_written
    global counter_obj
    etld_lib_functions.logger.info(f"count host written to csv: {count_host_ids_written:,}")
    counter_obj.display_final_counter_to_log()
    etld_lib_functions.log_file_info(etld_lib_config.host_list_detection_shelve_file, 'in')
    etld_lib_functions.log_dbm_info(etld_lib_config.host_list_detection_shelve_file)
    etld_lib_functions.log_file_info(etld_lib_config.host_list_detection_csv_file)
    etld_lib_functions.logger.info(f"end")


def host_list_detection_csv():
    global counter_obj
    host_list_detection_to_csv()


def main():
    start_msg_host_list_detection_csv()
    host_list_detection_csv()
    end_msg_host_list_detection_csv()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_csv')
    etld_lib_config.main()
    main()
