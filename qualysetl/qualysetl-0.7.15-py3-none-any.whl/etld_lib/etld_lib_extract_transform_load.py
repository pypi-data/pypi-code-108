import json
import xmltodict
import requests
import time
import dbm.gnu
import pickle
import re
import gzip
import qualys_etl
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables
from qualys_etl.etld_lib import etld_lib_test_system
global http_error_codes_v2_api


http_error_codes_v2_api = {
    "202": "Retry Later Duplicate Operation.",
    "400": "Bad Request Unrecognized parameter",
    "401": "Unauthorized check credentials",
    "403": "Forbidden User account is inactive or user license not authorized for API. ",
    "409": "Conflict Check Concurrency and Rate Limits",
    "501": "Internal Error. Contact your TAM to open ticket. ",
    "503": "Maintenance we are performing scheduled maintenance on our system.",
}


def get_qualys_headers(request=None):
    # 'X-Powered-By': 'Qualys:USPOD1:a6df6808-8c45-eb8c-e040-10ac13041e17:9e42af6e-c5a2-4d9e-825c-449440445cc8'
    # 'X-RateLimit-Limit': '2000'
    # 'X-RateLimit-Window-Sec': '3600'
    # 'X-Concurrency-Limit-Limit': '10'
    # 'X-Concurrency-Limit-Running': '0'
    # 'X-RateLimit-ToWait-Sec': '0'
    # 'X-RateLimit-Remaining': '1999'
    # 'Keep-Alive': 'timeout=300, max=250'
    # 'Connection': 'Keep-Alive'
    # 'Transfer-Encoding': 'chunked'
    # 'Content-Type': 'application/xml'
    if request is None:
        pass
    else:
        request_url = request.url
        url_fqdn = re.sub("(https://)([0-9a-zA-Z\.\_\-]+)(/.*$)", "\g<2>", request_url)
        url_end_point = re.sub("(https://[0-9a-zA-Z\.\_\-]+)/", "", request_url)
        headers = {}
        if 'X-RateLimit-Limit' in request.headers.keys():
            x_ratelimit_limit = request.headers['X-RateLimit-Limit']
            headers['x_ratelimit_limit'] = x_ratelimit_limit

        if 'X-RateLimit-Window-Sec' in request.headers.keys():
            x_ratelimit_window_sec = request.headers['X-RateLimit-Window-Sec']
            headers['x_ratelimit_window_sec'] = x_ratelimit_window_sec

        if 'X-RateLimit-ToWait-Sec' in request.headers.keys():
            x_ratelimit_towait_sec = request.headers['X-RateLimit-ToWait-Sec']
            headers['x_ratelimit_towait-sec'] = x_ratelimit_towait_sec

        if 'X-RateLimit-Remaining' in request.headers.keys():
            x_ratelimit_remaining = request.headers['X-RateLimit-Remaining']
            headers['x_ratelimit_remaining'] = x_ratelimit_remaining

        if 'X-Concurrency-Limit-Limit' in request.headers.keys():
            x_concurrency_limit_limit = request.headers['X-Concurrency-Limit-Limit']
            headers['x_concurrency_limit_limit'] = x_concurrency_limit_limit

        if 'X-Concurrency-Limit-Running' in request.headers.keys():
            x_concurrency_limit_running = request.headers['X-Concurrency-Limit-Running']
            headers['x_concurrency_limit_running'] = x_concurrency_limit_running

        headers['url'] = request_url
        headers['api_fqdn_server'] = url_fqdn
        headers['api_end_point'] = url_end_point

        return headers


def get_http_error_code_message_v2_api(http_error=""):
    global http_error_codes_v2_api

    if http_error in http_error_codes_v2_api.keys():
        return http_error_codes_v2_api[http_error]
    else:
        return None


def get_from_qualys_extract_filename_batch_date_and_batch_number_dict(qualys_extract_file_path: Path) -> dict:
    # Format of qualys_extract_filename
    # host_list_utc_run_datetime_2021-12-24T12:33:16Z_utc_vm_processed_after_1970-01-01T00:00:00Z_batch_000028.xml
    # host_list_detection_utc_run_datetime_2021-12-06T19_59_01Z_utc_vm_processed_after_1970-01-01T00_00_00Z_batch_000288.xml
    # asset_inventory_utc_run_datetime_2021-12-22T08_51_18Z_utc_assetLastUpdated_1970-01-01T00_00_00Z_batch_000908.json
    batch_info = \
        str(re.sub("(^.*datetime_)(20..-..-..)(T)(..:..:..)(Z_utc_.*_batch_)(.*)(.json$|.xml$|.json.gz$|.xml.gz$)",
                   "\g<2> \g<4>,\g<6>",
                   str(qualys_extract_file_path))).split(",")
    batch_dict = {'batch_date': batch_info[0], 'batch_number': batch_info[1]}
    return batch_dict


