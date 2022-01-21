#!/usr/bin/env python3
from pathlib import Path
import json
import gzip
import re
from qualys_etl.etld_lib import etld_lib_credentials as etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_extract_transform_load as etld_lib_extract_transform_load_distribute


def was_webapp_extract(batch_number_str, qualys_headers_dict, cred_dict, file_info_dict,
                       last_id=0, page_size=25):

    start_msg_was_extract(function_name='was_webapp_extract')
    payload = '{"ServiceRequest": {' \
              '"preferences": {"limitResults": ' \
              f'"{page_size}"' \
              ', "verbose": "true"}, ' \
              '"filters": {' '"Criteria": ' \
              '{"field": "id", "operator": "GREATER", "value": ' \
              f'"{last_id}"' + '}}}}'

    url = f"https://{cred_dict['api_fqdn_server']}/qps/rest/3.0/search/was/webapp"
    headers = {'X-Requested-With': 'qualysetl',
               'Authorization': cred_dict['authorization'],
               'Content-Type': 'application/json',
               'Accept': 'application/json',
               }

    etld_lib_functions.logger.info(f"api call     - URL:{url} - PAYLOAD:{payload}")
    json_file = Path(file_info_dict['next_file_path'])

    etld_lib_extract_transform_load_distribute.extract_qualys(
        try_extract_max_count=etld_lib_config.was_try_extract_max_count,
        url=url,
        headers=headers,
        payload=payload,
        http_conn_timeout=etld_lib_config.was_http_conn_timeout,
        chunk_size_calc=etld_lib_config.was_chunk_size_calc,
        output_file=json_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_dict,
        multi_proc_batch_number=batch_number_str,
        extract_validation_type='json',
        compression_method=etld_lib_config.was_open_file_compression_method)
    end_msg_was_extract(function_name='was_webapp_extract')


def was_finding_extract(batch_number_str, qualys_headers_dict, cred_dict, file_info_dict,
                        last_id=0, page_size=25):

    start_msg_was_extract(function_name='was_finding_extract')
    payload = '{"ServiceRequest": {' \
              '"preferences": {"limitResults": ' \
              f'"{page_size}"' \
              ', "verbose": "true"}, ' \
              '"filters": {' '"Criteria": ' \
              '{"field": "id", "operator": "GREATER", "value": ' \
              f'"{last_id}"' + '}}}}'

    url = f"https://{cred_dict['api_fqdn_server']}/qps/rest/3.0/search/was/finding"
    headers = {'X-Requested-With': 'qualysetl',
               'Authorization': cred_dict['authorization'],
               'Content-Type': 'application/json',
               'Accept': 'application/json',
               }

    etld_lib_functions.logger.info(f"api call     - URL:{url} - PAYLOAD:{payload}")
    json_file = Path(file_info_dict['next_file_path'])

    etld_lib_extract_transform_load_distribute.extract_qualys(
        try_extract_max_count=etld_lib_config.was_try_extract_max_count,
        url=url,
        headers=headers,
        payload=payload,
        http_conn_timeout=etld_lib_config.was_http_conn_timeout,
        chunk_size_calc=etld_lib_config.was_chunk_size_calc,
        output_file=json_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_dict,
        multi_proc_batch_number=batch_number_str,
        extract_validation_type='json',
        compression_method=etld_lib_config.was_open_file_compression_method)
    end_msg_was_extract(function_name='was_finding_extract')


def was_webapp_extract_count(batch_number_str, qualys_headers_dict, cred_dict, file_info_dict):

    url = f"https://{cred_dict['api_fqdn_server']}/qps/rest/3.0/count/was/webapp"

    headers = {'X-Requested-With': 'qualysetl',
               'Authorization': cred_dict['authorization'],
               'Content-Type': 'application/json',
               'Accept': 'application/json',
               }

    etld_lib_functions.logger.info(f"api call     - {url}")
    json_file = Path(file_info_dict['next_file_path'])

    etld_lib_extract_transform_load_distribute.extract_qualys(
        try_extract_max_count=etld_lib_config.was_try_extract_max_count,
        url=url,
        headers=headers,
        payload={},
        http_conn_timeout=etld_lib_config.was_http_conn_timeout,
        chunk_size_calc=etld_lib_config.was_chunk_size_calc,
        output_file=json_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_dict,
        multi_proc_batch_number=batch_number_str,
        extract_validation_type='json')

    was_log_count(json_file=json_file, count_type='was_webapp')


def was_finding_extract_count(batch_number_str, qualys_headers_dict, cred_dict, file_info_dict):

    url = f"https://{cred_dict['api_fqdn_server']}/qps/rest/3.0/count/was/finding"

    headers = {'X-Requested-With': 'qualysetl',
               'Authorization': cred_dict['authorization'],
               'Content-Type': 'application/json',
               'Accept': 'application/json',
               }

    etld_lib_functions.logger.info(f"api call     - {url}")

    json_file = Path(file_info_dict['next_file_path'])

    etld_lib_extract_transform_load_distribute.extract_qualys(
        try_extract_max_count=etld_lib_config.was_try_extract_max_count,
        url=url,
        headers=headers,
        payload={},
        http_conn_timeout=etld_lib_config.was_http_conn_timeout,
        chunk_size_calc=etld_lib_config.was_chunk_size_calc,
        output_file=json_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_dict,
        multi_proc_batch_number=batch_number_str,
        extract_validation_type='json')

    was_log_count(json_file=json_file, count_type='was_finding')


def was_log_count(json_file, count_type='was_webapp'):
    try:
        # {"ServiceResponse":{"count":139,"responseCode":"SUCCESS"}}
        with etld_lib_config.was_open_file_compression_method(str(json_file), "rt", encoding='utf-8') as read_file:
            my_count_service_response = json.load(read_file)
            if 'ServiceResponse' in my_count_service_response.keys():
                my_count = my_count_service_response['ServiceResponse']
                if "responseCode" in my_count.keys():
                    if my_count['responseCode'] == 'SUCCESS':
                        etld_lib_functions.logger.info(f"{count_type} count: {my_count['count']}")
                    else:
                        raise Exception(f"{count_type} failed, responseCode: {my_count_service_response},"
                                        f" responseMessage: {my_count_service_response}")
                else:
                    raise Exception(f"{count_type} failed, responseCode: {my_count_service_response},"
                                    f" responseMessage: {my_count_service_response}")
            else:
                raise Exception(f"{count_type} failed, responseCode: {my_count_service_response},"
                                f" responseMessage: {my_count_service_response}")

    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"{count_type} failed, responseCode: {my_count_service_response},")
        etld_lib_functions.logger.error(f"Potential JSON File corruption or api error detected: {json_file}")
        raise Exception("WAS Application Count Failed.")


def start_msg_was_extract(function_name=""):
    etld_lib_functions.logger.info(f"start {function_name}")


def end_msg_was_extract(function_name=""):
    etld_lib_functions.logger.info(f"end {function_name}")


def main(args=None):
    was_webapp_extract()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='was_webapp_extract')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()



