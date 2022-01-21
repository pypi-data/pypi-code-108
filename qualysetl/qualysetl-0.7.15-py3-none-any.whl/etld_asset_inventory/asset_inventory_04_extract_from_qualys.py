#!/usr/bin/env python3
from pathlib import Path
import json
from qualys_etl.etld_lib import etld_lib_credentials as etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_extract_transform_load as etld_lib_extract_transform_load_distribute


def asset_inventory_extract(
        asset_last_updated, last_seen_assetid, batch_number_str, qualys_headers_dict, cred_dict, file_info_dict):

    start_msg_asset_inventory_extract()
    bearer = cred_dict['bearer']
    page_size = 300

    # /rest/2.0/search/am/asset?assetLastUpdated=2021-06-01T00:00:00Z&lastSeenAssetId=0
    url = f"https://{cred_dict['gateway_fqdn_server']}/rest/2.0/search/am/asset"
    url = f"{url}?assetLastUpdated={asset_last_updated}&lastSeenAssetId={last_seen_assetid}&pageSize={page_size}"
    headers = {'X-Requested-With': 'qualysetl', 'Authorization': bearer, 'Content-Type': 'application/json'}
    etld_lib_functions.logger.info(f"api call     - {url}")

    json_file = Path(file_info_dict['next_file_path'])

    etld_lib_extract_transform_load_distribute.extract_qualys(
        try_extract_max_count=etld_lib_config.asset_inventory_try_extract_max_count,
        url=url,
        headers=headers,
        payload={},
        http_conn_timeout=etld_lib_config.asset_inventory_http_conn_timeout,
        chunk_size_calc=etld_lib_config.asset_inventory_chunk_size_calc,
        output_file=json_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_dict,
        multi_proc_batch_number=batch_number_str,
        extract_validation_type='json',
        compression_method=etld_lib_config.asset_inventory_open_file_compression_method)
    end_msg_asset_inventory_extract()


def asset_inventory_extract_count(asset_last_updated, last_seen_assetid, batch_number_str, qualys_headers_dict, cred_dict, file_info_dict):

    bearer = cred_dict['bearer']
    url = f"https://{cred_dict['gateway_fqdn_server']}/rest/2.0/count/am/asset"
    url = f"{url}?assetLastUpdated={asset_last_updated}&lastSeenAssetId={last_seen_assetid}"
    headers = {'X-Requested-With': 'qualysetl', 'Authorization': bearer, 'Content-Type': 'application/json'}
    etld_lib_functions.logger.info(f"api call     - {url}")

    json_file = Path(file_info_dict['next_file_path'])

    etld_lib_extract_transform_load_distribute.extract_qualys(
        try_extract_max_count=etld_lib_config.asset_inventory_try_extract_max_count,
        url=url,
        headers=headers,
        payload={},
        http_conn_timeout=etld_lib_config.asset_inventory_http_conn_timeout,
        chunk_size_calc=etld_lib_config.asset_inventory_chunk_size_calc,
        output_file=json_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_dict,
        multi_proc_batch_number=batch_number_str,
        extract_validation_type='json')

    asset_inventory_log_count(json_file=json_file)


def asset_inventory_log_count(json_file):
    try:
        with etld_lib_config.asset_inventory_open_file_compression_method(
                str(json_file), "rt", encoding='utf-8') as read_file:
            ai_count = json.load(read_file)
            if "responseCode" in ai_count.keys():
                if ai_count['responseCode'] == 'SUCCESS':
                    etld_lib_functions.logger.info(f"Asset Inventory Count: {ai_count['count']}")
                else:
                    raise Exception(f"Asset Inventory Count Failed, responseCode: {ai_count['responseCode']},"
                                    f" responseMessage: {ai_count['responseMessage']}")
    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Potential JSON File corruption or api error detected: {json_file}")
        exit(1)


def start_msg_asset_inventory_extract():
    etld_lib_functions.logger.info(f"start")


def end_msg_asset_inventory_extract():
    etld_lib_functions.logger.info(f"end")


def main(args=None):
    asset_inventory_extract()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='asset_inventory_extract')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()



