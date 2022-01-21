#!/usr/bin/env python3
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_spawn_etl
from qualys_etl.etld_test_system import test_system_02_workflow_manager


def main():
    etld_lib_config.set_path_qetl_user_home_dir()
    etld_lib_spawn_etl.log_dir = etld_lib_config.qetl_user_log_dir
    etld_lib_spawn_etl.log_file_path = etld_lib_config.test_system_log_file
    etld_lib_spawn_etl.log_file_rotate_path = etld_lib_config.test_system_log_rotate_file
    etld_lib_spawn_etl.lock_file = etld_lib_config.test_system_lock_file
    etld_lib_spawn_etl.log_file_max_size = (1024 * 100000)          # 1024 * size = Max Meg Size
    etld_lib_spawn_etl.spawned_process_max_run_time = 604800        # seconds before terminate as there is an issue.
    etld_lib_spawn_etl.spawned_process_sleep_time = 5               # check every n seconds for spawned_process.is_alive()
    etld_lib_spawn_etl.spawned_process_count_to_status_update = 11  # print status spawned_process.is_alive() after n checks

    etld_lib_spawn_etl.etl_dir_to_monitor = etld_lib_config.qetl_user_data_dir
    etld_lib_spawn_etl.etl_files_max_time_between_changes = 1800

    etld_lib_spawn_etl.target_module_to_run = test_system_02_workflow_manager.test_system_etl_workflow
    etld_lib_spawn_etl.target_method_in_module_to_run = "test_system_etl_workflow"
    etld_lib_spawn_etl.etl_main()


if __name__ == '__main__':
    main()
