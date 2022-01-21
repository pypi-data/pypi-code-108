#!/usr/bin/env python3
import sys
import timeit
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials

from qualys_etl.etld_was import was_03_extract_controller
from qualys_etl.etld_was import was_05_transform_load_json_to_sqlite
from qualys_etl.etld_was import was_06_distribution

global start_time
global stop_time


def was_03_extract_controller_wrapper(
        module_function=was_03_extract_controller, message=""
):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def was_05_transform_load_json_to_sqlite_wrapper(
        module_function=was_05_transform_load_json_to_sqlite, message=""
):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def prepare_was_06_distribution():
    module_function = prepare_was_06_distribution
    try:
        export_dir = etld_lib_config.was_export_dir
        if Path(export_dir).is_dir():
            return True
        else:
            etld_lib_functions.logger.info(
                f"No distribution as directory does not exist: {export_dir}")
            return False
    except Exception as e:
        etld_lib_functions.logger.info(f"Export test for {module_function} ended with an {e}, "
                                       f"ignore if distribution is off.")


def was_06_distribution_wrapper(
        module_function=was_06_distribution, message=""):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def was_start_wrapper():
    global start_time
    start_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"__start__ was_etl_workflow {str(sys.argv)}")
    etld_lib_functions.logger.info(f"data directory: {etld_lib_config.qetl_user_data_dir}")
    etld_lib_functions.logger.info(f"config file:    {etld_lib_config.qetl_user_config_settings_yaml_file}")
    etld_lib_functions.logger.info(f"cred yaml file: {etld_lib_credentials.cred_file}")
    etld_lib_functions.logger.info(f"bearer file:    {etld_lib_credentials.bearer_file}")


def was_end_wrapper():
    global start_time
    global stop_time

    stop_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"runtime for was_etl_workflow in seconds: {stop_time - start_time:,}")
    etld_lib_functions.logger.info(f"__end__ was_etl_workflow {str(sys.argv)}")


def was_etl_workflow():
    try:
        was_start_wrapper()
        was_03_extract_controller_wrapper(message=f"last_scan_date={etld_lib_config.was_webapp_last_scan_date}")
        #was_05_transform_load_json_to_sqlite_wrapper()
        #if prepare_was_06_distribution():
        #    was_06_distribution_wrapper()
        was_end_wrapper()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error occurred, please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def main():
    was_etl_workflow()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='was_etl_workflow')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
