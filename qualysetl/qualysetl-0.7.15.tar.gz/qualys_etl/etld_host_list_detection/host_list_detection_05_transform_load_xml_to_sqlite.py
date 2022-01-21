#!/usr/bin/env python3
import xmltodict
import json
import re
import time
from multiprocessing import Process, Queue
from pathlib import Path

from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables
from qualys_etl.etld_lib import etld_lib_extract_transform_load


def create_counter_objects(database_type='sqlite'):
    counter_obj_host_list_detection_hosts = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.host_list_detection_hosts_table_name}")

    counter_obj_host_list_detection_qids = \
        etld_lib_functions.DisplayCounterToLog(
            display_counter_at=100000,
            logger_func=etld_lib_functions.logger.info,
            display_counter_log_message=f"rows added to {database_type} "
                                        f"table {etld_lib_config.host_list_detection_qids_table_name}")

    counter_obj_host_list_detection_hosts_without_qids = \
        etld_lib_functions.DisplayCounterToLog(
            display_counter_at=10000,
            logger_func=etld_lib_functions.logger.info,
            display_counter_log_message=f"hosts without detection rows added to {database_type} "
                                        f"table {etld_lib_config.host_list_detection_qids_table_name}")

    counter_obj_dict_new = {
        'counter_obj_host_list_detection_hosts': counter_obj_host_list_detection_hosts,
        'counter_obj_host_list_detection_qids': counter_obj_host_list_detection_qids,
        'counter_obj_host_list_detection_hosts_without_qids': counter_obj_host_list_detection_hosts_without_qids,
    }

    return counter_obj_dict_new


