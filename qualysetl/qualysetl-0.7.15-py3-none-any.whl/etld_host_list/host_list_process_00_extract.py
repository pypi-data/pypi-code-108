import requests
import re
import time
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_credentials as etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_extract_transform_load_distribute as etld_lib_extract_transform_load_distribute
from qualys_etl.etld_lib import etld_lib_sqlite_tables as etld_lib_sqlite_tables
global xml_files
global url
global payload_list
global qualys_headers
global host_list_vm_processed_after
global xml_file


def remove_old_files():
    try:
        if Path(etld_lib_config.host_list_sqlite_file).is_file():
            etld_lib_functions.logger.info(f"Removing old sqlite file: {etld_lib_config.host_list_sqlite_file}")
            Path(etld_lib_config.host_list_sqlite_file).unlink()
        if Path(etld_lib_config.host_list_shelve_file).is_file():
            etld_lib_functions.logger.info(f"Removing old shelve file: {etld_lib_config.host_list_shelve_file}")
            Path(etld_lib_config.host_list_shelve_file).unlink()
        if Path(etld_lib_config.host_list_json_file).is_file():
            etld_lib_functions.logger.info(f"Removing old json file: {etld_lib_config.host_list_json_file}")
            Path(etld_lib_config.host_list_json_file).unlink()
        if Path(etld_lib_config.host_list_csv_file).is_file():
            etld_lib_functions.logger.info(f"Removing old csv file: {etld_lib_config.host_list_csv_file}")
            Path(etld_lib_config.host_list_csv_file).unlink()
    except Exception as e:
        etld_lib_functions.logger.error(f"{e}")
        exit(1)


def host_list_extract():
    global xml_files
    global url
    global payload_list
    global qualys_headers

    payload_list = []
    vm_processed_after = etld_lib_config.host_list_vm_processed_after  # UTC Date or 0 for all
    host_list_payload_option = etld_lib_config.host_list_payload_option  # notags or tags to used tag list
    if etld_lib_config.host_list_show_tags == '0':
        show_tags = '0'
    else:
        show_tags = '1'

    cred_dict = etld_lib_credentials.get_cred()
    authorization = cred_dict['authorization']  # Base64 user:password
    use_cookie = etld_lib_credentials.use_cookie  # If true, use cookie auth
    url = f"https://{cred_dict['api_fqdn_server']}/api/2.0/fo/asset/host/"  # Qualys Endpoint
    xml_files = {'host_list_other_xml_file': etld_lib_config.host_list_other_xml_file}

#    if host_list_payload_option == 'notags':
#        provider_list = ['notags']
#        xml_files = {'host_list_other_xml_file': etld_lib_config.host_list_other_xml_file }
#    else:
#        provider_list = ['ec2', 'gcp', 'azure', 'other']
#        xml_files = {'host_list_other_xml_file': etld_lib_config.host_list_other_xml_file,
#                     'host_list_ec2_xml_file': etld_lib_config.host_list_ec2_xml_file,
#                     'host_list_gcp_xml_file': etld_lib_config.host_list_gcp_xml_file,
#                     'host_list_azure_xml_file': etld_lib_config.host_list_azure_xml_file
#                     }


    # for provider in provider_list:
    #     if provider == 'notags':
    #         payload = {'action': 'list',
    #                    'details': 'All',
    #                    'truncation_limit': '0',
    #                    'show_tags': f"{show_tags}",
    #                    'show_asset_id': '1',
    #                    }
    #         xml_file = xml_files[f"host_list_other_xml_file"]
    #     else:
    #         xml_file = xml_files[f"host_list_{provider}_xml_file"]
    #         payload = {'action': 'list',
    #                    'details': 'All',
    #                    'use_tags': '1',
    #                    'truncation_limit': '0',
    #                    'tag_set_by': 'name',
    #                    'show_cloud_tags': '1',
    #                    'show_tags': f"{show_tags}",
    #                    'show_asset_id': '1',
    #                  }

        # if provider in ('ec2', 'gcp', 'azure'):
        #     payload['host_metadata'] = provider.replace('gcp', 'google')  # adjust if gcp to google for option
        #     payload['tag_set_include'] = 'qetl-all-' + provider   # ec2-all or gcp-all or azure-all
        # elif provider in 'notags':
        #     pass
        # elif provider in 'other':
        #     payload['tag_set_include'] = "qetl-all-hosts"
        #     payload['tag_set_exclude'] = "qetl-all-ec2,qetl-all-gcp,qetl-all-azure"

#        if vm_processed_after != "0":  # Set vm_processed_after to 0 get all assets scanned or un-scanned.
#            payload['vm_processed_after'] = vm_processed_after

    payload = {'action': 'list',
               'details': 'All',
               'truncation_limit': '0',
               'show_tags': f"{show_tags}",
               'show_cloud_tags': '1',
               'show_asset_id': '1',
               'host_metadata': 'all',
               }
    host_xml_file = xml_files[f"host_list_other_xml_file"]
    # provider = 'notags'
    if not str(vm_processed_after).__contains__("1970"):  # Set to 1970 to remove vm_processed_after and process alldata
        payload['vm_processed_after'] = vm_processed_after

    if use_cookie is False:
        headers = {'X-Requested-With': 'qualysetl', 'Authorization': authorization}
    else:
        headers = {'X-Requested-With': 'qualysetl', 'Cookie': etld_lib_credentials.get_cookie(update_cookie=True)}

    # etld_lib_functions.logger.info(f"provider     - {provider}")

    etld_lib_functions.logger.info(f"api call     - {url}")
    etld_lib_functions.logger.info(f"api options  - {payload}")
    etld_lib_functions.logger.info(f"api cookie   - {use_cookie}")

    payload_list.append(payload)
    # TODO: build payload_list in separate method from requests so options can be adjusted.

    chunk_size_calc = 20480
    try_extract_max_count = 30
    http_conn_timeout = 300  #
    qualys_headers = {}
    multi_proc_batch_number = None
    etld_lib_extract_transform_load_distribute.extract_qualys(
        try_extract_max_count=try_extract_max_count,
        url=url,
        headers=headers,
        payload=payload,
        http_conn_timeout=http_conn_timeout,
        chunk_size_calc=chunk_size_calc,
        output_file=host_xml_file,
        cred_dict=cred_dict,
        qualys_headers_dict=qualys_headers,
        multi_proc_batch_number=multi_proc_batch_number)


def start_msg_host_list_extract():
    etld_lib_functions.logger.info(f"start ")


def end_msg_host_list_extract():
    global url
    global xml_files
    global qualys_headers
    etld_lib_functions.log_file_info(url, 'in')
    for of in xml_files.values():
        of_file = Path(of)
        if of_file.exists():
            etld_lib_functions.log_file_info(of_file)
    for h in qualys_headers.keys():
        etld_lib_functions.logger.info(f"Qualys Header: {h} = {qualys_headers[h]}")

    etld_lib_functions.logger.info(f"end")


def main():
    start_msg_host_list_extract()
    # remove_old_files() Hold off on removing old files for restart.
    host_list_extract()
    end_msg_host_list_extract()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_extract')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()