def get_batch_date_from_filename(file_name):
    batch_dict = \
        get_from_qualys_extract_filename_batch_date_and_batch_number_dict(file_name)
    return batch_dict['batch_date']


def get_batch_number_from_filename(file_name):
    batch_dict = \
        get_from_qualys_extract_filename_batch_date_and_batch_number_dict(file_name)
    return batch_dict['batch_number']


def get_batch_name_from_filename(file_name):
    batch_name = re.sub("(^.*)(batch_[0-9]+)(\..*$)", "\g<2>", Path(file_name).name)
    return batch_name


def load_files_into_sqlite_via_multiprocessing_queue(
        queue_of_file_paths,
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        insert_xml_file_into_sqlite_method=None,
        counter_obj=None):

    def get_next_file_in_queue(bookend, queue_file_path):
        time.sleep(2)
        queue_data = queue_file_path.get()
        if queue_data == bookend:
            etld_lib_functions.logger.info(f"Found {bookend} of Queue.")
            queue_data = bookend
        return queue_data

    file_path = get_next_file_in_queue('BEGIN', queue_of_file_paths)
    if file_path == 'BEGIN':
        while True:
            file_path = get_next_file_in_queue('END', queue_of_file_paths)
            if file_path == 'END':
                break
            batch_number = get_batch_number_from_filename(file_path)
            etld_lib_functions.logger.info(f"Received batch file in Queue: {batch_number}")
            insert_xml_file_into_sqlite_method(file_path, sqlite_obj, counter_obj)
            etld_lib_functions.logger.info(f"Committed batch file in Queue to Database: {batch_number}")
    else:
        etld_lib_functions.logger.error(f"Invalid begin of Queue, {file_path}.  Please restart.")
        exit(1)


def load_files_into_sqlite_via_directory_listing(sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
                                                 table_name: str,
                                                 extract_dir,
                                                 extract_dir_file_search_blob,
                                                 counter_obj,
                                                 compression_method=open,
                                                 insert_xml_file_into_sqlite_method=None):
    xml_file_list = []
    for file_name in sorted(Path(extract_dir).glob(extract_dir_file_search_blob)):
        if str(file_name).endswith('.xml') or str(file_name).endswith('.xml.gz'):
            xml_file_list.append(file_name)
    for xml_file_path in xml_file_list:
        insert_xml_file_into_sqlite_method(xml_file_path, sqlite_obj, table_name, compression_method, counter_obj)
        etld_lib_functions.log_file_info(xml_file_path)


def transform_xml_file_to_json_file(xml_file: Path, compression_method=open, logger_method=print):
    json_file = Path(str(xml_file).replace('.xml', '.json'))
    logger_method(f"Begin transform_xml_file_to_json {xml_file.name} to {json_file.name}")
    with compression_method(
            json_file, 'wt', encoding='utf-8') as json_file_fd, \
            compression_method(
                xml_file, 'rt', encoding='utf-8') as xml_file_fd:
        json.dump(xmltodict.parse(xml_file_fd.read()), json_file_fd)
    logger_method(f"End   transform_xml_file_to_json {xml_file.name} to {json_file.name}")