def drop_and_create_all_tables(sqlite_obj):
    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_table_name,
        csv_columns=etld_lib_config.host_list_csv_columns(),
        csv_column_types=etld_lib_config.host_list_csv_column_types(),
        key='ID')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_detection_q_knowledgebase_in_host_list_detection,
        csv_columns=etld_lib_config.kb_csv_columns(),
        csv_column_types=etld_lib_config.kb_csv_column_types(),
        key='QID')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_detection_hosts_table_name,
        csv_columns=etld_lib_config.host_list_detection_host_csv_columns(),
        csv_column_types=etld_lib_config.host_list_detection_host_csv_column_types(),
        key='ID')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_detection_qids_table_name,
        csv_columns=etld_lib_config.host_list_detection_qids_csv_columns(),
        csv_column_types=etld_lib_config.host_list_detection_qids_csv_column_types(),
    )

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_detection_status_table_name,
        csv_columns=etld_lib_config.status_table_csv_columns(),
        csv_column_types=etld_lib_config.status_table_csv_column_types(),
        key='STATUS_NAME')

    sqlite_obj.execute_statement(f"DROP VIEW IF EXISTS {etld_lib_config.host_list_detection_table_view_name}")
    create_view_statement = \
        '''CREATE VIEW Q_Host_List_Detection as 
    select A.ID HL_ID, A.ASSET_ID HL_ASSET_ID, A.IP HL_IP, A.IPV6 HL_IPV6, A.TRACKING_METHOD HL_TRACKING_METHOD, 
    A.NETWORK_ID HL_NETWORK_ID, A.DNS HL_DNS, A.DNS_DATA HL_DNS_DATA, A.CLOUD_PROVIDER HL_CLOUD_PROVIDER, 
    A.CLOUD_SERVICE HL_CLOUD_SERVICE, A.CLOUD_RESOURCE_ID HL_CLOUD_RESOURCE_ID, 
    A.EC2_INSTANCE_ID HL_EC2_INSTANCE_ID, A.NETBIOS HL_NETBIOS, A.OS HL_OS, A.QG_HOSTID HL_QG_HOSTID, 
    A.TAGS HL_TAGS, A.METADATA HL_METADATA, A.CLOUD_PROVIDER_TAGS HL_CLOUD_PROVIDER_TAGS, 
    A.LAST_VULN_SCAN_DATETIME HL_LAST_VULN_SCAN_DATETIME, A.LAST_VM_SCANNED_DATE HL_LAST_VM_SCANNED_DATE, 
    A.LAST_VM_SCANNED_DURATION HL_LAST_VM_SCANNED_DURATION, 
    A.LAST_VM_AUTH_SCANNED_DATE HL_LAST_VM_AUTH_SCANNED_DATE, 
    A.LAST_VM_AUTH_SCANNED_DURATION HL_LAST_VM_AUTH_SCANNED_DURATION, 
    A.LAST_COMPLIANCE_SCAN_DATETIME HL_LAST_COMPLIANCE_SCAN_DATETIME, A.OWNER HL_OWNER, 
    A.COMMENTS HL_COMMENTS, A.USER_DEF HL_USER_DEF, A.ASSET_GROUP_IDS HL_ASSET_GROUP_IDS, 
    A.BATCH_DATE HL_BATCH_DATE, A.BATCH_NUMBER HL_BATCH_NUMBER, A.Row_Last_Updated HL_Row_Last_Updated, 
    B.ID HLDH_ID, B.ASSET_ID HLDH_ASSET_ID, B.IP HLDH_IP, B.IPV6 HLDH_IPV6, B.TRACKING_METHOD HLDH_TRACKING_METHOD, 
    B.NETWORK_ID HLDH_NETWORK_ID, B.OS HLDH_OS, B.OS_CPE HLDH_OS_CPE, B.DNS HLDH_DNS, B.DNS_DATA HLDH_DNS_DATA, 
    B.NETBIOS HLDH_NETBIOS, B.QG_HOSTID HLDH_QG_HOSTID, B.LAST_SCAN_DATETIME HLDH_LAST_SCAN_DATETIME, 
    B.LAST_VM_SCANNED_DATE HLDH_LAST_VM_SCANNED_DATE, B.LAST_VM_SCANNED_DURATION HLDH_LAST_VM_SCANNED_DURATION, 
    B.LAST_VM_AUTH_SCANNED_DATE HLDH_LAST_VM_AUTH_SCANNED_DATE, 
    B.LAST_VM_AUTH_SCANNED_DURATION HLDH_LAST_VM_AUTH_SCANNED_DURATION, 
    B.LAST_PC_SCANNED_DATE HLDH_LAST_PC_SCANNED_DATE, B.BATCH_DATE HLDH_BATCH_DATE, 
    B.BATCH_NUMBER HLDH_BATCH_NUMBER, B.Row_Last_Updated HLDH_Row_Last_Updated, 
    C.ID HLDQ_ID, C.ASSET_ID HLDQ_ASSET_ID, C.QID HLDQ_QID, C.TYPE HLDQ_TYPE, C.STATUS HLDQ_STATUS, 
    C.PORT HLDQ_PORT, C.PROTOCOL HLDQ_PROTOCOL, C.SEVERITY HLDQ_SEVERITY, C.FQDN HLDQ_FQDN, C.SSL HLDQ_SSL, 
    C.INSTANCE HLDQ_INSTANCE, C.LAST_PROCESSED_DATETIME HLDQ_LAST_PROCESSED_DATETIME, 
    C.FIRST_FOUND_DATETIME HLDQ_FIRST_FOUND_DATETIME, C.LAST_FOUND_DATETIME HLDQ_LAST_FOUND_DATETIME, 
    C.TIMES_FOUND HLDQ_TIMES_FOUND, C.LAST_TEST_DATETIME HLDQ_LAST_TEST_DATETIME, 
    C.LAST_UPDATE_DATETIME HLDQ_LAST_UPDATE_DATETIME, C.LAST_FIXED_DATETIME HLDQ_LAST_FIXED_DATETIME, 
    C.FIRST_REOPENED_DATETIME HLDQ_FIRST_REOPENED_DATETIME, C.LAST_REOPENED_DATETIME HLDQ_LAST_REOPENED_DATETIME, 
    C.TIMES_REOPENED HLDQ_TIMES_REOPENED, C.SERVICE HLDQ_SERVICE, C.IS_IGNORED HLDQ_IS_IGNORED, 
    C.IS_DISABLED HLDQ_IS_DISABLED, C.AFFECT_RUNNING_KERNEL HLDQ_AFFECT_RUNNING_KERNEL, 
    C.AFFECT_RUNNING_SERVICE HLDQ_AFFECT_RUNNING_SERVICE, 
    C.AFFECT_EXPLOITABLE_CONFIG HLDQ_AFFECT_EXPLOITABLE_CONFIG, 
    C.RESULTS HLDQ_RESULTS, 
    C.BATCH_DATE HLDQ_BATCH_DATE, 
    C.BATCH_NUMBER HLDQ_BATCH_NUMBER, 
    C.Row_Last_Updated HLDQ_Row_Last_Updated 
    from Q_Host_List A 
    left outer join Q_Host_List_Detection_HOSTS B ON A.ID = B.ID 
    left outer join Q_Host_List_Detection_QIDS C ON A.ID = C.ID'''

    sqlite_obj.execute_statement(create_view_statement)
    create_view_statement_display = create_view_statement.replace('\n', '').replace('  ', ' ')
    etld_lib_functions.logger.info(f"VIEW CREATED: {create_view_statement_display}")
    sqlite_obj.commit_changes()


