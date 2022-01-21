import re
import sqlite3
import time
import multiprocessing
from pathlib import Path
import os
import oschmod
import shutil
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables as etld_lib_sqlite_tables
from qualys_etl.etld_lib import etld_lib_datetime as api_datetime
import qualys_etl.etld_host_list_detection.host_list_detection_process_00_extract as host_list_detection_extract

global host_list_records
global host_list_records_count
global host_list_get_scope_of_host_ids_sql
global host_list_detection_vm_processed_after
global host_list_detection_multi_proc_batch_size
global host_list_detection_concurrency_limit
global host_list_detection_batch_queue
global host_list_detection_limit_hosts
global spawned_process_info_list
global already_reported_spawned_process_info_status
global qualys_headers_multi_proc_dict
global xml_file_utc_run_datetime


# Create queue of batches to process.
# Each batch will be up to host_list_detection_multi_proc_batch_size.

def remove_old_files():
    if Path(etld_lib_config.host_list_detection_xml_dir).name in 'host_list_detection_xml_dir':
        os.makedirs(etld_lib_config.host_list_detection_xml_dir, exist_ok=True)
        oschmod.set_mode(etld_lib_config.host_list_detection_xml_dir, "a+rwx,g-rwx,o-rwx")
    # Remove old xml files if they exist in host_list_detection_xml_dir
    if Path(etld_lib_config.host_list_detection_xml_dir).is_dir():
        if Path(etld_lib_config.host_list_detection_xml_dir).name in 'host_list_detection_xml_dir':
            count_files = 0
            for f in Path(etld_lib_config.host_list_detection_xml_dir).glob('host_list_detection*.xml'):
                count_files = count_files + 1
            etld_lib_functions.logger.info(f"Removing {count_files} old xml files from dir: "
                                           f"{etld_lib_config.host_list_detection_xml_dir}")

            files = Path(etld_lib_config.host_list_detection_xml_dir).glob('host_list_detection*.xml')
            try:
                for file in files:
                    file.unlink()
            except OSError as e:
                etld_lib_functions.logger.error(f"{e}")
                exit(1)
    try:
        if Path(etld_lib_config.host_list_detection_sqlite_file).is_file():
            etld_lib_functions.logger.info(f"Removing old sqlite file: {etld_lib_config.host_list_detection_sqlite_file}")
            Path(etld_lib_config.host_list_detection_sqlite_file).unlink()
        if Path(etld_lib_config.host_list_detection_shelve_file).is_file():
            etld_lib_functions.logger.info(f"Removing old shelve file: {etld_lib_config.host_list_detection_shelve_file}")
            Path(etld_lib_config.host_list_detection_shelve_file).unlink()
        if Path(etld_lib_config.host_list_detection_json_file).is_file():
            etld_lib_functions.logger.info(f"Removing old json file: {etld_lib_config.host_list_detection_json_file}")
            Path(etld_lib_config.host_list_detection_json_file).unlink()
        if Path(etld_lib_config.host_list_detection_csv_file).is_file():
            etld_lib_functions.logger.info(f"Removing old csv file: {etld_lib_config.host_list_detection_csv_file}")
            Path(etld_lib_config.host_list_detection_csv_file).unlink()
    except Exception as e:
        etld_lib_functions.logger.error(f"{e}")
        exit(1)


def extract_host_list_detection(host_ids, batch_number, xml_file_utc_run_datetime_arg):
    host_list_detection_extract.multi_proc_host_ids = host_ids
    host_list_detection_extract.qualys_headers_multi_proc_dict = qualys_headers_multi_proc_dict
    host_list_detection_extract.multi_proc_batch_number = batch_number
    host_list_detection_extract.xml_file_utc_run_datetime = xml_file_utc_run_datetime_arg
    etld_lib_functions.logger.info(f"begin batch: {host_list_detection_extract.multi_proc_batch_number}")
    host_list_detection_extract.main()
    time.sleep(1)
    etld_lib_functions.logger.info(f"end batch: {host_list_detection_extract.multi_proc_batch_number}")