def load_json(load_json_file=None, shelve_db=None):
    counter = 0
    count_json_obj_written = \
        etld_lib_functions.DisplayCounterToLog(display_counter_at=10000,
                                               logger_func=etld_lib_functions.logger.info,
                                               display_counter_log_message="count json records written")
    try:
        with open(load_json_file, "w", encoding='utf-8') as output_json_file:
            output_json_file.write("[")
            with dbm.gnu.open(str(shelve_db), 'rf') as shelve_database:
                shelve_key = shelve_database.firstkey()
                count_key_value_pairs_loaded_to_json = 0
                shelve_length = len(shelve_database)
                keys_max_count_added_to_json = 0
                while shelve_key is not None:
                    shelve_data = pickle.loads(shelve_database[shelve_key])
                    json.dump(shelve_data, output_json_file, indent=4)
                    keys_max_count_added_to_json = keys_max_count_added_to_json + 1
                    count_key_value_pairs_loaded_to_json = count_key_value_pairs_loaded_to_json + 1
                    if keys_max_count_added_to_json > shelve_length:
                        break
                    else:
                        output_json_file.write(",")
                        count_json_obj_written.display_counter_to_log()
                        counter += 1
                    shelve_key = shelve_database.nextkey(shelve_key)

            output_json_file.write("]")
        count_json_obj_written.display_final_counter_to_log()

    except Exception as e:
        etld_lib_functions.logger.error(f"Error in File: {__file__} Line: {etld_lib_functions.lineno()}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)
    return count_key_value_pairs_loaded_to_json


def extract_validation(validation_type='xml', output_file_to_validate=None, compression_method=open):
    # TODO Add Logic to validate xml and json
    if 'xml' in validation_type:
        etld_lib_test_system.validate_xml_is_closed_properly(
            open_file_method=compression_method, file_path=Path(output_file_to_validate))
    elif 'json' in validation_type:
        etld_lib_test_system.validate_json_file(
            open_file_method=compression_method, file_path=Path(output_file_to_validate))


def extract_qualys(
        try_extract_max_count=30,
        url=None,
        headers=None,
        payload=None,
        http_conn_timeout=300,
        chunk_size_calc=10240,
        output_file=None,
        cred_dict=None,
        qualys_headers_multiprocessing_dict=None,
        multi_proc_batch_number=None,
        extract_validation_type='xml',
        requests_module_tls_verify_status=True,
        compression_method=gzip.open
):
    for _ in range(try_extract_max_count):
        try:
            headers['User-Agent'] = f"qualysetl_v{qualys_etl.__version__}"
            with requests.request("POST", url, stream=True, headers=headers, data=payload,
                                  timeout=http_conn_timeout, verify=requests_module_tls_verify_status) as r:
                qualys_headers = get_qualys_headers(r)
                if multi_proc_batch_number is None:
                    qualys_headers_multiprocessing_dict['batch_000001'] = get_qualys_headers(r)
                else:
                    qualys_headers_multiprocessing_dict[multi_proc_batch_number] = get_qualys_headers(r)

                etld_lib_functions.logger.info(f"Qualys Headers: {qualys_headers}")
                if r.status_code == 200:
                    with compression_method(output_file, "wb") as f:
                        for chunk in r.iter_content(chunk_size=chunk_size_calc):
                            f.write(chunk)

                    if 'qetl' not in str(output_file):
                        pass  # don't validate temp files outside of qetl paths.
                    else:
                        extract_validation(validation_type=extract_validation_type, output_file_to_validate=output_file,
                                           compression_method=compression_method)
                elif r.status_code == 409 or r.status_code == 202 or r.status_code == 500:
                    # Concurrency Issue, Duplication Operation, Temporary Service Issue.
                    message = get_http_error_code_message_v2_api(str(r.status_code))
                    etld_lib_functions.logger.warning(f"HTTP USER: {cred_dict['username']} url: {url}")
                    raise Exception(f"HTTP Status is: {r.status_code}, message: {message}")
                else:
                    message = get_http_error_code_message_v2_api(str(r.status_code))
                    etld_lib_functions.logger.error(f"HTTP USER: {cred_dict['username']} url: {url}")
                    etld_lib_functions.logger.error(f"HTTP {r.status_code}, exiting. message={message}")
                    exit(1)
        except Exception as e:
            time_sleep = 300
            etld_lib_functions.logger.warning(f"Warning for extract file: {Path(output_file).name}")
            etld_lib_functions.logger.warning(f"Warning {e}")
            etld_lib_functions.logger.warning(f"Sleeping for {time_sleep} seconds before next retry.")
            etld_lib_functions.logger.warning(f"Retry attempt number: {_ + 1} of max retry: {try_extract_max_count}")
            time.sleep(time_sleep)
            continue
        else:
            break  # success
    else:
        etld_lib_functions.logger.error(f"Max retries attempted: {try_extract_max_count}")
        etld_lib_functions.logger.error(f"extract file: {Path(output_file).name}")
        exit(1)

