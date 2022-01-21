#!/usr/bin/env python3
import sqlite3
import json
import xmltodict
import gzip
import time
import multiprocessing
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_host_list_detection import host_list_detection_04_extract
from qualys_etl.etld_host_list_detection import host_list_detection_05_transform_load_xml_to_sqlite
from qualys_etl.etld_lib import etld_lib_extract_transform_load


def update_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite(file_path,
                                                                             queue_process,
                                                                             queue_of_file_paths):

    if etld_lib_config.host_list_detection_xml_to_sqlite_via_multiprocessing is True:
        if queue_of_file_paths is not None:
            queue_of_file_paths.put(str(file_path))
            batch_dict = \
                etld_lib_extract_transform_load.\
                get_from_qualys_extract_filename_batch_date_and_batch_number_dict(file_path)
            etld_lib_functions.logger.info(f"Sending batch to queue for transform to sqlite: {int(batch_dict['batch_number']):06d}")
            if queue_process.exitcode is None:
                pass
            else:
                etld_lib_functions.logger.error(
                    f"Batch Process was killed or database error, please investigate and retry.")
                exit(1)
        else:
            etld_lib_functions.logger.error(
                f"Batch Queue was not setup, please investigate and retry.")
            exit(1)


def extract_host_list_detection(batch_of_host_ids: str,
                                batch_number_str: str,
                                xml_file_paths_multiprocessing_queue: multiprocessing.Queue,
                                output_xml_file: str,
                                cred_dict: dict,
                                qualys_headers_multiprocessing_dict,
                                queue_of_file_paths_to_load_to_sqlite: multiprocessing.Queue,
                                queue_process_of_load_to_sqlite
                                ):

    etld_lib_functions.logger.info(f"begin batch: {batch_number_str}")

    host_list_detection_04_extract.host_list_detection_extract(
        xml_file=output_xml_file,
        batch_of_host_ids=batch_of_host_ids,
        batch_number_str=batch_number_str,
        qualys_headers_multiprocessing_dict=qualys_headers_multiprocessing_dict,
        cred_dict=cred_dict
    )
    xml_file_paths_multiprocessing_queue.put(output_xml_file)
    etld_lib_extract_transform_load.transform_xml_file_to_json_file(
        xml_file=Path(output_xml_file),
        compression_method=etld_lib_config.host_list_detection_open_file_compression_method,
        logger_method=etld_lib_functions.logger.info
        )
    update_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite(
        file_path=output_xml_file,
        queue_process=queue_process_of_load_to_sqlite,
        queue_of_file_paths=queue_of_file_paths_to_load_to_sqlite
    )
    time.sleep(1)
    etld_lib_functions.logger.info(f"end batch: {batch_number_str}")


