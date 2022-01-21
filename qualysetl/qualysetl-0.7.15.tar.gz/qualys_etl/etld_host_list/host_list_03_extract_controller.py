#!/usr/bin/env python3
import time
import gzip
from pathlib import Path
import re
import xmltodict
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_extract_transform_load
from qualys_etl.etld_host_list import host_list_04_extract_from_qualys
from qualys_etl.etld_host_list import host_list_05_transform_load_xml_to_sqlite


global host_list_records
global host_list_records_count
global host_list_get_scope_of_host_ids_sql
global host_list_vm_processed_after
global host_list_multi_proc_batch_size
global host_list_concurrency_limit
global host_list_limit_hosts
global spawned_process_info_list
global already_reported_spawned_process_info_status
global xml_file_utc_run_datetime
global counter_obj_dict


def create_counter_objects(message: str) -> dict:
    counter_obj_host_list = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"{message} ")

    counter_obj_dict_new = {'counter_obj_host_list': counter_obj_host_list}

    return counter_obj_dict_new


def start_msg_get_host_list_data():
    etld_lib_functions.logger.info(f"start")


def end_msg_get_host_list_data():
    etld_lib_functions.logger.info(f"host_list get_scope_of_host_ids sql: {host_list_get_scope_of_host_ids_sql}")
    etld_lib_functions.logger.info(f"host_list sqlite file: {etld_lib_config.host_list_sqlite_file}")
    etld_lib_functions.logger.info(f"count host_list host id: {len(host_list_records):,}")
    etld_lib_functions.logger.info(f"end")


def get_next_batch_from_xml_file(xml_file=None, batch_number_str=None) -> dict:

    def get_next_url_from_xml(element_names: tuple, document_item: dict):
        global counter_obj_dict

        def element_type(element_name, element_tuple_list):
            element_found = False
            for element_tuple in element_tuple_list:
                if element_name == element_tuple[0]:
                    element_found = True
                    break
            return element_found

        if element_type('HOST_LIST', element_names):
            counter_obj_dict['counter_obj_host_list'].display_counter_to_log()
        elif element_type('WARNING', element_names):
            last_element_index = (element_names.__len__() - 1)
            element_name_idx = element_names[last_element_index][0]
            if isinstance(document_item, str):
                xml_warning_dict['WARNING'][element_name_idx] = document_item.strip()
        elif element_type('GLOSSARY', element_names):
            pass

        return True

    xml_warning_dict = {'WARNING': {}}
    with etld_lib_config.host_list_open_file_compression_method(xml_file, "rt", encoding='utf-8') as xml_file_fd:
        xmltodict.parse(
            xml_file_fd.read(),
            item_depth=4,
            item_callback=get_next_url_from_xml)

    if 'WARNING' in xml_warning_dict and 'URL' in xml_warning_dict['WARNING']:
        has_more_records = '1'
        id_min = re.sub("(^.*id_min=)([0-9]+)", "\g<2>", xml_warning_dict['WARNING']['URL'])
    else:
        has_more_records = '0'
        id_min = ''

    xml_warning_dict['hasMore'] = has_more_records
    xml_warning_dict['id_min'] = id_min
    etld_lib_functions.logger.info(
        f"End {batch_number_str}, hasMore={has_more_records}, id_min={id_min} info: {xml_warning_dict}")
    return xml_warning_dict


def update_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite(host_xml_file, queue_process, queue_of_file_paths):

    if etld_lib_config.host_list_xml_to_sqlite_via_multiprocessing is True:
        if queue_of_file_paths is not None:
            queue_of_file_paths.put(str(host_xml_file))
            batch_dict = \
                etld_lib_extract_transform_load.get_from_qualys_extract_filename_batch_date_and_batch_number_dict(host_xml_file)
            etld_lib_functions.logger.info(f"Sending batch to queue: {int(batch_dict['batch_number']):06d}")
            if queue_process.is_alive():
                pass
            else:
                etld_lib_functions.logger.error(
                    f"Batch Process was killed or database error, please investigate and retry.")
                exit(1)
        else:
            etld_lib_functions.logger.error(
                f"Batch Queue was not setup, please investigate and retry.")
            exit(1)


def stop_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite(queue_process, queue_of_file_paths):
    while True:
        if queue_process.is_alive():
            queue_of_file_paths.put("END")
            queue_process.join(timeout=300)
            time.sleep(1)
            break
        else:
            etld_lib_functions.logger.error(
                f"Could not send END to batch queue of files to send to sqlite. queue_process died. "
                f"please investigate and retry.")
            exit(1)


