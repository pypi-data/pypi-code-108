#!/usr/bin/env python3
import time
import json
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_extract_transform_load
from qualys_etl.etld_asset_inventory import asset_inventory_05_transform_load_json_to_sqlite
from qualys_etl.etld_asset_inventory import asset_inventory_04_extract_from_qualys


def start_msg_get_asset_inventory_data():
    etld_lib_functions.logger.info(f"start")


def end_msg_get_asset_inventory_data():
    etld_lib_functions.logger.info(f"end")


def get_next_batch(json_file=None):
    asset_inventory_batch_status = {}
    with etld_lib_config.asset_inventory_open_file_compression_method(json_file, "rt", encoding='utf-8') as read_file:
        asset_inventory_dict = json.load(read_file)
        if 'hasMore' in asset_inventory_dict.keys():
            asset_inventory_batch_status = {
                'responseCode': asset_inventory_dict['responseCode'],
                'count': asset_inventory_dict['count'],
                'hasMore': asset_inventory_dict['hasMore'],
                'lastSeenAssetId': asset_inventory_dict['lastSeenAssetId'],
                          }

        if 'hasMore' not in asset_inventory_batch_status.keys():
            etld_lib_functions.logger.error("Error downloading records")
            etld_lib_functions.logger.error(f"asset_inventory_batch_status: {asset_inventory_batch_status}")
            exit(1)

    return asset_inventory_batch_status


def start_multiprocessing_transform_json_to_sqlite():

    if etld_lib_config.asset_inventory_json_to_sqlite_via_multiprocessing is True:
        batch_queue_of_file_paths, batch_queue_process = \
            asset_inventory_05_transform_load_json_to_sqlite.\
            spawn_multiprocessing_queue_to_transform_and_load_json_files_into_sqlite()
        etld_lib_functions.logger.info(f"Queue of json files process id: {batch_queue_process.pid} ")
        batch_queue_of_file_paths.put("BEGIN")
        return batch_queue_of_file_paths, batch_queue_process
    else:
        return None, None


def add_batch_to_transform_json_to_sqlite(batch_number_str, json_file, batch_queue_of_file_paths, batch_queue_process):

    if etld_lib_config.asset_inventory_json_to_sqlite_via_multiprocessing is True:
        etld_lib_functions.logger.info(f"Sending batch file to multiprocessing Queue: {batch_number_str}")
        batch_queue_of_file_paths.put(str(json_file))
        if batch_queue_process.is_alive():
            pass
        else:
            etld_lib_functions.logger.error("Batch Process was killed or database error, please investigate and retry.")
            exit(1)


def stop_multiprocessing_transform_json_to_sqlite(batch_queue_process, batch_queue_of_file_paths):

    if etld_lib_config.asset_inventory_json_to_sqlite_via_multiprocessing is True:
        batch_queue_of_file_paths.put("END")
        while True:
            if batch_queue_process.is_alive():
                etld_lib_functions.logger.info("Waiting for Queue to end.")
                time.sleep(15)
            else:
                etld_lib_functions.logger.info("Queue Completed.")
                break


def check_qualys_connection_rate_limits(batch_number_str, qualys_headers_dict, batch_info):

    if batch_number_str in qualys_headers_dict.keys():
        if 'x_ratelimit_remaining' in qualys_headers_dict[batch_number_str].keys():
            x_ratelimit_remaining = qualys_headers_dict[batch_number_str]['x_ratelimit_remaining']
            if int(x_ratelimit_remaining) < 100:
                etld_lib_functions.logger.warning(f"x_ratelimit_remaining is less than 100. "
                                                  f"Sleeping 5 min.  batch_info: {batch_info}, "
                                                  f"header_info: {qualys_headers_dict[batch_number_str]}")
                time.sleep(300)
        else:
            etld_lib_functions.logger.warning(f"x_ratelimit_remaining missing from Qualys Header. "
                                              f"Sleeping 5 min.  batch_info: {batch_info}, "
                                              f"header_info: {qualys_headers_dict[batch_number_str]}")
            time.sleep(300)