def attach_database_to_host_list_detection(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj, table_name, database_as_name, database_file):
    sqlite_obj.attach_database_to_connection(database_as_name=database_as_name,
                                             database_sqlite_file=database_file)
    table_name = f"{database_as_name}.{table_name}"
    table_columns = sqlite_obj.get_table_columns(table_name=table_name)
    etld_lib_functions.logger.info(f"Found Table {table_name} columns: {table_columns}")
    return table_name, table_columns


def copy_database_table(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj, table_name, new_table_name, where_clause=""):
    try:
        etld_lib_functions.logger.info(f"Begin creating {new_table_name} from {table_name}")
        #        sqlite_obj.cursor.execute(f"DROP TABLE IF EXISTS {new_table_name}")
        #        sqlite_obj.cursor.execute(f"CREATE TABLE {new_table_name} AS SELECT * FROM {table_name} where 1=0")
        sqlite_obj.cursor.execute(f"INSERT INTO {new_table_name} SELECT * FROM {table_name} {where_clause}")
        etld_lib_functions.logger.info(f"End   creating {new_table_name} from {table_name}")
    except Exception as e:
        etld_lib_functions.logger.error(f"Error creating table {new_table_name} from {table_name}")
        etld_lib_functions.logger.error(f"Exception is: {e}")
        exit(1)


def create_kb_and_host_list_tables_in_host_list_detection_database(sqlite_obj: etld_lib_sqlite_tables.SqliteObj):
    etld_lib_functions.logger.info(f"Attaching database: {etld_lib_config.host_list_sqlite_file}")
    host_list_table_name, host_list_table_columns = \
        attach_database_to_host_list_detection(sqlite_obj=sqlite_obj,
                                               table_name="Q_Host_List",
                                               database_as_name="H1",
                                               database_file=etld_lib_config.host_list_sqlite_file)
    etld_lib_functions.logger.info(f"Attaching database: {etld_lib_config.kb_table_name}")
    kb_table_name, kb_table_columns = \
        attach_database_to_host_list_detection(sqlite_obj=sqlite_obj,
                                               table_name="Q_KnowledgeBase",
                                               database_as_name="K1",
                                               database_file=etld_lib_config.kb_sqlite_file)

    etld_lib_functions.logger.info(f"Copying table: {host_list_table_name}")
    copy_database_table(sqlite_obj=sqlite_obj, table_name=host_list_table_name, new_table_name="Q_Host_List")

    etld_lib_functions.logger.info(f"Copying table: {kb_table_name}")
    where_clause = f"where {kb_table_name}.QID in (select distinct(QID) from Q_Host_List_Detection_QIDS)"
    copy_database_table(sqlite_obj=sqlite_obj, table_name=kb_table_name,
                        new_table_name="Q_KnowledgeBase_In_Host_List_Detection", where_clause=where_clause)
    etld_lib_functions.logger.info(f"Commit copy of table: {host_list_table_name}, {kb_table_name}")
    sqlite_obj.commit_changes()