def spawn_processes_to_extract_host_list_detection(qualys_headers_multiprocessing_dict=None,
                                                   host_list_detection_batch_queue: multiprocessing.Queue = None,
                                                   already_reported_spawned_process_info_status: list = None,
                                                   spawned_process_info_list: list = None,
                                                   xml_file_utc_run_datetime: str = None,
                                                   cred_dict: dict = None,
                                                   xml_file_paths_multiprocessing_queue: multiprocessing.Queue = None
                                                   ):

    hostid_batch_queue_size = host_list_detection_batch_queue.qsize()
    etld_lib_functions.logger.info(f"host_list_detection host_ids per batch: "
                                   f"{etld_lib_config.host_list_detection_multi_proc_batch_size}")
    etld_lib_functions.logger.info(f"host_list_detection_batch_queue.qsize:  {hostid_batch_queue_size}")
    etld_lib_functions.logger.info(f"user selected concurrency_limit:        "
                                   f"{etld_lib_config.host_list_detection_concurrency_limit}")
    if_exceeding_concurrency_reset_user_selected_concurrency_limit(qualys_headers_multiprocessing_dict,
                                                                   cred_dict)

    if etld_lib_config.host_list_detection_xml_to_sqlite_via_multiprocessing is True:
        queue_process_of_load_to_sqlite, queue_of_file_paths_to_load_to_sqlite = \
            host_list_detection_05_transform_load_xml_to_sqlite.\
            spawn_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite()
    else:
        queue_process_of_load_to_sqlite = None
        queue_of_file_paths_to_load_to_sqlite = None

    # TODO change to begin queue and end queue method for processing host list as each file is loaded to sqlite.

    for batch in range(0, hostid_batch_queue_size, 1):
        batch_data = host_list_detection_batch_queue.get()

        file_info_dict = \
            etld_lib_config.prepare_extract_batch_file_name(
                next_batch_number_str=batch_data['batch_number'],
                next_batch_date=xml_file_utc_run_datetime,
                extract_dir=etld_lib_config.host_list_detection_extract_dir,
                file_name_type="host_list_detection",
                file_name_option="vm_processed_after",
                file_name_option_date=etld_lib_config.host_list_detection_vm_processed_after,
                compression_method=etld_lib_config.host_list_detection_open_file_compression_method
            )

        spawned_process_info = \
            multiprocessing.Process(target=extract_host_list_detection,
                                    args=(batch_data['host_ids'],
                                          file_info_dict['next_batch_number_str'],
                                          xml_file_paths_multiprocessing_queue,
                                          file_info_dict['next_file_path'],
                                          cred_dict,
                                          qualys_headers_multiprocessing_dict,
                                          queue_of_file_paths_to_load_to_sqlite,
                                          queue_process_of_load_to_sqlite),
                                    name=file_info_dict['next_batch_number_str'])
        spawned_process_info_list.append(spawned_process_info)
        test_child_processes_for_concurrency_max(
            host_list_detection_batch_queue=host_list_detection_batch_queue,
            already_reported_spawned_process_info_status=already_reported_spawned_process_info_status,
            spawned_process_info_list=spawned_process_info_list,
            queue_process_of_load_to_sqlite=queue_process_of_load_to_sqlite,
            queue_of_file_paths_to_load_to_sqlite=queue_of_file_paths_to_load_to_sqlite
        )
        spawned_process_info.daemon = True
        spawned_process_info.start()
        test_for_errors_in_extracts(
            report_status=True,
            host_list_detection_batch_queue=host_list_detection_batch_queue,
            spawned_process_info_list=spawned_process_info_list,
            already_reported_spawned_process_info_status=already_reported_spawned_process_info_status,
            queue_process_of_load_to_sqlite=queue_process_of_load_to_sqlite,
            queue_of_file_paths_to_load_to_sqlite=queue_of_file_paths_to_load_to_sqlite)
        test_child_processes_for_concurrency_max(
            host_list_detection_batch_queue=host_list_detection_batch_queue,
            already_reported_spawned_process_info_status=already_reported_spawned_process_info_status,
            spawned_process_info_list=spawned_process_info_list,
            queue_process_of_load_to_sqlite=queue_process_of_load_to_sqlite,
            queue_of_file_paths_to_load_to_sqlite=queue_of_file_paths_to_load_to_sqlite
        )

    cleanup_remaining_processes(
        host_list_detection_batch_queue=host_list_detection_batch_queue,
        already_reported_spawned_process_info_status=already_reported_spawned_process_info_status,
        spawned_process_info_list=spawned_process_info_list,
        queue_process_of_load_to_sqlite=queue_process_of_load_to_sqlite,
        queue_of_file_paths_to_load_to_sqlite=queue_of_file_paths_to_load_to_sqlite
    )

    if etld_lib_config.host_list_detection_xml_to_sqlite_via_multiprocessing is True:
        stop_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite(
            queue_process=queue_process_of_load_to_sqlite, queue_of_file_paths=queue_of_file_paths_to_load_to_sqlite)


