import fcntl
import multiprocessing
import shutil
import sys
import time
import re
from pathlib import Path
from datetime import datetime
import timeit
from contextlib import redirect_stdout, redirect_stderr

from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_functions

global target_module_to_run
global target_method_in_module_to_run
global spawned_process
global spawned_process_max_run_time
global spawned_process_start_time
global spawned_process_stop_time
global spawned_process_sleep_time
global spawned_process_count_to_status_update
global spawned_process_status_count
global log_file_max_size
global log_file_path
global log_file_rotate_path
global lock_file
global log_dir
global etl_dir_to_monitor
global etl_files_mtime_dict
global etl_files_max_time_between_changes
global etl_file_stalled


def spawn_etl_in_background_with_arg(args_list=[], max_proc=None):
    global spawned_process
    global spawned_process_start_time
    global spawned_process_status_count
    spawn_process_list = []

    # target=etl_host_list_detection
    # name=etl_hld_d_2021_06_03T00:00:00Z_b_000001
    # args=list_of_host_ids
    # Create jobs list  ready to spawn
    for arg in args_list:
        arg: dict
        arg.get('target_module_to_run')
        arg.get('target_method_in_module_to_run')
        arg.get('method_arguments')

        spawned_process = multiprocessing.Process(
            target=arg.get('target_module_to_run'),
            name=arg.get('target_method_in_module_to_run'),
            args=arg.get('method_arguments'))
        spawn_process_list.append(spawned_process)


def spawn_etl_in_background():
    global spawned_process
    global spawned_process_start_time
    global spawned_process_status_count
    global etl_dir_to_monitor
    global etl_files_mtime_dict
    etl_files_mtime_dict = {}

    spawned_process = multiprocessing.Process(target=target_module_to_run, name=target_method_in_module_to_run)
    spawned_process.start()
    etld_lib_functions.logger.info("Spawned ETL in Background")
    spawned_process_start_time = timeit.default_timer()
    spawned_process_status_count = 0
    etl_initial_file_for_monitoring = Path(etl_dir_to_monitor, str(target_method_in_module_to_run))
    Path.touch(etl_initial_file_for_monitoring, exist_ok=True)

    while spawned_process.is_alive():
        spawned_process_report_status()

    spawned_process_ended()
    time.sleep(1)


def etl_files_are_stalled():
    global etl_dir_to_monitor
    global etl_files_max_time_between_changes
    global etl_file_stalled
    etl_files_max_time_exceeded_flag = True
    etl_files = Path(etl_dir_to_monitor).glob('**/*')
    vm_workflow = \
        re.fullmatch(r"^.*(knowledgebase_etl_workflow|host_list_etl_workflow|host_list_detection_etl_workflow).*$",
                     str(target_method_in_module_to_run))
    asset_inventory_workflow = \
        re.fullmatch(r"^.*(asset_inventory_etl_workflow).*$",
                     str(target_method_in_module_to_run))

    was_workflow = \
        re.fullmatch(r"^.*(was_etl_workflow).*$",
                     str(target_method_in_module_to_run))

    test_system_workflow = \
        re.fullmatch(
            r"^.*(test_system_etl_workflow).*$", str(target_method_in_module_to_run))

    try:
        if vm_workflow:
            workflow_pattern = re.compile(r"^.*(/knowledgebase|/kb|/host_list).*$")
        elif asset_inventory_workflow:
            workflow_pattern = re.compile(r"^.*(/asset_inventory).*$")
        elif was_workflow:
            workflow_pattern = re.compile(r"^.*(/was).*$")
        elif test_system_workflow:
            workflow_pattern = re.compile(r"^.*(/test_system|/knowledgebase|/kb|/host_list|asset_inventory/was).*$")
        else:
            etld_lib_functions.logger.error("Could not determine workflow type.")
            etld_lib_functions.logger.error("Please investigate.")
            raise Exception("Error determining workflow type")

        for etl_file_path in etl_files:
            if Path(etl_file_path).is_file():
                workflow_pattern_match = re.fullmatch(workflow_pattern, str(Path(etl_file_path)))
                if workflow_pattern_match:
                    mtime = int(Path(etl_file_path).stat().st_mtime)
                    datetime_now = datetime.now().timestamp()
                    datetime_diff = datetime_now - mtime
                    if datetime_diff < etl_files_max_time_between_changes:
                        etl_files_max_time_exceeded_flag = False
                        break  # Files have changed, break and continue.
                    else:
                        etl_file_stalled = Path(etl_file_path)
    except Exception as e:
        etl_files_max_time_exceeded_flag = True
        etld_lib_functions.logger.error(f"Could not determine file paths for monitoring: {etl_dir_to_monitor}")
        etld_lib_functions.logger.error(f"Please investigate Error: {e}.")

    if etl_files_max_time_exceeded_flag:
        etld_lib_functions.logger.info(f"{str(target_method_in_module_to_run)} is stalled.")

    return etl_files_max_time_exceeded_flag