def insert_into_sqlite_host_list_detection_host_and_associated_qids(
        host_list_detection_document: dict,
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        counter_obj: dict,
        batch_number: int = 1,
        batch_date: str = '1970-01-01 00:00:00',
):
    def prepare_database_field(field_data, field_name_tmp) -> dict:
        if field_data is None:
            field_data = ""
        elif 'DATE' in field_name_tmp:
            field_data = field_data.replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif isinstance(field_data, int):
            field_data = str(field_data)
        elif not isinstance(field_data, str):
            field_data = json.dumps(field_data)

        return field_data

    def prepare_database_row(item: dict, database_columns: list) -> list:
        row_in_sqlite_form = []
        for field_name in database_columns:
            if field_name in item.keys():
                item[field_name] = \
                    prepare_database_field(item[field_name], field_name)
                row_in_sqlite_form.append(item[field_name])
            else:
                row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field
        return row_in_sqlite_form

    def insert_host_into_database(host_document):
        host_row_in_sqlite_form: list = \
            prepare_database_row(
                item=host_document,
                database_columns=etld_lib_config.host_list_detection_host_csv_columns())

        result = sqlite_obj.insert_or_replace_row(
            table_name=etld_lib_config.host_list_detection_hosts_table_name,
            row=host_row_in_sqlite_form)
        if result is True:
            counter_obj['counter_obj_host_list_detection_hosts'].display_counter_to_log()
        else:
            etld_lib_functions.logger.error("Error inserting detection")
            row = re.sub('\n', '', '|'.join(host_row_in_sqlite_form))
            json_str = json.dumps(host_document)
            json_str = re.sub('\n', '', json_str)
            etld_lib_functions.logger.error(f"ROW: {row}")
            etld_lib_functions.logger.error(f"JSON: {json_str}")
            exit(1)

    def insert_qids_into_database(detection_list: list):

        for one_detection_dict in detection_list:
            if isinstance(one_detection_dict, dict):
                one_detection_dict['ID'] = host_list_detection_document['ID']
                if 'ASSET_ID' in host_list_detection_document.keys():
                    one_detection_dict['ASSET_ID'] = host_list_detection_document['ASSET_ID']
                one_detection_dict['BATCH_DATE'] = batch_date
                one_detection_dict['BATCH_NUMBER'] = batch_number

                qids_row_in_sqlite_form = prepare_database_row(
                    item=one_detection_dict,
                    database_columns=etld_lib_config.host_list_detection_qids_csv_columns())

                result = sqlite_obj.insert_or_replace_row(
                    table_name=etld_lib_config.host_list_detection_qids_table_name,
                    row=qids_row_in_sqlite_form)

                if result is True:
                    counter_obj['counter_obj_host_list_detection_qids'].display_counter_to_log()
                else:
                    etld_lib_functions.logger.error("Error inserting detection")
                    row = re.sub('\n', '', '|'.join(qids_row_in_sqlite_form))
                    json_str = json.dumps(one_detection_dict)
                    json_str = re.sub('\n', '', json_str)
                    etld_lib_functions.logger.error(f"ROW: {row}")
                    etld_lib_functions.logger.error(f"JSON: {json_str}")
                    exit(1)

    # Main
    host_list_detection_document['BATCH_DATE'] = batch_date
    host_list_detection_document['BATCH_NUMBER'] = batch_number
    insert_host_into_database(host_list_detection_document)
    if 'DETECTION_LIST' in host_list_detection_document:
        if 'DETECTION' in host_list_detection_document['DETECTION_LIST']:
            insert_qids_into_database(host_list_detection_document['DETECTION_LIST']['DETECTION'])
        else:
            json_message = \
                {'ID': host_list_detection_document['ID'], 'BATCH_NUMBER': batch_number, 'BATCH_DATE': batch_date}
            etld_lib_functions.logger.info(f"No DETECTION for: {json_message}")
    else:
        json_message = \
            {'ID': host_list_detection_document['ID'], 'BATCH_NUMBER': batch_number, 'BATCH_DATE': batch_date}
        etld_lib_functions.logger.info(f"No DETECTION_LIST for: {json_message}")


def insert_xml_file_into_sqlite(xml_file, sqlite_obj: etld_lib_sqlite_tables.SqliteObj, counter_obj):
    def callback_to_insert_host_into_sqlite(element_names: tuple, document_item: dict):

        if len(element_names) > 2 and "HOST" != element_names[3][0]:
            return True
        else:
            batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(xml_file)
            batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(xml_file)
            try:
                if document_item['ID'] == '168327708':
                    print()
                insert_into_sqlite_host_list_detection_host_and_associated_qids(
                    host_list_detection_document=document_item, sqlite_obj=sqlite_obj,
                    batch_date=batch_date, batch_number=int(batch_number), counter_obj=counter_obj)
            except Exception as e:
                etld_lib_functions.logger.error(f"Exception: {e}")
                etld_lib_functions.logger.error(
                    f"Issue inserting xml file into sqlite: {document_item}, counter={counter_obj}")
            return True

    with etld_lib_config.host_list_detection_open_file_compression_method(
            str(xml_file), "rt", encoding='utf-8') as xml_file_fd:
        xmltodict.parse(xml_file_fd.read(), item_depth=4,
                        item_callback=callback_to_insert_host_into_sqlite)
        sqlite_obj.commit_changes()