def stop_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite(queue_process, queue_of_file_paths):
    if etld_lib_config.host_list_detection_xml_to_sqlite_via_multiprocessing is True:
        while True:
            if queue_process.is_alive():
                queue_of_file_paths.put("END")
                queue_process.join(timeout=600)
                time.sleep(1)
                break
            else:
                etld_lib_functions.logger.error(
                    f"Could not send END to batch queue of files to send to sqlite. queue_process died. "
                    f"please investigate and retry.")
                exit(1)


def cleanup_remaining_processes(host_list_detection_batch_queue: multiprocessing.Queue,
                                spawned_process_info_list: list,
                                already_reported_spawned_process_info_status: list,
                                queue_process_of_load_to_sqlite,
                                queue_of_file_paths_to_load_to_sqlite,
                                ):

    active_children = get_count_of_active_child_processes('batch_')
    etld_lib_functions.logger.info(f"waiting for final active children: {multiprocessing.active_children()}")

    while active_children > 0:
        etld_lib_functions.logger.debug(f"waiting for final active children: {multiprocessing.active_children()}")
        test_for_errors_in_extracts(
            report_status=True,
            host_list_detection_batch_queue=host_list_detection_batch_queue,
            spawned_process_info_list=spawned_process_info_list,
            already_reported_spawned_process_info_status=already_reported_spawned_process_info_status,
            queue_process_of_load_to_sqlite=queue_process_of_load_to_sqlite,
            queue_of_file_paths_to_load_to_sqlite=queue_of_file_paths_to_load_to_sqlite
        )
        active_children = get_count_of_active_child_processes('batch_')

    for spawned_process_info_final_status in spawned_process_info_list:
        etld_lib_functions.logger.info(f"final job status spawned_process_info_status.exitcode: "
                                       f"{spawned_process_info_final_status}")

    while host_list_detection_batch_queue.qsize() > 0:
        empty_queue = host_list_detection_batch_queue.get()


def if_exceeding_concurrency_reset_user_selected_concurrency_limit(
        qualys_headers_multiprocessing_dict, cred_dict
):
    host_list_detection_04_extract.get_qualys_limits_from_host_list_detection(
        qualys_headers_multiprocessing_dict, cred_dict)
    user_selected_concurrency_limit = int(etld_lib_config.host_list_detection_concurrency_limit)

    for key in qualys_headers_multiprocessing_dict.keys():
        qualys_concurrency_limit = int(qualys_headers_multiprocessing_dict[key]['x_concurrency_limit_limit'])
        etld_lib_functions.logger.info(f"Found {key} qualys header concurrency limit: {qualys_concurrency_limit}")

        if user_selected_concurrency_limit >= qualys_concurrency_limit - 1:
            if qualys_concurrency_limit == 1:
                etld_lib_config.host_list_detection_concurrency_limit = 1
                etld_lib_functions.logger.info(f"resetting concurrency limit to: "
                                               f"{etld_lib_config.host_list_detection_concurrency_limit}")
            else:
                etld_lib_config.host_list_detection_concurrency_limit = qualys_concurrency_limit - 1
                etld_lib_functions.logger.info(f"resetting concurrency limit to: "
                                               f"{etld_lib_config.host_list_detection_concurrency_limit}")

        qualys_headers_multiprocessing_dict.__delitem__(key)


def get_count_of_active_child_processes(name='batch_'):
    active_children = 0
    for child in multiprocessing.active_children():
        if str(child.__getattribute__('name')).__contains__(name):
            active_children = active_children + 1
    return active_children


