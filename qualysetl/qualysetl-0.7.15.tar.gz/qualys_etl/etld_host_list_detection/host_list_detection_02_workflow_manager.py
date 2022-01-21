#!/usr/bin/env python3
import sys
import timeit
import time
from pathlib import Path
import multiprocessing
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials

from qualys_etl.etld_host_list_detection import host_list_detection_03_extract_controller
from qualys_etl.etld_host_list_detection import host_list_detection_05_transform_load_xml_to_sqlite
from qualys_etl.etld_host_list_detection import host_list_detection_06_distribution
from qualys_etl.etld_host_list import host_list_02_workflow_manager
from qualys_etl.etld_knowledgebase import knowledgebase_02_workflow_manager

global start_time
global stop_time


def host_list_02_workflow_manager_wrapper(module_function=host_list_02_workflow_manager, message=""):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def knowledgebase_02_workflow_manager_wrapper(
       module_function=knowledgebase_02_workflow_manager, message=""
):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def host_list_detection_03_extract_controller_wrapper(module_function=host_list_detection_03_extract_controller, message=""):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def host_list_detection_05_transform_load_xml_to_sqlite_wrapper(
        module_function=host_list_detection_05_transform_load_xml_to_sqlite):
    etld_lib_functions.logger.info(f"start {module_function}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def host_list_detection_06_distribution_wrapper(module_function=host_list_detection_06_distribution):
    etld_lib_functions.logger.info(f"start {module_function}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


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


def spawn_host_list_02_workflow_manager_wrapper():
    queue_of_batch_names_loaded_into_sqlite = multiprocessing.Queue()
    queue_process = \
        multiprocessing.Process(target=host_list_02_workflow_manager.main,
                                args=(queue_of_batch_names_loaded_into_sqlite,),
                                name='host_list_02_workflow_manager')
    return queue_process,queue_of_batch_names_loaded_into_sqlite


def spawn_knowledgebase_02_workflow_manager_wrapper():
    process = \
        multiprocessing.Process(target=knowledgebase_02_workflow_manager.main,
                                name='knowledgebase_02_workflow_manager')
    process.daemon = True
    process.start()
    return process


def host_list_detection_etl_workflow():
    host_list_detection_start_wrapper()

    try:
        knowledgebase_process = spawn_knowledgebase_02_workflow_manager_wrapper()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error knowledgebase_02_workflow_manager_wrapper, please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)

    try:
        etld_lib_config.host_list_detection_vm_processed_after = etld_lib_config.host_list_vm_processed_after
        long_message = f"host_list_detection_vm_processed_after = " \
                       f"host_list_vm_processed_after={etld_lib_config.host_list_vm_processed_after}"
        host_list_02_workflow_manager_wrapper(message=long_message)
        while True:
            if knowledgebase_process.is_alive():
                time.sleep(1)
            else:
                if knowledgebase_process.exitcode != 0:
                    etld_lib_functions.logger.error(
                       "Error in knowledgebase processing.  Please investigate logs and repair issue.")
                    etld_lib_functions.logger.error(f"exit code for knowledgebase is: {knowledgebase_process.exitcode}")
                    raise Exception("knowledgebase_process exception")
                break

        # TODO create multiprocessing queue of host list batches loaded into sqlite.
        # TODO Use multiprocessing queue in host list detection to start processing host list as it is being downloaded
        # TODO instead of waiting.

    except Exception as e:
        etld_lib_functions.logger.error(f"Error host_list_02_workflow_manager_wrapper, please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)

    try:
        host_list_detection_03_extract_controller_wrapper(
            message=f"vm_processed_after={etld_lib_config.host_list_detection_vm_processed_after}")
    except Exception as e:
        etld_lib_functions.logger.error(f"Error host_list_detection_03_extract_controller_wrapper, please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)

    try:
        host_list_detection_06_distribution_wrapper()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error host_list_detection_06_distribution_wrapper, please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)

    host_list_detection_end_wrapper()


def main():
    host_list_detection_etl_workflow()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_etl_workflow')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
