#!/usr/bin/env python3
import sys
import timeit
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials as etld_lib_credentials

import qualys_etl.etld_host_list_detection.host_list_detection_process_00_extract_controller \
    as host_list_detection_extract_controller
import qualys_etl.etld_host_list_detection.host_list_detection_process_01_transform_to_shelve as host_list_detection_to_shelve
import qualys_etl.etld_host_list_detection.host_list_detection_process_02_load_json as host_list_detection_json
import qualys_etl.etld_host_list_detection.host_list_detection_process_03_load_csv as host_list_detection_csv
import qualys_etl.etld_host_list_detection.host_list_detection_process_04_load_sqlite as host_list_detection_sqlite
import qualys_etl.etld_host_list_detection.host_list_detection_process_05_distribution as host_list_detection_distribution
import qualys_etl.etld_host_list.etld_01_workload_manager_host_list as etl_host_list
import qualys_etl.etld_knowledgebase.etld_01_workflow_manager_knowledgebase as etl_knowledgebase
from qualys_etl.etld_lib.etld_lib_sqlite_tables import get_q_knowledgebase_min_max_dates

global start_time
global stop_time


def update_host_list_for_input_to_host_list_detection_wrapper():
    etld_lib_functions.logger.info(f"start update host list from Qualys")

    etl_host_list.main()
    etld_lib_functions.logger.info(f"     using host_list_vm_processed_after="
                                   f"{etld_lib_config.host_list_vm_processed_after} "
                                   f"in host_list_detection_vm_processed_after")
    etld_lib_config.host_list_detection_vm_processed_after = etld_lib_config.host_list_vm_processed_after
    etld_lib_functions.logger.info(f"end   update host list from Qualys")


def update_knowledgebase_for_input_to_host_list_detection_sqlite_wrapper():
    etld_lib_functions.logger.info(f"start update knowledgebase from Qualys")
    etl_knowledgebase.main()
    etl_knowledgebase.kb_sqlite_file = etld_lib_config.host_list_detection_sqlite_file
    etl_knowledgebase.kb_load_sqlite.main()
    etld_lib_functions.logger.info(f"end   update knowledgebase from Qualys")


def host_list_detection_extract_wrapper():
    etld_lib_functions.logger.info(f"start host_list_detection_extract from Qualys")
    etld_lib_functions.logger.info(f"     vm_processed_after={etld_lib_config.host_list_detection_vm_processed_after}")
    host_list_detection_extract_controller.main()
    etld_lib_functions.logger.info(f"end   host_list_detection_extract from Qualys")


def host_list_detection_to_shelve_wrapper():

    etld_lib_functions.logger.info(f"start host_list_detection_shelve xml to shelve")
    host_list_detection_to_shelve.main()
    etld_lib_functions.logger.info(f"end   host_list_detection_shelve xml to shelve")


def host_list_detection_to_json_wrapper():
    etld_lib_functions.logger.info(f"start host_list_detection_json transform Shelve to JSON")
    host_list_detection_json.main()
    etld_lib_functions.logger.info(f"end   host_list_detection_json transform Shelve to JSON")


def host_list_detection_to_csv_wrapper():
    etld_lib_functions.logger.info(f"start host_list_detection_csv - shelve to csv")
    host_list_detection_csv.main()
    etld_lib_functions.logger.info(f"end   host_list_detection_csv - shelve to csv")


def host_list_detection_to_sqlite_wrapper():
    etld_lib_functions.logger.info(f"start host_list_detection_sqlite transform Shelve to Sqlite3 DB")
    host_list_detection_sqlite.main()
    etld_lib_functions.logger.info(f"end   host_list_detection_sqlite transform Shelve to Sqlite3 DB")


def host_list_detection_distribution_wrapper():
    try:
        does_dir_exist = etld_lib_config.host_list_detection_export_dir
        try:
            etld_lib_functions.logger.info(f"start host_list_detection_distribution")
            host_list_detection_distribution.main()
            etld_lib_functions.logger.info(f"end   host_list_detection_distribution")
        except Exception as e:
            etld_lib_functions.logger.info(f"host_list_detection_distribution ended with an {e}, ignore if distribution is off.")
    except Exception as e:
        # no distribution directory found and that's ok.
        pass


def host_list_detection_start_wrapper():
    global start_time
    start_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"__start__ host_list_detection_etl_workflow {str(sys.argv)}")
    etld_lib_functions.logger.info(f"data directory: {etld_lib_config.qetl_user_data_dir}")
    etld_lib_functions.logger.info(f"config file:    {etld_lib_config.qetl_user_config_settings_yaml_file}")
    etld_lib_functions.logger.info(f"cred yaml file: {etld_lib_credentials.cred_file}")
    etld_lib_functions.logger.info(f"cookie file:    {etld_lib_credentials.cookie_file}")


def host_list_detection_end_wrapper():
    global start_time
    global stop_time

    stop_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"runtime for host_list_detection_etl_workflow in seconds: {stop_time - start_time:,}")
    etld_lib_functions.logger.info(f"__end__ host_list_detection_etl_workflow {str(sys.argv)}")


def host_list_detection_etl_workflow():
    try:
        host_list_detection_start_wrapper()
        update_host_list_for_input_to_host_list_detection_wrapper()
        host_list_detection_extract_wrapper()
        host_list_detection_to_shelve_wrapper()
        host_list_detection_to_json_wrapper()
        host_list_detection_to_csv_wrapper()
        update_knowledgebase_for_input_to_host_list_detection_sqlite_wrapper()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error occurred in initial steps, please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)

    try:
        host_list_detection_to_sqlite_wrapper()
        host_list_detection_distribution_wrapper()
        host_list_detection_end_wrapper()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error occurred final step, please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def main():
    host_list_detection_etl_workflow()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_etl_workflow')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
