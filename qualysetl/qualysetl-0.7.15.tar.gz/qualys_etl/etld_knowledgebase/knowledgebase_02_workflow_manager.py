#!/usr/bin/env python3
import sys
import timeit
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials

from qualys_etl.etld_knowledgebase import knowledgebase_03_extract
from qualys_etl.etld_knowledgebase import knowledgebase_05_transform_load_xml_to_sqlite
from qualys_etl.etld_knowledgebase import knowledgebase_06_distribution

global start_time
global stop_time


def knowledgebase_03_extract_wrapper(module_function=knowledgebase_03_extract, message=""):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def knowledgebase_05_transform_load_xml_to_sqlite_wrapper(
        module_function=knowledgebase_05_transform_load_xml_to_sqlite):
    etld_lib_functions.logger.info(f"start {module_function}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def knowledgebase_06_distribution_wrapper(module_function=knowledgebase_06_distribution):
    etld_lib_functions.logger.info(f"start {module_function}")
    try:
        export_dir = etld_lib_config.kb_export_dir
        if Path(export_dir).is_dir():
            module_function.main()
        else:
            etld_lib_functions.logger.info(
                f"No distribution as directory does not exist: {export_dir}")
    except Exception as e:
        etld_lib_functions.logger.info(f"{module_function} ended with an {e}, "
                                       f"ignore if distribution is off.")
    etld_lib_functions.logger.info(f"end   {module_function}")


def knowledgebase_start_wrapper():
    global start_time
    start_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"__start__ knowledgebase_etl_workflow {str(sys.argv)}")
    etld_lib_functions.logger.info(f"data directory: {etld_lib_config.qetl_user_data_dir}")
    etld_lib_functions.logger.info(f"config file:    {etld_lib_config.qetl_user_config_settings_yaml_file}")
    etld_lib_functions.logger.info(f"cred yaml file: {etld_lib_credentials.cred_file}")
    etld_lib_functions.logger.info(f"cookie file:    {etld_lib_credentials.cookie_file}")


def knowledgebase_end_wrapper():
    global start_time
    global stop_time

    stop_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"runtime for knowledgebase_etl_workflow in seconds: {stop_time - start_time:,}")
    etld_lib_functions.logger.info(f"__end__ knowledgebase_etl_workflow {str(sys.argv)}")


def knowledgebase_etl_workflow():
    try:
        knowledgebase_start_wrapper()
        knowledgebase_03_extract_wrapper(message=f"kb_last_modified_after={etld_lib_config.kb_last_modified_after}")
        knowledgebase_05_transform_load_xml_to_sqlite_wrapper()
        knowledgebase_06_distribution_wrapper()
        knowledgebase_end_wrapper()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error occurred, please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def main():
    knowledgebase_etl_workflow()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name="knowledgebase_etl_workflow")
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