def load_one_file_into_sqlite(sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
                              file_path: Path,
                              counter_obj: dict,
                              from_queue_or_directory="Queue",
                              batch_number: int = 0,
                              batch_name: str = "batch_000000",
                              batch_date: str = "2022-01-01 00:00:00",
                              ):
    etld_lib_functions.logger.info(f"Received batch file from {from_queue_or_directory}: {batch_name}")
    sqlite_obj.update_status_table(
        batch_date=batch_date, batch_number=batch_number,
        total_rows_added_to_database=counter_obj['counter_obj_host_list_detection_hosts'].get_counter(),
        status_table_name=etld_lib_config.host_list_detection_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=f'{etld_lib_config.host_list_detection_hosts_table_name} table load_status',
        status_column='begin')
    try:
        insert_xml_file_into_sqlite(file_path, sqlite_obj, counter_obj)
    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Issue inserting xml file into sqlite: {file_path}, counter={counter_obj}")
        exit(1)

    sqlite_obj.update_status_table(
        batch_date=batch_date, batch_number=batch_number,
        total_rows_added_to_database=counter_obj['counter_obj_host_list_detection_hosts'].get_counter(),
        status_table_name=etld_lib_config.host_list_detection_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=f'{etld_lib_config.host_list_detection_hosts_table_name} table load_status',
        status_column='end')
    etld_lib_functions.logger.info(f"Committed batch file to Database: {batch_name}")


def spawn_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite():
    queue_of_file_paths_to_load_to_sqlite = Queue()
    queue_process_to_load_to_sqlite = \
        Process(
            target=host_list_detection_transform_and_load_all_xml_files_into_sqlite,
            args=(queue_of_file_paths_to_load_to_sqlite, True),
            name="load_all_xml_files_into_sqlite")
    queue_process_to_load_to_sqlite.daemon = True
    queue_process_to_load_to_sqlite.start()

    queue_of_file_paths_to_load_to_sqlite.put("BEGIN")
    etld_lib_functions.logger.info(f"Queue of files process id: {queue_process_to_load_to_sqlite.pid} ")

    return queue_process_to_load_to_sqlite, queue_of_file_paths_to_load_to_sqlite


def load_files_into_sqlite_via_multiprocessing_queue(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        queue_of_file_paths,
        counter_obj=None,
):
    def get_next_file_in_queue(bookend, queue_file_path):
        time.sleep(2)
        queue_data = queue_file_path.get()
        if queue_data == bookend:
            etld_lib_functions.logger.info(f"Found {bookend} of Queue.")
            queue_data = bookend
        return queue_data

    file_path = get_next_file_in_queue('BEGIN', queue_of_file_paths)
    batch_number = ""
    batch_date = ""
    if file_path == 'BEGIN':
        while True:
            file_path = get_next_file_in_queue('END', queue_of_file_paths)
            if file_path == 'END':
                sqlite_obj.update_status_table(
                    batch_date=batch_date, batch_number=batch_number,
                    total_rows_added_to_database=counter_obj['counter_obj_host_list_detection_hosts'].get_counter(),
                    status_table_name=etld_lib_config.host_list_detection_status_table_name,
                    status_table_columns=etld_lib_config.status_table_csv_columns(),
                    status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                    status_name_column=f'{etld_lib_config.host_list_detection_hosts_table_name} table load_status',
                    status_column='final')
                break  # SUCCESSFUL END

            batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(file_path)
            batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(file_path)
            batch_name = etld_lib_extract_transform_load.get_batch_name_from_filename(file_path)
            load_one_file_into_sqlite(sqlite_obj=sqlite_obj,
                                      file_path=file_path,
                                      counter_obj=counter_obj,
                                      from_queue_or_directory="Queue",
                                      batch_number=batch_number,
                                      batch_name=batch_name,
                                      batch_date=batch_date,
                                      )
    else:
        etld_lib_functions.logger.error(f"Invalid begin of Queue, {file_path}.  Please restart.")
        exit(1)


