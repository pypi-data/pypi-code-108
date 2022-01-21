import re
import sqlite3
import time
import multiprocessing
from pathlib import Path
import os
import oschmod
import json
import shelve
import shutil
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials as etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables as etld_lib_sqlite_tables
from qualys_etl.etld_lib import etld_lib_datetime as etld_lib_datetime
import qualys_etl.etld_asset_inventory.asset_inventory_process_00_extract as asset_inventory_extract

global host_list_records
global host_list_records_count
global host_list_get_scope_of_host_ids_sql
global asset_inventory_vm_processed_after
global asset_inventory_multi_proc_batch_size
global asset_inventory_concurrency_limit
global asset_inventory_batch_queue
global asset_inventory_limit_hosts
global spawned_process_info_list
global already_reported_spawned_process_info_status
global qualys_headers_multi_proc_dict
global xml_file_utc_run_datetime


# Create queue of batches to process.
# Each batch will be up to asset_inventory_multi_proc_batch_size.

def remove_old_files():
    if Path(etld_lib_config.asset_inventory_json_dir).name in 'asset_inventory_json_dir':
        os.makedirs(etld_lib_config.asset_inventory_json_dir, exist_ok=True)
        oschmod.set_mode(etld_lib_config.asset_inventory_json_dir, "a+rwx,g-rwx,o-rwx")
    # Remove old json files if they exist in asset_inventory_json_dir
    if Path(etld_lib_config.asset_inventory_json_dir).is_dir():
        if Path(etld_lib_config.asset_inventory_json_dir).name in 'asset_inventory_json_dir':
            count_files = 0
            for f in Path(etld_lib_config.asset_inventory_json_dir).glob('asset_inventory*.json'):
                count_files = count_files + 1
            etld_lib_functions.logger.info(f"Removing {count_files} old json files from dir: "
                                           f"{etld_lib_config.asset_inventory_json_dir}")

            files = Path(etld_lib_config.asset_inventory_json_dir).glob('asset_inventory*.json')
            try:
                for file in files:
                    file.unlink()
            except OSError as e:
                etld_lib_functions.logger.error(f"{e}")
                exit(1)
    try:
        for file_name in etld_lib_config.asset_inventory_data_files:
            if Path(file_name).is_file():
                etld_lib_functions.logger.info(f"Removing old asset inventory file: {str(file_name)}")
                Path(file_name).unlink()

    except Exception as e:
        etld_lib_functions.logger.error(f"{e}")
        exit(1)


def start_msg_get_asset_inventory_data():
    etld_lib_functions.logger.info(f"start")


def end_msg_get_asset_inventory_data():
    etld_lib_functions.logger.info(f"host_list get_scope_of_host_ids sql: {host_list_get_scope_of_host_ids_sql}")
    etld_lib_functions.logger.info(f"host_list sqlite file: {etld_lib_config.host_list_sqlite_file}")
    etld_lib_functions.logger.info(f"count host_list host id: {len(host_list_records):,}")
    etld_lib_functions.logger.info(f"end")


def get_next_batch(json_file=None):
    batch_info = {}
    with open(json_file, "r", encoding='utf-8') as read_file:
        with shelve.open(str(etld_lib_config.asset_inventory_temp_shelve_file), flag='n') as shelve_database_temp:
            shelve_database_temp = json.load(read_file)
            if 'hasMore' in shelve_database_temp.keys():
                batch_info = {'responseCode': shelve_database_temp['responseCode'],
                              'count': shelve_database_temp['count'],
                              'hasMore': shelve_database_temp['hasMore'],
                              'lastSeenAssetId': shelve_database_temp['lastSeenAssetId'],
                              }
    return batch_info


def get_asset_inventory_data():
    global qualys_headers_multi_proc_dict
    start_msg_get_asset_inventory_data()
    utc_datetime = etld_lib_datetime.get_utc_date()
    qualys_headers_multi_proc_dict = {}
    batch_info = {'hasMore': '1', 'lastSeenAssetId': 0}
    has_more_records = '1'
    batch_number = 0

    # Get Asset Inventory Count
    batch_number_str = f'batch_{batch_number:06d}'
    cred_dict = asset_inventory_extract.asset_inventory_extract_count(
        asset_last_updated=etld_lib_config.asset_inventory_asset_last_updated,
        last_seen_assetid=str(batch_info['lastSeenAssetId']),
        utc_datetime=utc_datetime,
        batch_number=batch_number_str,
        proc_dict=qualys_headers_multi_proc_dict,
        cred_dict={})

    # Extract Assets
    while has_more_records == '1':
        batch_number = batch_number + 1
        batch_number_str = f'batch_{batch_number:06d}'
        cred_dict = asset_inventory_extract.asset_inventory_extract(
            asset_last_updated=etld_lib_config.asset_inventory_asset_last_updated,
            last_seen_assetid=str(batch_info['lastSeenAssetId']),
            utc_datetime=utc_datetime,
            batch_number=batch_number_str,
            proc_dict=qualys_headers_multi_proc_dict,
            cred_dict=cred_dict)
        batch_info = get_next_batch(json_file=asset_inventory_extract.json_file)
        etld_lib_functions.logger.info(f"{batch_number_str} info: {batch_info}")
        if 'hasMore' in batch_info.keys():
            has_more_records = str(batch_info['hasMore'])
        else:
            etld_lib_functions.logger.error("Error downloading records")
            etld_lib_functions.logger.error(f"batch_info: {batch_info}")
            exit(1)
        if batch_number_str in qualys_headers_multi_proc_dict.keys():
            if 'x_ratelimit_remaining' in qualys_headers_multi_proc_dict[batch_number_str].keys():
                x_ratelimit_remaining = qualys_headers_multi_proc_dict[batch_number_str]['x_ratelimit_remaining']
                if int(x_ratelimit_remaining) < 100:
                    # Sleep for 5 minutes and run next.
                    etld_lib_functions.logger.warning(f"x_ratelimit_remaining is less than 100. "
                                                      f"Sleeping 5 min.  batch_info: {batch_info}, "
                                                      f"header_info: {qualys_headers_multi_proc_dict[batch_number_str]}")
                    time.sleep(300)
            else:
                etld_lib_functions.logger.warning(f"x_ratelimit_remaining missing from Qualys Header. "
                                                  f"Sleeping 5 min.  batch_info: {batch_info}, "
                                                  f"header_info: {qualys_headers_multi_proc_dict[batch_number_str]}")
                time.sleep(300)


def main():
    remove_old_files()
    get_asset_inventory_data()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='asset_inventory_extract_controller')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()