def get_asset_inventory_data():

    start_msg_get_asset_inventory_data()
    etld_lib_config.remove_old_files(
        dir_path=etld_lib_config.asset_inventory_extract_dir,
        dir_search_glob=etld_lib_config.asset_inventory_extract_dir_file_search_blob,
        other_files_list=etld_lib_config.asset_inventory_data_files
    )
    etld_lib_config.remove_old_files(
        dir_path=etld_lib_config.asset_inventory_extract_dir,
        dir_search_glob=etld_lib_config.asset_inventory_extract_dir_file_search_blob_two,
    )

    batch_queue_of_file_paths, batch_queue_process = \
        start_multiprocessing_transform_json_to_sqlite()

    utc_datetime = etld_lib_datetime.get_utc_datetime_qualys_format()
    qualys_headers_dict = {}
    batch_info = {'hasMore': '1', 'lastSeenAssetId': 0}
    has_more_records = '1'
    batch_number = 0
    batch_number_str = f'batch_{batch_number:06d}'
    cred_dict = etld_lib_credentials.get_cred(cred_dict={})
    cred_dict = etld_lib_credentials.get_bearer_stored_in_env(update_bearer=False, cred=cred_dict)

    file_info_dict = \
        etld_lib_config.prepare_extract_batch_file_name(
            next_batch_number_str='batch_000000',
            next_batch_date=utc_datetime,
            extract_dir=etld_lib_config.asset_inventory_extract_dir,
            file_name_type="asset_inventory_count",
            file_name_option="assetLastUpdated",
            file_name_option_date=etld_lib_config.asset_inventory_asset_last_updated,
            file_extension="json",
            compression_method=etld_lib_config.asset_inventory_open_file_compression_method)

    asset_inventory_04_extract_from_qualys.asset_inventory_extract_count(
        asset_last_updated=etld_lib_config.asset_inventory_asset_last_updated,
        last_seen_assetid=str(batch_info['lastSeenAssetId']),
        batch_number_str=batch_number_str,
        qualys_headers_dict=qualys_headers_dict,
        cred_dict=cred_dict,
        file_info_dict=file_info_dict)

    while has_more_records == '1':
        batch_number = batch_number + 1
        batch_number_str = f'batch_{batch_number:06d}'

        file_info_dict = \
            etld_lib_config.prepare_extract_batch_file_name(
                next_batch_number_str=batch_number_str,
                next_batch_date=utc_datetime,
                extract_dir=etld_lib_config.asset_inventory_extract_dir,
                file_name_type="asset_inventory",
                file_name_option="assetLastUpdated",
                file_name_option_date=etld_lib_config.asset_inventory_asset_last_updated,
                file_extension="json",
                compression_method=etld_lib_config.asset_inventory_open_file_compression_method)

        asset_inventory_04_extract_from_qualys.asset_inventory_extract(
            asset_last_updated=etld_lib_config.asset_inventory_asset_last_updated,
            last_seen_assetid=str(batch_info['lastSeenAssetId']),
            batch_number_str=batch_number_str,
            qualys_headers_dict=qualys_headers_dict,
            cred_dict=cred_dict,
            file_info_dict=file_info_dict)

        add_batch_to_transform_json_to_sqlite(
            batch_number_str=batch_number_str, json_file=file_info_dict['next_file_path'],
            batch_queue_process=batch_queue_process, batch_queue_of_file_paths=batch_queue_of_file_paths)

        batch_info = get_next_batch(json_file=file_info_dict['next_file_path'])
        has_more_records = str(batch_info['hasMore'])
        etld_lib_functions.logger.info(f"{batch_number_str} info: {batch_info}")

        has_more_records = test_system_option(
            file_path=file_info_dict['next_file_path'],
            has_more_records=has_more_records,
            number_of_files_to_extract=etld_lib_config.asset_inventory_test_number_of_files_to_extract,
            test_system_flag=etld_lib_config.asset_inventory_test_system_flag
        )

        check_qualys_connection_rate_limits(batch_number_str, qualys_headers_dict, batch_info)

    stop_multiprocessing_transform_json_to_sqlite(
        batch_queue_of_file_paths=batch_queue_of_file_paths, batch_queue_process=batch_queue_process)
    end_msg_get_asset_inventory_data()


def test_system_option(file_path: Path, has_more_records, number_of_files_to_extract, test_system_flag):
    if test_system_flag is True:
        test_batch_number = \
            etld_lib_extract_transform_load.get_batch_number_from_filename(file_path)
        if int(test_batch_number) >= number_of_files_to_extract:
            has_more_records = '0'
    return has_more_records


def main():
    get_asset_inventory_data()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='asset_inventory_04_extract_from_qualys')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