def test_child_processes_for_concurrency_max(
        host_list_detection_batch_queue: multiprocessing.Queue = None,
        spawned_process_info_list: list = None,
        already_reported_spawned_process_info_status: list = None,
        queue_process_of_load_to_sqlite=None,
        queue_of_file_paths_to_load_to_sqlite=None
        ):

    etld_lib_functions.logger.info(
        f"test_child_processes_for_concurrency_max: {multiprocessing.active_children()}")
    active_children = get_count_of_active_child_processes('batch_')
    concurrency = int(etld_lib_config.host_list_detection_concurrency_limit)

    while active_children >= concurrency:
        etld_lib_functions.logger.debug(f"active_children: {active_children} "
                                        f"limit: {concurrency} "
                                        f"children: {multiprocessing.active_children()}")
        test_for_errors_in_extracts(
            host_list_detection_batch_queue=host_list_detection_batch_queue,
            spawned_process_info_list=spawned_process_info_list,
            already_reported_spawned_process_info_status=already_reported_spawned_process_info_status,
            queue_process_of_load_to_sqlite=queue_process_of_load_to_sqlite,
            queue_of_file_paths_to_load_to_sqlite=queue_of_file_paths_to_load_to_sqlite
        )
        active_children = get_count_of_active_child_processes('batch_')
        time.sleep(1)


def terminate_program_due_to_error(terminate_process_info_status: multiprocessing.Process,
                                   host_list_detection_batch_queue: multiprocessing.Queue,
                                   spawned_process_info_list: list,
                                   queue_process_of_load_to_sqlite,
                                   queue_of_file_paths_to_load_to_sqlite
                                   ):

    # Error Occurred, Terminate all remaining jobs
    etld_lib_functions.logger.error(
        f"terminate_process_info_status.exitcode: {str(terminate_process_info_status.exitcode)}")
    etld_lib_functions.logger.error(f"terminate_process_info_status:          {terminate_process_info_status}")
    etld_lib_functions.logger.error("Job exiting with error, please investigate")

    for spawned_process_info_remaining in spawned_process_info_list:
        if spawned_process_info_remaining.exitcode is None or spawned_process_info_remaining.exitcode != 0:
            etld_lib_functions.logger.error(f"Terminating remaining process: {spawned_process_info_remaining}")
            spawned_process_info_remaining.kill()
            spawned_process_info_remaining.join()
            spawned_process_info_remaining.close()
            etld_lib_functions.logger.error(f"Status after 'terminate, join, close': {spawned_process_info_remaining}")
    # Empty Queue
    etld_lib_functions.logger.error(f"cancel remaining batches in queue: {host_list_detection_batch_queue.qsize()}")
    for batch in range(0, host_list_detection_batch_queue.qsize(), 1):
        empty_out_queue = host_list_detection_batch_queue.get()
    etld_lib_functions.logger.error(f"batches remaining in queue: {host_list_detection_batch_queue.qsize()}")
    # ALL JOB STATUS
    for spawned_process_info_final_status in spawned_process_info_list:
        etld_lib_functions.logger.error(
            f"final job status spawned_process_info_status.exitcode: {spawned_process_info_final_status}")
    if etld_lib_config.host_list_detection_xml_to_sqlite_via_multiprocessing is True:
        stop_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite(
            queue_process=queue_process_of_load_to_sqlite,
            queue_of_file_paths=queue_of_file_paths_to_load_to_sqlite)
    exit(1)


def test_for_errors_in_extracts(report_status: bool = False,
                                host_list_detection_batch_queue: multiprocessing.Queue = None,
                                spawned_process_info_list: list = None,
                                already_reported_spawned_process_info_status: list = None,
                                queue_process_of_load_to_sqlite=None,
                                queue_of_file_paths_to_load_to_sqlite=None
                                ):

    time.sleep(1)
    for spawned_process_info_status in spawned_process_info_list:
        spawned_process_info_status: multiprocessing.Process
        if spawned_process_info_status.exitcode is not None:
            if spawned_process_info_status.exitcode > 0:
                # Error Occurred, Terminate all remaining jobs
                terminate_program_due_to_error(
                    terminate_process_info_status=spawned_process_info_status,
                    host_list_detection_batch_queue=host_list_detection_batch_queue,
                    spawned_process_info_list=spawned_process_info_list,
                    queue_process_of_load_to_sqlite=queue_process_of_load_to_sqlite,
                    queue_of_file_paths_to_load_to_sqlite=queue_of_file_paths_to_load_to_sqlite
                )
            elif (spawned_process_info_status.exitcode == 0 and report_status is True) and \
                    not already_reported_spawned_process_info_status.__contains__(spawned_process_info_status.pid):
                # Report exit status only one time, keep track of already reported status.
                already_reported_spawned_process_info_status.append(spawned_process_info_status.pid)
                etld_lib_functions.logger.info(
                    f"job completed spawned_process_info_status.exitcode: {spawned_process_info_status}")
                spawned_process_info_status.join()
            elif spawned_process_info_status.exitcode < 0:
                # Odd error.  Report and quit.
                etld_lib_functions.logger.error(
                    f"odd negative spawned_process_info_status.exitcode: {spawned_process_info_status}")
                etld_lib_functions.logger.error(f"spawned_process_info_status: "
                                                f"{spawned_process_info_list}")
                exit(1)