def get_host_list_detection_data(manager=None):
    global host_list_detection_batch_queue
    global spawned_process_info_list
    global already_reported_spawned_process_info_status
    global qualys_headers_multi_proc_dict
    global xml_file_utc_run_datetime

    qualys_headers_multi_proc_dict = manager.dict()
    already_reported_spawned_process_info_status = []
    spawned_process_info_list = []
    hostid_batch_queue_size = host_list_detection_batch_queue.qsize()

    etld_lib_functions.logger.info(f"host_list_detection host_ids per batch: "
                                   f"{etld_lib_config.host_list_detection_multi_proc_batch_size}")
    etld_lib_functions.logger.info(f"host_list_detection_batch_queue.qsize:  {hostid_batch_queue_size}")
    etld_lib_functions.logger.info(f"user selected concurrency_limit:        "
                                   f"{etld_lib_config.host_list_detection_concurrency_limit}")

    xml_file_utc_run_datetime = api_datetime.get_utc_date()

    if_exceeding_concurrency_reset_user_selected_concurrency_limit()

    for batch in range(0, hostid_batch_queue_size, 1):
        batch_data = host_list_detection_batch_queue.get()

        spawned_process_info = \
            multiprocessing.Process(target=extract_host_list_detection,
                                    args=(batch_data['host_ids'],
                                          batch_data['batch_number'],
                                          xml_file_utc_run_datetime),
                                    name=batch_data['batch_number'])
        spawned_process_info_list.append(spawned_process_info)
        test_child_processes_for_concurrency_max()
        spawned_process_info.start()
        test_for_errors_in_extracts(report_status=True)
        test_child_processes_for_concurrency_max()

    cleanup_remaining_processes()


def cleanup_remaining_processes():
    global host_list_detection_batch_queue

    active_children = get_count_of_active_child_processes('batch_')
    etld_lib_functions.logger.info(f"waiting for final active children: {multiprocessing.active_children()}")

    while active_children > 0:
        etld_lib_functions.logger.debug(f"waiting for final active children: {multiprocessing.active_children()}")
        test_for_errors_in_extracts()
        active_children = get_count_of_active_child_processes('batch_')

    for spawned_process_info_final_status in spawned_process_info_list:
        etld_lib_functions.logger.info(f"final job status spawned_process_info_status.exitcode: "
                                       f"{spawned_process_info_final_status}")
    host_list_detection_batch_queue = None


def if_exceeding_concurrency_reset_user_selected_concurrency_limit():
    global qualys_headers_multi_proc_dict
    host_list_detection_extract.qualys_headers_multi_proc_dict = qualys_headers_multi_proc_dict
    host_list_detection_extract.get_qualys_limits_from_host_list_detection()
    user_selected_concurrency_limit = int(etld_lib_config.host_list_detection_concurrency_limit)

    for key in qualys_headers_multi_proc_dict.keys():
        qualys_concurrency_limit = int(qualys_headers_multi_proc_dict[key]['x_concurrency_limit_limit'])
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

        qualys_headers_multi_proc_dict.__delitem__(key)


def get_count_of_active_child_processes(name='batch_'):
    active_children = 0
    for child in multiprocessing.active_children():
        if str(child.__getattribute__('name')).__contains__(name):
            active_children = active_children + 1
    return active_children


def test_child_processes_for_concurrency_max():
    global qualys_headers_multi_proc_dict
    etld_lib_functions.logger.info(f"test_child_processes_for_concurrency_max: {multiprocessing.active_children()}")
    active_children = get_count_of_active_child_processes('batch_')
    concurrency = int(etld_lib_config.host_list_detection_concurrency_limit)

    while active_children >= concurrency:
        etld_lib_functions.logger.debug(f"active_children: {active_children} "
                                        f"limit: {concurrency} "
                                        f"children: {multiprocessing.active_children()}")
        test_for_errors_in_extracts()
        active_children = get_count_of_active_child_processes('batch_')


def terminate_program_due_to_error(terminate_process_info_status=None):
    global spawned_process_info_list
    global host_list_detection_batch_queue
    global already_reported_spawned_process_info_status
    # Error Occurred, Terminate all remaining jobs
    etld_lib_functions.logger.error(f"terminate_process_info_status.exitcode: {str(terminate_process_info_status.exitcode)}")
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
        etld_lib_functions.logger.error(f"final job status spawned_process_info_status.exitcode: {spawned_process_info_final_status}")
    exit(1)