def spawned_process_report_status():
    now = timeit.default_timer()
    run_time = (now - spawned_process_start_time)
    if run_time > spawned_process_max_run_time:
        terminate_spawned_process()
    else:
        spawned_process_status_update()


def spawned_process_ended():
    global spawned_process_stop_time
    spawned_process_stop_time = timeit.default_timer()
    run_time = (spawned_process_stop_time - spawned_process_start_time)
    etld_lib_functions.logger.info(f"Final Runtime: {run_time:,.0f} seconds")


def spawned_process_status_update():
    global spawned_process_status_count
    time.sleep(spawned_process_sleep_time)
    if spawned_process_status_count > spawned_process_count_to_status_update or spawned_process_status_count == 0:
        etld_lib_functions.logger.info(f"Job PID {str(spawned_process.pid)} {target_module_to_run.__name__} "
                             f"job running in background.")
        spawned_process_status_count = 1
        if etl_files_are_stalled():
            terminate_spawned_process_due_to_stalled_output()
    else:
        spawned_process_status_count = spawned_process_status_count + 1


def terminate_spawned_process_due_to_stalled_output():
    etld_lib_functions.logger.error(f"Stalled Error: {etl_files_max_time_between_changes:,.0f} Seconds Exceeded")
    etld_lib_functions.logger.error(f"Directory:     {etl_dir_to_monitor} Directory monitored for changes.")
    etld_lib_functions.logger.error(f"Please review previous extract function name in log to identify the "
                                    f"stalling program.")
    etld_lib_functions.logger.error(f"Use api options from the logs to create curl command to simulate issue.")
    etld_lib_functions.logger.error(f"Provide feedback to your Qualys TAM to assist with engaging support "
                                    f"if problem persists.")
    etld_lib_functions.logger.error(f"Terminating job.")
    spawned_process.terminate()
    spawned_process.join()
    exit(1)


def terminate_spawned_process():
    etld_lib_functions.logger.error(f"Max Run Time: {spawned_process_max_run_time:,.0f} Seconds Exceeded")
    etld_lib_functions.logger.error(f"Please review for issues that are slowing down the program.")
    etld_lib_functions.logger.error(f"Terminating job.")
    spawned_process.terminate()
    spawned_process.join()
    exit(1)


def rotate_log_check():
    if log_file_path.is_file():
        log_file_size = log_file_path.stat().st_size  # In Bytes
        if log_file_size > log_file_max_size:
            shutil.copy2(log_file_path, log_file_rotate_path, follow_symlinks=True)
            fo = open(log_file_path, 'w+')
            fo.close()


def etl_main():
    try:
        with open(lock_file, 'wb+') as lock_program_fcntl:        # If locked, exit.
            fcntl.flock(lock_program_fcntl, fcntl.LOCK_EX | fcntl.LOCK_NB)
            rotate_log_check()
            if log_dir.is_dir():
                with open(log_file_path, 'a', newline='', encoding='utf-8') as log_fo:
                    with redirect_stdout(log_fo), redirect_stderr(sys.stdout):
                        etld_lib_functions.main(my_logger_prog_name=target_module_to_run.__name__)
                        etld_lib_config.main()
                        etld_lib_credentials.main()
                        spawn_etl_in_background()
    except Exception as e:
        print(f"Program is already running.  Please re-run when ready. {__file__} ")
        print(f"Exception: {e}")
        exit(1)

