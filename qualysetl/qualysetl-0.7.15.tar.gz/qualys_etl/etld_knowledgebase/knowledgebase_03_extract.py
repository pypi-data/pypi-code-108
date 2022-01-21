#!/usr/bin/env python3
import re
from pathlib import Path

from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_sqlite_tables
from qualys_etl.etld_lib import etld_lib_extract_transform_load
from qualys_etl.etld_lib import etld_lib_datetime


def get_table_columns(database_file=None, table_name=None):
    sqlite_obj = etld_lib_sqlite_tables.SqliteObj(sqlite_file=database_file, read_only=True)
    table_columns = sqlite_obj.get_table_columns(table_name=table_name)
    sqlite_obj.close_connection()
    return table_columns


def get_min_max_dates(database_file, table_name, column_name):
    sqlite_obj = etld_lib_sqlite_tables.SqliteObj(str(database_file), read_only=True)
    min_max_date_dict = sqlite_obj.get_min_max_dates_from_table_column(table_name=table_name, column_name=column_name)
    sqlite_obj.close_connection()
    return min_max_date_dict


def setup_kb_last_modified_after():
    if Path(etld_lib_config.kb_sqlite_file).exists():
        table_columns = get_table_columns(database_file=etld_lib_config.kb_sqlite_file,
                                          table_name=etld_lib_config.kb_table_name)
        table_columns_definition = etld_lib_config.kb_csv_columns()
        table_columns_definition.append('Row_Last_Updated')
        if table_columns != table_columns_definition:
            # Rebuild tables/data
            etld_lib_config.kb_last_modified_after = '1970-01-01T00:00:00Z'

        min_max_date_dict = get_min_max_dates(
            database_file=etld_lib_config.kb_sqlite_file,
            table_name=etld_lib_config.kb_table_name,
            column_name='LAST_SERVICE_MODIFICATION_DATETIME')
    else:
        etld_lib_config.kb_last_modified_after = '1970-01-01T00:00:00Z'
        # First time build.

    if str(etld_lib_config.kb_last_modified_after).__contains__("1970"):
        etld_lib_functions.logger.info(f"rebuilding knowledgebase...")
        etld_lib_functions.logger.info(f"     using kb_last_modified_after=1970-01-01T00:00:00Z")
        etld_lib_config.kb_last_modified_after = '1970-01-01T00:00:00Z'
    elif str(etld_lib_config.kb_last_modified_after).startswith("20"):
        etld_lib_functions.logger.info(f"updating knowledgebase...")
        etld_lib_functions.logger.info(f"     using kb_last_modified_after={etld_lib_config.kb_last_modified_after}")
    elif str(min_max_date_dict['min_date']).__contains__("1999"):
        etld_lib_config.kb_last_modified_after = re.sub(" .*$", "T00:00:00Z", min_max_date_dict['max_date'])
        etld_lib_functions.logger.info(f"Found knowledgebase max date of: {min_max_date_dict['max_date']}")
        etld_lib_functions.logger.info(f"     using kb_last_modified_after={etld_lib_config.kb_last_modified_after}")
    else:
        etld_lib_functions.logger.info(f"Did not find full knowledgebase, rebuilding...")
        etld_lib_functions.logger.info(f"     using kb_last_modified_after=1970-01-01T00:00:00Z")
        etld_lib_config.kb_last_modified_after = '1970-01-01T00:00:00Z'


def knowledgebase_extract():

    cred_dict = etld_lib_credentials.get_cred()
    authorization = cred_dict['authorization']
    url = f"https://{cred_dict['api_fqdn_server']}/api/2.0/fo/knowledge_base/vuln/"

    payload = etld_lib_config.kb_payload_option
    payload['last_modified_after'] = etld_lib_config.kb_last_modified_after

    etld_lib_functions.logger.info(f"api call    - {url}")
    etld_lib_functions.logger.info(f"api options - {payload}")

    headers = {'X-Requested-With': 'qualysetl', 'Authorization': authorization}
    utc_datetime = etld_lib_datetime.get_utc_datetime_qualys_format()
    file_info_dict = \
        etld_lib_config.prepare_extract_batch_file_name(
            next_batch_number_str="batch_000001",
            next_batch_date=utc_datetime,
            extract_dir=etld_lib_config.kb_extract_dir,
            file_name_type="kb",
            file_name_option="last_modified_after",
            file_name_option_date=etld_lib_config.kb_last_modified_after,
            compression_method=etld_lib_config.kb_open_file_compression_method
        )
    kb_xml_file = file_info_dict['next_file_path']

    qualys_headers = {}
    multi_proc_batch_number = None
    etld_lib_extract_transform_load.extract_qualys(
        try_extract_max_count=etld_lib_config.kb_try_extract_max_count,
        url=url,
        headers=headers,
        payload=payload,
        http_conn_timeout=etld_lib_config.kb_http_conn_timeout,
        chunk_size_calc=etld_lib_config.kb_chunk_size_calc,
        output_file=kb_xml_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers,
        multi_proc_batch_number=multi_proc_batch_number,
        compression_method=etld_lib_config.kb_open_file_compression_method)

    etld_lib_extract_transform_load.transform_xml_file_to_json_file(
        xml_file=kb_xml_file,
        compression_method=etld_lib_config.kb_open_file_compression_method,
        logger_method=etld_lib_functions.logger.info)


    for h in qualys_headers.keys():
        etld_lib_functions.logger.info(f"Qualys Header: {h} = {qualys_headers[h]}")


def start_msg_knowledgebase_extract():
    etld_lib_functions.logger.info(f"start")


def end_msg_knowledgebase_extract():
    etld_lib_functions.logger.info(f"end")


def main():
    start_msg_knowledgebase_extract()
    setup_kb_last_modified_after()
    etld_lib_config.remove_old_files(
        dir_path=etld_lib_config.kb_extract_dir,
        dir_search_glob=etld_lib_config.kb_extract_dir_file_search_blob,
        other_files_list=etld_lib_config.kb_data_files,
        other_files_list_exclusions=[etld_lib_config.kb_sqlite_file]
        )
    knowledgebase_extract()
    end_msg_knowledgebase_extract()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='knowledgebase_extract')
    etld_lib_config.main()
    etld_lib_credentials.main()
    main()
