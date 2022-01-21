#!/usr/bin/env python3
import xmltodict
import time
import json
import re
from multiprocessing import Process, Queue
from pathlib import Path

from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables
from qualys_etl.etld_lib import etld_lib_extract_transform_load


def create_counter_objects(database_type='sqlite'):
    counter_obj_host_list = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.host_list_table_name}")

    counter_obj_host_list_duplicates = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"duplicate rows not added to {database_type} "
                                    f"table {etld_lib_config.host_list_table_name}")

    counter_obj_dict_new = {'counter_obj_host_list': counter_obj_host_list,
                            'counter_obj_host_list_duplicates': counter_obj_host_list_duplicates}

    return counter_obj_dict_new


def drop_and_create_all_tables(sqlite_obj):
    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_table_name,
        csv_columns=etld_lib_config.host_list_csv_columns(),
        csv_column_types=etld_lib_config.host_list_csv_column_types(),
        key='ID')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_status_table_name,
        csv_columns=etld_lib_config.status_table_csv_columns(),
        csv_column_types=etld_lib_config.status_table_csv_column_types(),
        key='STATUS_NAME')


def insert_one_row_into_table_q_host_list(
        item_dict: dict,
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        table_name: str,
        counter_obj_dict: dict
):

    def prepare_field(field_data, field_name_tmp):
        if field_data is None:
            field_data = ""
        elif 'DATE' in field_name_tmp:
            field_data = field_data.replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif isinstance(field_data, int):
            field_data = str(field_data)
        elif not isinstance(field_data, str):
            field_data = json.dumps(field_data)

        return field_data

    row_in_sqlite_form = []
    for field_name in etld_lib_config.host_list_csv_columns():  # Iterate through expected columns (contract)
        if field_name in item_dict.keys():  # Iterate through columns found in dictionary
            item_dict[field_name] = \
                prepare_field(item_dict[field_name], field_name)
            row_in_sqlite_form.append(item_dict[field_name])
        else:
            row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field

    result = sqlite_obj.insert_unique_row_ignore_duplicates(table_name, row_in_sqlite_form)

    if result is True:
        counter_obj_dict['counter_obj_host_list'].display_counter_to_log()
    else:
        counter_obj_dict['counter_obj_host_list_duplicates'].display_counter_to_log()


def insert_xml_file_into_sqlite(xml_file: Path, sqlite_obj: etld_lib_sqlite_tables.SqliteObj, counter_obj: dict):

    def callback_to_insert_host_into_sqlite(element_names: tuple, document_item: dict):
        if len(element_names) > 2 and "HOST" != element_names[3][0]:
            return True
        document_item['BATCH_DATE'] = batch_date
        document_item['BATCH_NUMBER'] = int(batch_number)
        insert_one_row_into_table_q_host_list(
            document_item, sqlite_obj, etld_lib_config.host_list_table_name, counter_obj)
        return True

    with etld_lib_config.host_list_open_file_compression_method(str(xml_file), "rt", encoding='utf-8') as xml_file_fd:
        batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(xml_file)
        batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(xml_file)
        status_name, status_detail_dict, status_count = \
            sqlite_obj.update_status_table(
                batch_date=batch_date, batch_number=batch_number,
                total_rows_added_to_database=counter_obj['counter_obj_host_list'].get_counter(),
                status_table_name=etld_lib_config.host_list_status_table_name,
                status_table_columns=etld_lib_config.status_table_csv_columns(),
                status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                status_name_column='HOST_LIST_LOAD_STATUS', status_column='begin')

        xmltodict.parse(xml_file_fd.read(), item_depth=4,
                        item_callback=callback_to_insert_host_into_sqlite)
        sqlite_obj.commit_changes()

        status_name, status_detail_dict, status_count = \
            sqlite_obj.update_status_table(
                batch_date=batch_date, batch_number=batch_number,
                total_rows_added_to_database=counter_obj['counter_obj_host_list'].get_counter(),
                status_table_name=etld_lib_config.host_list_status_table_name,
                status_table_columns=etld_lib_config.status_table_csv_columns(),
                status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                status_name_column='HOST_LIST_LOAD_STATUS', status_column='end')


def spawn_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite():
    queue_of_file_paths = Queue()
    queue_process = \
        Process(target=host_list_transform_and_load_all_xml_files_into_sqlite,
                args=(queue_of_file_paths, True))
    queue_process.daemon = True
    queue_process.start()

    queue_of_file_paths.put("BEGIN")
    etld_lib_functions.logger.info(f"Queue of files process id: " f"{queue_process.pid} ")

    return queue_process, queue_of_file_paths


