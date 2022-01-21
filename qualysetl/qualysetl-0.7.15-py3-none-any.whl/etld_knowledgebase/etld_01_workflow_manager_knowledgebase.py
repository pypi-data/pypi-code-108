#!/usr/bin/env python3
import sys
import timeit
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials as etld_lib_credentials

import qualys_etl.etld_knowledgebase.knowledgebase_process_00_extract as kb_extract
import qualys_etl.etld_knowledgebase.knowledgebase_process_01_transform_to_shelve as kb_transform_to_shelve
import qualys_etl.etld_knowledgebase.knowledgebase_process_02_load_json as kb_load_json
import qualys_etl.etld_knowledgebase.knowledgebase_process_03_load_csv as kb_load_csv
import qualys_etl.etld_knowledgebase.knowledgebase_process_03_load_cve_qid_csv as kb_load_cve_qid_csv
import qualys_etl.etld_knowledgebase.knowledgebase_process_04_load_sqlite as kb_load_sqlite
import qualys_etl.etld_knowledgebase.knowledgebase_process_05_distribution as kb_distribution

global start_time
global stop_time


def kb_extract_wrapper():
    etld_lib_functions.logger.info(f"start knowledgebase extract from qualys with "
                         f"kb_last_modified_after={etld_lib_config.kb_last_modified_after}")
    kb_extract.main()
    etld_lib_functions.logger.info(f"end knowledgebase extract from qualys")


def kb_transform_to_shelve_wrapper():
    etld_lib_functions.logger.info(f"start kb_transform_to_shelve")
    kb_transform_to_shelve.main()
    etld_lib_functions.logger.info(f"end   kb_transform_to_shelve")


def kb_load_json_wrapper():
    etld_lib_functions.logger.info(f"start kb_load_json")
    kb_load_json.main()
    etld_lib_functions.logger.info(f"end   kb_load_json")


def kb_load_csv_wrapper():
    etld_lib_functions.logger.info(f"start kb_load_csv")
    kb_load_csv.main()
    etld_lib_functions.logger.info(f"end   kb_load_csv")


def kb_load_cve_qid_csv_wrapper():
    etld_lib_functions.logger.info(f"start kb_load_cve_qid_csv")
    kb_load_cve_qid_csv.main()
    etld_lib_functions.logger.info(f"end   kb_load_cve_qid_csv")


def kb_load_sqlite_wrapper():
    etld_lib_functions.logger.info(f"start kb_load_sqlite")
    kb_load_sqlite.main()
    etld_lib_functions.logger.info(f"end   kb_load_sqlite")


def kb_distribution_wrapper():
    try:
        does_dir_exist = etld_lib_config.kb_export_dir
        try:
            etld_lib_functions.logger.info(f"start kb_distribution")
            kb_distribution.main()
            etld_lib_functions.logger.info(f"end   kb_distribution")
        except Exception as e:
            etld_lib_functions.logger.info(f"kb_distribution ended with an {e}, ignore if distribution is off.")
    except Exception as e:
        # no distribution directory found and that's ok.
        pass


def kb_start_wrapper():
    global start_time
    start_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"__start__ kb_etl_workflow {str(sys.argv)}")
    etld_lib_functions.logger.info(f"data directory: {etld_lib_config.qetl_user_data_dir}")
    etld_lib_functions.logger.info(f"config file:    {etld_lib_config.qetl_user_config_settings_yaml_file}")
    etld_lib_functions.logger.info(f"cred yaml file: {etld_lib_credentials.cred_file}")
    etld_lib_functions.logger.info(f"cookie file:    {etld_lib_credentials.cookie_file}")


def kb_end_wrapper():
    global start_time
    global stop_time

    stop_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"runtime for kb_etl_workflow in seconds: {stop_time - start_time:,}")
    etld_lib_functions.logger.info(f"__end__ kb_etl_workflow {str(sys.argv)}")


def kb_etl_workflow():
    try:
        kb_start_wrapper()
        kb_extract_wrapper()
        kb_transform_to_shelve_wrapper()
        kb_load_json_wrapper()
        kb_load_csv_wrapper()
        kb_load_cve_qid_csv_wrapper()
        kb_load_sqlite_wrapper()
        kb_distribution_wrapper()
        kb_end_wrapper()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error occurred, please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def main():
    kb_etl_workflow()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name="kb_etl_workflow")
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
