#!/usr/bin/env python3
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_distribution


def was_dist():
    try:
        file_paths = (
            etld_lib_config.was_sqlite_file,
            etld_lib_config.was_csv_file,
        )
        etld_lib_distribution.copy_results_to_external_target(file_paths, etld_lib_config.was_export_dir)
    except Exception as e:
        etld_lib_functions.logger.error(f"Program aborted, ensure etld_lib_config_settings.yaml distribution "
                                        f"directory exists or is set to default: Exception: {e}")
        exit(1)


def start_msg_was_dist():
    etld_lib_functions.logger.info(f"start")


def end_msg_was_dist():
    etld_lib_functions.logger.info(f"end")


def main():
    start_msg_was_dist()
    was_dist()
    end_msg_was_dist()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='was_distribution')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
