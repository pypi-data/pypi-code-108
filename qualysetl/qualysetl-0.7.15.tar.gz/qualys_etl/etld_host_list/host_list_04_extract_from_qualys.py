#!/usr/bin/env python3
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_credentials as etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_extract_transform_load as etld_lib_extract_transform_load_distribute


def host_list_extract_batch(host_xml_file=None, id_min=0,
                            batch_number=None, cred_dict={}, qualys_headers_multiprocessing_dict={}):

    start_msg_host_list_extract()
    authorization = cred_dict['authorization']  # Base64 user:password
    url = f"https://{cred_dict['api_fqdn_server']}/api/2.0/fo/asset/host/"  # Qualys Endpoint

    payload = etld_lib_config.host_list_api_payload
    payload.update({'id_min': id_min})
    if isinstance(etld_lib_config.host_list_payload_option, dict):
        payload.update(etld_lib_config.host_list_payload_option)

    headers = {'X-Requested-With': 'qualysetl', 'Authorization': authorization}

    etld_lib_functions.logger.info(f"api call     - {url}")
    etld_lib_functions.logger.info(f"api options  - {payload}")

    etld_lib_extract_transform_load_distribute.extract_qualys(
        try_extract_max_count=etld_lib_config.host_list_try_extract_max_count,
        url=url,
        headers=headers,
        payload=payload,
        http_conn_timeout=etld_lib_config.host_list_http_conn_timeout,
        chunk_size_calc=etld_lib_config.host_list_chunk_size_calc,
        output_file=host_xml_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_multiprocessing_dict,
        multi_proc_batch_number=batch_number,
        compression_method=etld_lib_config.host_list_open_file_compression_method)
    end_msg_host_list_extract()


def host_list_extract(cred_dict: dict):

    start_msg_host_list_extract()
    authorization = cred_dict['authorization']  # Base64 user:password
    url = f"https://{cred_dict['api_fqdn_server']}/api/2.0/fo/asset/host/"  # Qualys Endpoint
    xml_files = {'host_list_other_xml_file': etld_lib_config.host_list_other_xml_file}
    payload = etld_lib_config.host_list_api_payload
    payload.update({'truncation_limit': '0'})
    if isinstance(etld_lib_config.host_list_payload_option, dict):
        payload.update(etld_lib_config.host_list_payload_option)
    etld_lib_functions.logger.info(f"api call     - {url}")
    etld_lib_functions.logger.info(f"api options  - {payload}")

    chunk_size_calc = etld_lib_config.host_list_chunk_size_calc
    try_extract_max_count = etld_lib_config.host_list_try_extract_max_count
    http_conn_timeout = etld_lib_config.host_list_http_conn_timeout
    qualys_headers = {}
    multi_proc_batch_number = None
    headers = {'X-Requested-With': 'qualysetl', 'Authorization': authorization}
    etld_lib_extract_transform_load_distribute.extract_qualys(
        try_extract_max_count=try_extract_max_count,
        url=url,
        headers=headers,
        payload=payload,
        http_conn_timeout=http_conn_timeout,
        chunk_size_calc=chunk_size_calc,
        output_file=host_xml_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers,
        multi_proc_batch_number=multi_proc_batch_number,
        compression_method=etld_lib_config.host_list_open_file_compression_method)
    end_msg_host_list_extract()
    return qualys_headers


def start_msg_host_list_extract():
    etld_lib_functions.logger.info(f"start ")


def end_msg_host_list_extract():
    etld_lib_functions.logger.info(f"end")


def main():
    host_list_extract(cred_dict=etld_lib_credentials.get_cred())


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_extract')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()