def prepare_host_id_batches_for_host_list_detection_04_extract(
        host_list_detection_batch_queue: multiprocessing.Queue = None,
        host_list_records=None):

    batch_number = 1
    batch_size_counter = 0
    batch_size_max = 2000

    if int(etld_lib_config.host_list_detection_multi_proc_batch_size) > 2000:
        etld_lib_functions.logger.info(f"reset batch_size_max to 2000.")
        etld_lib_functions.logger.info(f" user select batch_size_max was "
                                       f"{etld_lib_config.host_list_detection_multi_proc_batch_size}.")
        etld_lib_config.host_list_detection_multi_proc_batch_size = 2000

    host_id_list = []
    for ID, DATETIME in host_list_records:
        if batch_size_counter >= batch_size_max:
            # create new batch
            host_list_detection_batch_queue.put({'batch_number': f"batch_{batch_number:06d}", 'host_ids': host_id_list})
            host_id_list = []
            batch_number = batch_number + 1
            batch_size_counter = 0
        host_id_list.append(ID)
        batch_size_counter = batch_size_counter + 1

    if len(host_id_list) > 0:
        host_list_detection_batch_queue.put({'batch_number': f"batch_{batch_number:06d}", 'host_ids': host_id_list})
    else:
        etld_lib_functions.logger.info(f"There were no hosts found with vm_processed_after date of: "
                                       f"{etld_lib_config.host_list_detection_vm_processed_after}")
        etld_lib_functions.logger.info(
            f"Please select another date and rerun.  No errors, exiting with status of zero.")
        exit(0)


def get_next_batch_of_host_ids_from_host_list_sqlite(batch_name: str, host_list_records: list):
    host_list_records_count = 0

    if int(etld_lib_config.host_list_detection_limit_hosts) == 0:
        sql_statement_limit = ""
    else:
        sql_statement_limit = f"limit {str(etld_lib_config.host_list_detection_limit_hosts)}"

    sql_statement = "SELECT t.ID, t.LAST_VM_SCANNED_DATE FROM Q_Host_List t " \
                    'WHERE LAST_VULN_SCAN_DATETIME is not "" or NULL ' \
                    "ORDER BY LAST_VULN_SCAN_DATETIME DESC " \
                    f"{sql_statement_limit}"

    host_list_get_scope_of_host_ids_sql = sql_statement

    try:
        conn = sqlite3.connect(etld_lib_config.host_list_sqlite_file, timeout=300)
        cursor = conn.cursor()
        cursor.execute(sql_statement)
        host_list_records = cursor.fetchall()
        host_list_records_count = len(host_list_records)
        cursor.close()
        conn.close()
    except Exception as e:
        etld_lib_functions.logger.error(f"error sqlite db: {etld_lib_config.host_list_sqlite_file}")
        etld_lib_functions.logger.error(f"exception: {e}")
        exit(1)

    return host_list_records, host_list_records_count, host_list_get_scope_of_host_ids_sql