def load_files_into_sqlite_via_directory_listing(sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
                                                 extract_dir,
                                                 extract_dir_file_search_blob,
                                                 counter_obj,
                                                 ):
    xml_file_list = []
    for file_name in sorted(Path(extract_dir).glob(extract_dir_file_search_blob)):
        if str(file_name).endswith('.xml') or str(file_name).endswith('.xml.gz'):
            xml_file_list.append(file_name)

    batch_number = ""
    batch_date = ""

    for file_path in xml_file_list:
        batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(file_path)
        batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(file_path)
        batch_name = etld_lib_extract_transform_load.get_batch_name_from_filename(file_path)
        load_one_file_into_sqlite(sqlite_obj=sqlite_obj,
                                  file_path=file_path,
                                  counter_obj=counter_obj,
                                  from_queue_or_directory="directory",
                                  batch_number=batch_number,
                                  batch_name=batch_name,
                                  batch_date=batch_date,
                                  )

    sqlite_obj.update_status_table(
        batch_date=batch_date, batch_number=batch_number,
        total_rows_added_to_database=counter_obj['counter_obj_host_list_detection_hosts'].get_counter(),
        status_table_name=etld_lib_config.host_list_detection_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=f'{etld_lib_config.host_list_detection_hosts_table_name} table load_status',
        status_column='final')


def host_list_detection_transform_and_load_all_xml_files_into_sqlite(
        queue_of_file_paths: Queue = Queue(), multiprocessing_flag=False):
    start_msg_host_list_detection_to_sqlite()
    xml_file_path = ""
    counter_obj_dict = create_counter_objects()
    try:
        host_list_detection_sqlite_obj = etld_lib_sqlite_tables.SqliteObj(
            sqlite_file=etld_lib_config.host_list_detection_sqlite_file)
        drop_and_create_all_tables(
            sqlite_obj=host_list_detection_sqlite_obj)
        #
        if multiprocessing_flag is True:
            load_files_into_sqlite_via_multiprocessing_queue(
                sqlite_obj=host_list_detection_sqlite_obj,
                queue_of_file_paths=queue_of_file_paths,
                counter_obj=counter_obj_dict
            )
            create_kb_and_host_list_tables_in_host_list_detection_database(sqlite_obj=host_list_detection_sqlite_obj)
            host_list_detection_sqlite_obj.commit_changes()
            host_list_detection_sqlite_obj.close_connection()
        else:
            load_files_into_sqlite_via_directory_listing(
                sqlite_obj=host_list_detection_sqlite_obj,
                counter_obj=counter_obj_dict,
                extract_dir=etld_lib_config.host_list_detection_extract_dir,
                extract_dir_file_search_blob=etld_lib_config.host_list_detection_extract_dir_file_search_blob,
            )
            create_kb_and_host_list_tables_in_host_list_detection_database(sqlite_obj=host_list_detection_sqlite_obj)
            host_list_detection_sqlite_obj.commit_changes()
            host_list_detection_sqlite_obj.close_connection()

        for counter_obj_key in counter_obj_dict.keys():
            counter_obj_dict[counter_obj_key].display_final_counter_to_log()
        end_msg_host_list_detection_to_sqlite()

    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Issue with xml file: {xml_file_path}")
        exit(1)


def end_msg_host_list_detection_to_sqlite():
    xml_file_list = sorted(
        Path(etld_lib_config.host_list_detection_extract_dir).glob(
            etld_lib_config.host_list_detection_extract_dir_file_search_blob))
    for host_list_detection_xml_file in xml_file_list:
        if str(host_list_detection_xml_file).endswith('.xml') or str(host_list_detection_xml_file).endswith('.xml.gz'):
            etld_lib_functions.log_file_info(host_list_detection_xml_file, 'input file')
    etld_lib_functions.logger.info(f"end")


def start_msg_host_list_detection_to_sqlite():
    etld_lib_functions.logger.info("start")


def main(multiprocessing_flag=False, queue_of_file_paths: Queue = Queue()):
    # Multiprocessing is executed through spawn_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite()
    host_list_detection_transform_and_load_all_xml_files_into_sqlite(multiprocessing_flag=multiprocessing_flag,
                                                                     queue_of_file_paths=queue_of_file_paths)


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_05_transform_load_xml_to_sqlite')
    etld_lib_config.main()
    main(multiprocessing_flag=False, queue_of_file_paths=Queue())
