import re
import json

from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables as etld_lib_sqlite_tables

global asset_inventory_sqlite_file


def asset_inventory_sqlite():
    global asset_inventory_sqlite_file
    sqlite_asset_inventory = etld_lib_sqlite_tables.SqliteObj(asset_inventory_sqlite_file)

    sqlite_asset_inventory.drop_and_recreate_table(
        etld_lib_config.asset_inventory_table_name_software_assetid,
        etld_lib_config.asset_inventory_software_assetid_csv_columns(),
        False, etld_lib_config.asset_inventory_software_assetid_csv_column_types())

    sqlite_asset_inventory.bulk_insert_csv_file(
        etld_lib_config.asset_inventory_table_name_software_assetid,
        etld_lib_config.asset_inventory_csv_software_assetid_file,
        etld_lib_config.asset_inventory_software_assetid_csv_columns(),
        "software_assetid", 10000)

    sqlite_asset_inventory.drop_and_recreate_table(
        etld_lib_config.asset_inventory_table_name_software_unique,
        etld_lib_config.asset_inventory_software_unique_csv_columns(),
        False)

    sqlite_asset_inventory.bulk_insert_csv_file(etld_lib_config.asset_inventory_table_name_software_unique,
                                                etld_lib_config.asset_inventory_csv_software_unique_file,
                                                etld_lib_config.asset_inventory_software_unique_csv_columns(),
                                                "software_unique", 10000)

    sqlite_asset_inventory.drop_and_recreate_table(
        etld_lib_config.asset_inventory_table_name_software_os_unique,
        etld_lib_config.asset_inventory_software_os_unique_csv_columns(),
        False)

    sqlite_asset_inventory.bulk_insert_csv_file(etld_lib_config.asset_inventory_table_name_software_os_unique,
                                                etld_lib_config.asset_inventory_csv_software_os_unique_file,
                                                etld_lib_config.asset_inventory_software_os_unique_csv_columns(),
                                                "software_os_unique", 10000)

    sqlite_asset_inventory.drop_and_recreate_table(etld_lib_config.asset_inventory_table_name,
                                                   etld_lib_config.asset_inventory_csv_columns(),
                                                   key='assetId')

    sqlite_asset_inventory.bulk_insert_csv_file(etld_lib_config.asset_inventory_table_name,
                                                etld_lib_config.asset_inventory_csv_file,
                                                etld_lib_config.asset_inventory_csv_columns(),
                                                "full asset inventory", 10000)
    sqlite_asset_inventory.commit_changes()
    sqlite_asset_inventory.close_connection()
    etld_lib_functions.logger.info(f"count rows added to {etld_lib_config.asset_inventory_table_name} table: "
                                   f"{sqlite_asset_inventory.count_rows_added_to_table:,}")


def start_msg_asset_inventory_sqlite():
    etld_lib_functions.logger.info(f"start")


def end_msg_asset_inventory_sqlite():
    etld_lib_functions.log_file_info(etld_lib_config.asset_inventory_csv_file)
    etld_lib_functions.log_file_info(asset_inventory_sqlite_file)
    etld_lib_functions.logger.info(f"end")


def setup_vars():
    global asset_inventory_sqlite_file
    try:
        asset_inventory_sqlite_file
    except:
        asset_inventory_sqlite_file = etld_lib_config.asset_inventory_sqlite_file


def main():
    start_msg_asset_inventory_sqlite()
    setup_vars()
    asset_inventory_sqlite()
    end_msg_asset_inventory_sqlite()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='asset_inventory_sqlite')
    etld_lib_config.main()
    main()