def get_scope_of_host_ids_from_host_list():
    host_list_records = None
    host_list_records_count = 0
    if int(etld_lib_config.host_list_detection_limit_hosts) == 0:
        sql_statement_limit = ""
    else:
        sql_statement_limit = f"limit {str(etld_lib_config.host_list_detection_limit_hosts)}"

    sql_statement = f"SELECT t.ID, t.LAST_VULN_SCAN_DATETIME FROM Q_Host_List t " \
                    f'WHERE LAST_VULN_SCAN_DATETIME is not "" or NULL ' \
                    f"ORDER BY LAST_VULN_SCAN_DATETIME DESC {sql_statement_limit}"

    host_list_get_scope_of_host_ids_sql = sql_statement

    try:
        conn = sqlite3.connect(etld_lib_config.host_list_sqlite_file, timeout=300)
        cursor = conn.cursor()
        cursor.execute(sql_statement)
        host_list_records = cursor.fetchall()
        host_list_records_count = len(host_list_records)
        cursor.close()
        conn.close()
    except Exception as e:
        etld_lib_functions.logger.error(f"error sqlite db: {etld_lib_config.host_list_sqlite_file}")
        etld_lib_functions.logger.error(f"exception: {e}")
        exit(1)
    return host_list_records, host_list_records_count, host_list_get_scope_of_host_ids_sql


def start_msg_get_host_list_detection_data():
    etld_lib_functions.logger.info(f"start")


def end_msg_get_host_list_detection_data(host_list_records, host_list_get_scope_of_host_ids_sql):
    etld_lib_functions.logger.info(f"host_list get_scope_of_host_ids sql: {host_list_get_scope_of_host_ids_sql}")
    etld_lib_functions.logger.info(f"host_list sqlite file: {etld_lib_config.host_list_sqlite_file}")
    etld_lib_functions.logger.info(f"count host_list where last_vuln_scan_datetime is not blank or null: {len(host_list_records):,}")
    etld_lib_functions.logger.info(f"end")


def extract_host_list_detection_via_multiprocessing_manager():
    start_msg_get_host_list_detection_data()
    etld_lib_config.remove_old_files(
        dir_path=etld_lib_config.host_list_detection_extract_dir,
        dir_search_glob=etld_lib_config.host_list_detection_extract_dir_file_search_blob,
        other_files_list=etld_lib_config.host_list_detection_data_files)

    with multiprocessing.Manager() as manager:

        host_list_detection_batch_queue = manager.Queue()

        host_list_records, host_list_records_count, host_list_get_scope_of_host_ids_sql = \
            get_scope_of_host_ids_from_host_list()

        prepare_host_id_batches_for_host_list_detection_04_extract(
            host_list_detection_batch_queue=host_list_detection_batch_queue,
            host_list_records=host_list_records)

        qualys_headers_multiprocessing_dict = manager.dict()
        already_reported_spawned_process_info_status = []
        spawned_process_info_list = []
        xml_file_utc_run_datetime = etld_lib_datetime.get_utc_datetime_qualys_format()

        xml_file_paths_multiprocessing_queue = manager.Queue()
        cred_dict = etld_lib_credentials.get_cred(cred_dict={})

        spawn_processes_to_extract_host_list_detection(
            host_list_detection_batch_queue=host_list_detection_batch_queue,
            qualys_headers_multiprocessing_dict=qualys_headers_multiprocessing_dict,
            already_reported_spawned_process_info_status=already_reported_spawned_process_info_status,
            spawned_process_info_list=spawned_process_info_list,
            xml_file_utc_run_datetime=xml_file_utc_run_datetime,
            xml_file_paths_multiprocessing_queue=xml_file_paths_multiprocessing_queue,
            cred_dict=cred_dict)

    end_msg_get_host_list_detection_data(host_list_records=host_list_records,
                                         host_list_get_scope_of_host_ids_sql=host_list_get_scope_of_host_ids_sql)


def main():
    extract_host_list_detection_via_multiprocessing_manager()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_extract_03_controller')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