def load_files_into_sqlite_via_multiprocessing_queue(
        queue_of_file_paths, sqlite_obj: etld_lib_sqlite_tables.SqliteObj, counter_obj):

    def get_next_file_in_queue(bookend, queue_file_path):
        time.sleep(2)
        queue_data = queue_file_path.get()
        if queue_data == bookend:
            etld_lib_functions.logger.info(f"Found {bookend} of multiprocessing Queue.")
            queue_data = bookend
        return queue_data

    file_path = get_next_file_in_queue('BEGIN', queue_of_file_paths)
    batch_date = ""
    batch_number = ""
    if file_path == 'BEGIN':
        while True:
            file_path = get_next_file_in_queue('END', queue_of_file_paths)
            if file_path == 'END':
                status_name, status_detail_dict, status_count = \
                    sqlite_obj.update_status_table(
                        batch_date=batch_date, batch_number=batch_number,
                        total_rows_added_to_database=counter_obj['counter_obj_host_list'].get_counter(),
                        status_table_name=etld_lib_config.host_list_status_table_name,
                        status_table_columns=etld_lib_config.status_table_csv_columns(),
                        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                        status_name_column='HOST_LIST_LOAD_STATUS', status_column='final')
                break
            batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(file_path)
            batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(file_path)
            etld_lib_functions.logger.info(f"Received batch file in Queue: {batch_number}")
            insert_xml_file_into_sqlite(xml_file=file_path, sqlite_obj=sqlite_obj, counter_obj=counter_obj)
            etld_lib_functions.logger.info(f"Committed batch file in Queue to Database: {batch_number}")
    else:
        etld_lib_functions.logger.error(f"Invalid begin of Queue, {file_path}.  Please restart.")
        exit(1)


def load_files_into_sqlite_via_directory_listing(sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
                                                 counter_obj,
                                                 insert_xml_file_into_sqlite_method=None):
    xml_file_list = []
    for file_name in sorted(Path(etld_lib_config.host_list_extract_dir).glob(
            etld_lib_config.host_list_extract_dir_file_search_blob)):
        if str(file_name).endswith('.xml') or str(file_name).endswith('.xml.gz'):
            xml_file_list.append(file_name)
    for file_path in xml_file_list:
        insert_xml_file_into_sqlite_method(xml_file=file_path, sqlite_obj=sqlite_obj, counter_obj=counter_obj)
        etld_lib_functions.log_file_info(file_path)


def host_list_transform_and_load_all_xml_files_into_sqlite(queue_of_file_paths=None, multiprocessing_flag=False):

    start_msg_host_list_to_sqlite()
    xml_file_path = ""
    counter_obj_dict = create_counter_objects()

    try:
        host_list_sqlite_obj = etld_lib_sqlite_tables.SqliteObj(
            sqlite_file=etld_lib_config.host_list_sqlite_file)
        drop_and_create_all_tables(
            sqlite_obj=host_list_sqlite_obj)
        #
        if multiprocessing_flag is True:
            load_files_into_sqlite_via_multiprocessing_queue(
                queue_of_file_paths=queue_of_file_paths,
                sqlite_obj=host_list_sqlite_obj,
                counter_obj=counter_obj_dict)
        else:
            load_files_into_sqlite_via_directory_listing(
                sqlite_obj=host_list_sqlite_obj,
                insert_xml_file_into_sqlite_method=insert_xml_file_into_sqlite,
                counter_obj=counter_obj_dict)

        host_list_sqlite_obj.commit_changes()
        host_list_sqlite_obj.close_connection()
        counter_obj_dict['counter_obj_host_list'].display_final_counter_to_log()
        end_msg_host_list_to_sqlite()

    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Issue with xml file: {xml_file_path}")
        exit(1)


def end_msg_host_list_to_sqlite():
    xml_file_list = sorted(
        Path(etld_lib_config.host_list_extract_dir).glob(etld_lib_config.host_list_extract_dir_file_search_blob))
    for host_list_xml_file in xml_file_list:
        if str(host_list_xml_file).endswith('.xml') or str(host_list_xml_file).endswith('.xml.gz'):
            etld_lib_functions.log_file_info(host_list_xml_file, 'input file')
    etld_lib_functions.logger.info(f"end")


def start_msg_host_list_to_sqlite():
    etld_lib_functions.logger.info("start")


def main(multiprocessing_flag=False):
    host_list_transform_and_load_all_xml_files_into_sqlite(
        queue_of_file_paths=None,
        multiprocessing_flag=multiprocessing_flag
    )


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_05_transform_load_xml_to_sqlite')
    etld_lib_config.main()
    main(multiprocessing_flag=False)
