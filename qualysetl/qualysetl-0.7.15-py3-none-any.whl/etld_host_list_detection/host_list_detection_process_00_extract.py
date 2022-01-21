import requests
import re
from pathlib import Path
import time
from qualys_etl.etld_lib import etld_lib_credentials as etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_extract_transform_load_distribute as etld_lib_extract_transform_load_distribute

global xml_file
global url
global multi_proc_host_ids
global multi_proc_batch_number
global xml_file_utc_run_datetime
global qualys_headers_multi_proc_dict


def host_list_detection_extract():
    global xml_file
    global url
    global multi_proc_host_ids
    global multi_proc_batch_number
    global xml_file_utc_run_datetime
    global qualys_headers_multi_proc_dict

    cred_dict = etld_lib_credentials.get_cred()
    authorization = cred_dict['authorization']  # Base64 user:password
    use_cookie = etld_lib_credentials.use_cookie  # If true, use cookie auth
    url = f"https://{cred_dict['api_fqdn_server']}/api/2.0/fo/asset/host/vm/detection/"

    payload_id_list = ",".join(multi_proc_host_ids)
    payload = {'action': 'list',
               'show_asset_id': '1',
               'show_reopened_info': '1',
               'show_tags': '0',
               'show_results': '1',
               'show_igs': '1',
               'status': 'Active,New,Re-Opened,Fixed',
               'arf_kernel_filter': '1',
               'arf_service_filter': '0',
               'arf_config_filter': '0',
               'include_ignored': '1',
               'include_disabled': '1',
               'truncation_limit': '0',
               'ids': payload_id_list}

    if use_cookie is False:
        headers = {'X-Requested-With': 'qualysetl', 'Authorization': authorization}
    else:
        headers = {'X-Requested-With': 'qualysetl', 'Cookie': etld_lib_credentials.cookie_file()}

    print_payload = payload.copy()
    print_payload['ids'] = "TRUNCATED FOR LOG"
    etld_lib_functions.logger.info(f"api call     - {url}")
    etld_lib_functions.logger.info(f"api options  - {print_payload}")
    etld_lib_functions.logger.info(f"api cookie   - {use_cookie}")

    xml_file_prefix = re.sub("_rename_me_to_batch.xml", "", str(etld_lib_config.host_list_detection_xml_file))
    xml_batch_vm_processed_after = re.sub(':', '_', f"{etld_lib_config.host_list_detection_vm_processed_after}")
    xml_file_utc_run_datetime_filename = re.sub(':', '_', f"{xml_file_utc_run_datetime}")
    xml_file_name = f'{Path(xml_file_prefix).name}_utc_run_datetime_{xml_file_utc_run_datetime_filename}_utc_vm_processed_after_{xml_batch_vm_processed_after}_{multi_proc_batch_number}.xml'
    xml_file = Path(etld_lib_config.host_list_detection_xml_dir, xml_file_name)

    chunk_size_calc = 20480
    try_extract_max_count = 30
    http_conn_timeout = 300
    etld_lib_extract_transform_load_distribute.extract_qualys(
        try_extract_max_count=try_extract_max_count,
        url=url,
        headers=headers,
        payload=payload,
        http_conn_timeout=http_conn_timeout,
        chunk_size_calc=chunk_size_calc,
        output_file=xml_file,
        cred_dict=cred_dict,
        qualys_headers_dict=qualys_headers_multi_proc_dict,
        multi_proc_batch_number=multi_proc_batch_number)


def get_qualys_limits_from_host_list_detection():
    global xml_file
    global url
    global multi_proc_host_ids
    global multi_proc_batch_number
    global xml_file_utc_run_datetime
    global qualys_headers_multi_proc_dict
    etld_lib_credentials.main()
    cred_dict = etld_lib_credentials.get_cred()
    authorization = cred_dict['authorization']  # Base64 user:password
    use_cookie = etld_lib_credentials.use_cookie  # If true, use cookie auth
    url = f"https://{cred_dict['api_fqdn_server']}/api/2.0/fo/asset/host/vm/detection/"

    payload = {'action': 'list',
               'truncation_limit': '1',
               }

    if use_cookie is False:
        headers = {'X-Requested-With': 'qualysetl', 'Authorization': authorization}
    else:
        headers = {'X-Requested-With': 'qualysetl', 'Cookie': etld_lib_credentials.get_cookie(update_cookie=False)}

    xml_file = Path("/dev/null")
    chunk_size_calc = 20480
    try_extract_max_count = 5
    http_conn_timeout = 30
    multi_proc_batch_number = "check_headers"
    etld_lib_extract_transform_load_distribute.extract_qualys(
        try_extract_max_count=try_extract_max_count,
        url=url,
        headers=headers,
        payload=payload,
        http_conn_timeout=http_conn_timeout,
        chunk_size_calc=chunk_size_calc,
        output_file=xml_file,
        cred_dict=cred_dict,
        qualys_headers_dict=qualys_headers_multi_proc_dict,
        multi_proc_batch_number=multi_proc_batch_number)


def start_msg_host_list_detection_extract():
    etld_lib_functions.logger.info(f"start")


def end_msg_host_list_detection_extract():
    global url
    global xml_file
    global xml_file_utc_run_datetime
    etld_lib_functions.log_file_info(url, 'in')
    etld_lib_functions.logger.info(f"Run Date: {xml_file_utc_run_datetime}")
    etld_lib_functions.log_file_info(xml_file)
    etld_lib_functions.logger.info(f"end")


def main(args=None):
    start_msg_host_list_detection_extract()
    etld_lib_credentials.main()
    host_list_detection_extract()
    end_msg_host_list_detection_extract()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_extract')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()



