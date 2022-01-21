#!/usr/bin/env python3
import sys
import timeit
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials as etld_lib_credentials

import qualys_etl.etld_asset_inventory.asset_inventory_process_00_extract_controller as asset_inventory_extract
import qualys_etl.etld_asset_inventory.asset_inventory_process_01_transform_load_json_to_sqlite as asset_inventory_json_to_sqlite
import qualys_etl.etld_asset_inventory.asset_inventory_process_01_transform_to_shelve as asset_inventory_to_shelve
import qualys_etl.etld_asset_inventory.asset_inventory_process_03_load_csv as asset_inventory_csv
import qualys_etl.etld_asset_inventory.asset_inventory_process_04_load_sqlite as asset_inventory_sqlite
import qualys_etl.etld_asset_inventory.asset_inventory_process_05_distribution as asset_inventory_distribution

global start_time
global stop_time


def asset_inventory_extract_wrapper():
    etld_lib_functions.logger.info(f"start asset_inventory_extract from Qualys")
    etld_lib_functions.logger.info(f"     asset_last_updated={etld_lib_config.asset_inventory_asset_last_updated}")
    asset_inventory_extract.main()
    etld_lib_functions.logger.info(f"end   asset_inventory_extract from Qualys")


def asset_inventory_json_to_sqlite_wrapper():

    etld_lib_functions.logger.info(f"start asset_inventory json to sqlite")
    asset_inventory_json_to_sqlite.main()
    etld_lib_functions.logger.info(f"end   asset_inventory json to shelve")


def asset_inventory_to_shelve_wrapper():

    etld_lib_functions.logger.info(f"start asset_inventory json to shelve")
    asset_inventory_to_shelve.main()
    etld_lib_functions.logger.info(f"end   asset_inventory json to shelve")


def asset_inventory_to_csv_wrapper():
    etld_lib_functions.logger.info(f"start asset_inventory_csv - shelve to csv")
    asset_inventory_csv.main()
    etld_lib_functions.logger.info(f"end   asset_inventory_csv - shelve to csv")


def asset_inventory_to_sqlite_wrapper():
    etld_lib_functions.logger.info(f"start asset_inventory_sqlite transform Shelve to Sqlite3 DB")
    asset_inventory_sqlite.main()
    etld_lib_functions.logger.info(f"end   asset_inventory_sqlite transform Shelve to Sqlite3 DB")


def asset_inventory_distribution_wrapper():
    try:
        does_dir_exist = etld_lib_config.asset_inventory_export_dir
        try:
            etld_lib_functions.logger.info(f"start asset_inventory_distribution")
            asset_inventory_distribution.main()
            etld_lib_functions.logger.info(f"end   asset_inventory_distribution")
        except Exception as e:
            etld_lib_functions.logger.info(f"asset_inventory_distribution ended with an {e}, ignore if distribution is off.")
    except Exception as e:
        # no distribution directory found and that's ok.
        pass


def asset_inventory_start_wrapper():
    global start_time
    start_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"__start__ asset_inventory_etl_workflow {str(sys.argv)}")
    etld_lib_functions.logger.info(f"data directory: {etld_lib_config.qetl_user_data_dir}")
    etld_lib_functions.logger.info(f"config file:    {etld_lib_config.qetl_user_config_settings_yaml_file}")
    etld_lib_functions.logger.info(f"cred yaml file: {etld_lib_credentials.cred_file}")
    etld_lib_functions.logger.info(f"bearer file:    {etld_lib_credentials.bearer_file}")


def asset_inventory_end_wrapper():
    global start_time
    global stop_time

    stop_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"runtime for asset_inventory_etl_workflow in seconds: {stop_time - start_time:,}")
    etld_lib_functions.logger.info(f"__end__ asset_inventory_etl_workflow {str(sys.argv)}")


def asset_inventory_etl_workflow():
    try:
        asset_inventory_start_wrapper()
        asset_inventory_extract_wrapper()
        asset_inventory_json_to_sqlite_wrapper()
        #asset_inventory_to_shelve_wrapper()
        #asset_inventory_to_csv_wrapper()
        #asset_inventory_to_sqlite_wrapper()
        asset_inventory_distribution_wrapper()
        asset_inventory_end_wrapper()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error occurred, please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def main():
    asset_inventory_etl_workflow()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='asset_inventory_etl_workflow')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
