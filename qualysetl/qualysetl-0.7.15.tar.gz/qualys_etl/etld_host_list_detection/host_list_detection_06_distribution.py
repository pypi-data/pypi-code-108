#!/usr/bin/env python3
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials as etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_distribution as api_dist


def host_list_detection_dist():
    try:
        file_paths = (
            etld_lib_config.host_list_detection_sqlite_file,
            etld_lib_config.host_list_detection_csv_file,
            etld_lib_config.host_list_detection_json_file,
        )
        api_dist.copy_results_to_external_target(file_paths, etld_lib_config.host_list_detection_export_dir)
    except Exception as e:
        etld_lib_functions.logger.error(f"Program aborted, ensure etld_lib_config_settings.yaml distribution "
                                        f"directory exists or is set to default: Exception: {e}")
        exit(1)


def check_if_distribution_directory_exists():
    distribution_directory_exists_flag = False
    try:
        export_dir = etld_lib_config.host_list_detection_export_dir
        if Path(export_dir).is_dir():
            distribution_directory_exists_flag = True
        else:
            etld_lib_functions.logger.info(
                f"No distribution as directory does not exist: {export_dir}, continue.")
            distribution_directory_exists_flag = False

    except Exception as e:
        etld_lib_functions.logger.warning(f"check_if_distribution_directory_exists ended with an {e}, "
                                          f"ignore if distribution is off.")
        distribution_directory_exists_flag = False

    return distribution_directory_exists_flag


def start_msg_host_list_detection_dist():
    etld_lib_functions.logger.info(f"start")


def end_msg_host_list_detection_dist():
    etld_lib_functions.logger.info(f"end")


def main():
    start_msg_host_list_detection_dist()
    if check_if_distribution_directory_exists():
        host_list_detection_dist()
    end_msg_host_list_detection_dist()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_distribution')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