def test_for_errors_in_extracts(report_status=False):
    global spawned_process_info_list
    global host_list_detection_batch_queue
    global already_reported_spawned_process_info_status

    time.sleep(1)
    for spawned_process_info_status in spawned_process_info_list:
        if spawned_process_info_status.exitcode is not None:
            if spawned_process_info_status.exitcode > 0:
                # Error Occurred, Terminate all remaining jobs
                terminate_program_due_to_error(terminate_process_info_status=spawned_process_info_status)
            elif (spawned_process_info_status.exitcode == 0 and report_status is True) and \
                    not already_reported_spawned_process_info_status.__contains__(spawned_process_info_status.pid):
                # Report exit status only one time, keep track of already reported status.
                already_reported_spawned_process_info_status.append(spawned_process_info_status.pid)
                etld_lib_functions.logger.info(f"job completed spawned_process_info_status.exitcode: {spawned_process_info_status}")
            elif spawned_process_info_status.exitcode < 0:
                # Odd error.  Report and quit.
                etld_lib_functions.logger.error(f"odd negative spawned_process_info_status.exitcode: {spawned_process_info_status}")
                etld_lib_functions.logger.error(f"spawned_process_info_status: "
                                                f"{spawned_process_info_list}")
                exit(1)


def prepare_host_id_batches_for_host_list_detection_extract(manager=None):
    global host_list_detection_batch_queue
    global host_list_detection_vm_processed_after

    host_list_detection_batch_queue = manager.Queue()
    batch_number = 1
    batch_size_counter = 0
    batch_size_max = int(etld_lib_config.host_list_detection_multi_proc_batch_size)
    if batch_size_max > 750:
        etld_lib_functions.logger.info(f"reset batch_size_max to 750.")
        etld_lib_functions.logger.info(f" user select batch_size_max was {batch_size_max}.")
        batch_size_max = 750
        etld_lib_config.host_list_detection_multi_proc_batch_size = 750

    host_id_list = []
    for ID, DATETIME in host_list_records:
        if batch_size_counter >= int(batch_size_max):
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
                                       f"{host_list_detection_vm_processed_after}")
        etld_lib_functions.logger.info(f"Please select another date and rerun.  No errors, exiting with status of zero.")
        exit(0)


def get_scope_of_host_ids_from_host_list():
    global host_list_records
    global host_list_records_count
    global host_list_get_scope_of_host_ids_sql
    global host_list_detection_vm_processed_after
    global host_list_detection_limit_hosts

    host_list_detection_limit_hosts = etld_lib_config.host_list_detection_limit_hosts
    if api_datetime.is_valid_qualys_datetime_format(etld_lib_config.host_list_detection_vm_processed_after):
        vm_processed_after = etld_lib_config.host_list_detection_vm_processed_after
        vm_processed_after = re.sub("T", " ", vm_processed_after)
        vm_processed_after = re.sub("Z", "", vm_processed_after)
        host_list_detection_vm_processed_after = vm_processed_after
    else:
        etld_lib_functions.logger.error(f"error vm_processed_after: {etld_lib_config.host_list_detection_vm_processed_after} ")
        exit(1)
    #
    #  f"WHERE LAST_VM_SCANNED_DATE > datetime('{vm_processed_after}') "
    #  Qualys has internal algorithm for vm_processed_after.  Trust host list to pull all vm_processed after
    #  and select all assets where LAST_VM_SCANNED_DATE is not "" or NULL.
    #
    sql_statement = f"SELECT t.ID, t.LAST_VM_SCANNED_DATE FROM Q_Host_List t " \
                    f'WHERE LAST_VM_SCANNED_DATE is not "" or NULL ' \
                    f"ORDER BY LAST_VULN_SCAN_DATETIME DESC limit {host_list_detection_limit_hosts}"

    host_list_get_scope_of_host_ids_sql = sql_statement

    try:
        conn = sqlite3.connect(etld_lib_config.host_list_sqlite_file, timeout=20)
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
    finally:
        if conn:
            conn.close()


def start_msg_get_host_list_detection_data():
    etld_lib_functions.logger.info(f"start")


def end_msg_get_host_list_detection_data():
    etld_lib_functions.logger.info(f"host_list get_scope_of_host_ids sql: {host_list_get_scope_of_host_ids_sql}")
    etld_lib_functions.logger.info(f"host_list sqlite file: {etld_lib_config.host_list_sqlite_file}")
    etld_lib_functions.logger.info(f"count host_list host id: {len(host_list_records):,}")
    etld_lib_functions.logger.info(f"end")


def main():
    start_msg_get_host_list_detection_data()
    get_scope_of_host_ids_from_host_list()
    remove_old_files()
    with multiprocessing.Manager() as manager:
        prepare_host_id_batches_for_host_list_detection_extract(manager=manager)
        get_host_list_detection_data(manager=manager)
    end_msg_get_host_list_detection_data()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_extract_controller')
    etld_lib_config.main()
    main()