def check_qualys_connection_rate_limits(batch_number_str, qualys_headers_multiprocessing_dict, batch_info):

    if batch_number_str in qualys_headers_multiprocessing_dict.keys():
        if 'x_ratelimit_remaining' in qualys_headers_multiprocessing_dict[batch_number_str].keys():
            x_ratelimit_remaining = qualys_headers_multiprocessing_dict[batch_number_str]['x_ratelimit_remaining']
            if int(x_ratelimit_remaining) < 100:
                etld_lib_functions.logger.warning(f"x_ratelimit_remaining is less than 100. "
                                                  f"Sleeping 5 min.  batch_info: {batch_info}, "
                                                  f"header_info: {qualys_headers_multiprocessing_dict[batch_number_str]}")
                time.sleep(300)
        else:
            etld_lib_functions.logger.warning(f"x_ratelimit_remaining missing from Qualys Header. "
                                              f"Sleeping 5 min.  batch_info: {batch_info}, "
                                              f"header_info: {qualys_headers_multiprocessing_dict[batch_number_str]}")
            time.sleep(300)
    qualys_headers_multiprocessing_dict.__delitem__(batch_number_str)


def extract_host_list_data_from_qualys(cleanup_old_files=True):
    global counter_obj_dict
    start_msg_get_host_list_data()
    counter_obj_dict = create_counter_objects("hosts added to host_list_extract_dir")
    cred_dict = etld_lib_credentials.get_cred(cred_dict={})
    utc_datetime = etld_lib_datetime.get_utc_datetime_qualys_format()
    batch_number = 0
    batch_date = utc_datetime
    id_min = 0
    has_more_records = '1'
    qualys_headers_multiprocessing_dict = {}

    if cleanup_old_files is True:
        etld_lib_config.remove_old_files(
            dir_path=etld_lib_config.host_list_extract_dir,
            dir_search_glob=etld_lib_config.host_list_extract_dir_file_search_blob,
            other_files_list=etld_lib_config.host_list_data_files)

    if etld_lib_config.host_list_xml_to_sqlite_via_multiprocessing is True:
        queue_process, queue_of_file_paths = host_list_05_transform_load_xml_to_sqlite.\
            spawn_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite()
    else:
        queue_process = None
        queue_of_file_paths = None

    while has_more_records == '1':
        # create next batch filename
        batch_number += 1
        batch_number_str = f'batch_{batch_number:06d}'
        file_info_dict = \
            etld_lib_config.prepare_extract_batch_file_name(
                next_batch_number_str=batch_number_str,
                next_batch_date=batch_date,
                extract_dir=etld_lib_config.host_list_extract_dir,
                file_name_type="host_list",
                file_name_option="vm_processed_after",
                file_name_option_date=etld_lib_config.host_list_vm_processed_after,
                compression_method=etld_lib_config.host_list_open_file_compression_method
            )

        etld_lib_functions.logger.info(f"Begin {batch_number_str}")
        host_list_04_extract_from_qualys.host_list_extract_batch(
            host_xml_file=file_info_dict['next_file_path'],
            id_min=id_min, batch_number=batch_number_str,
            cred_dict=cred_dict,
            qualys_headers_multiprocessing_dict=qualys_headers_multiprocessing_dict)

        if etld_lib_config.host_list_xml_to_sqlite_via_multiprocessing is True:
            update_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite(
                file_info_dict['next_file_path'], queue_process, queue_of_file_paths)

        etld_lib_extract_transform_load.transform_xml_file_to_json_file(
            xml_file=Path(file_info_dict['next_file_path']),
            compression_method=etld_lib_config.host_list_open_file_compression_method,
            logger_method=etld_lib_functions.logger.info)
        batch_info = get_next_batch_from_xml_file(xml_file=file_info_dict['next_file_path'],
                                                  batch_number_str=batch_number_str)
        has_more_records = str(batch_info['hasMore'])
        id_min = str(batch_info['id_min'])

        has_more_records, id_min = \
            test_system_option(
                file_path=file_info_dict['next_file_path'],
                has_more_records=has_more_records,
                id_min=id_min,
                test_system_flag=etld_lib_config.host_list_test_system_flag,
                number_of_files_to_extract=etld_lib_config.host_list_test_number_of_files_to_extract
                )

        check_qualys_connection_rate_limits(batch_number_str, qualys_headers_multiprocessing_dict, batch_info)

    counter_obj_dict['counter_obj_host_list'].display_final_counter_to_log()
    if etld_lib_config.host_list_xml_to_sqlite_via_multiprocessing is True:
        stop_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite(
            queue_process, queue_of_file_paths)
    else:
        host_list_05_transform_load_xml_to_sqlite.host_list_transform_and_load_all_xml_files_into_sqlite(
            multiprocessing_flag=False)


def test_system_option(file_path: Path, has_more_records, id_min, number_of_files_to_extract, test_system_flag):
    if test_system_flag is True:
        test_batch_number = \
            etld_lib_extract_transform_load.get_batch_number_from_filename(file_path)
        if int(test_batch_number) >= number_of_files_to_extract:
            has_more_records = '0'
            id_min = ''
    return has_more_records, id_min


def main():
    extract_host_list_data_from_qualys()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_03_extract_controller')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
