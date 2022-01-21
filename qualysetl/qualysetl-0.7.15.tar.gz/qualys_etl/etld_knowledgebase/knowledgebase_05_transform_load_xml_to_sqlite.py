#!/usr/bin/env python3
import xmltodict
import json
import re
from pathlib import Path

from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables
from qualys_etl.etld_lib import etld_lib_extract_transform_load


def create_counter_objects(database_type='sqlite', table_name=""):
    counter_obj_kb = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added/updated into {database_type} "
                                    f"table {table_name}")

    counter_obj_kb_duplicates = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"duplicate rows not added to {database_type} "
                                    f"table {table_name}")

    counter_obj_dict_new = {'counter_obj_kb': counter_obj_kb,
                            'counter_obj_kb_duplicates': counter_obj_kb_duplicates}

    return counter_obj_dict_new


def drop_and_create_temp_merge_tables(sqlite_obj):
    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.kb_table_name_merge_new_data,
        csv_columns=etld_lib_config.kb_csv_columns(),
        csv_column_types=etld_lib_config.kb_csv_column_types(),
        key=['QID'])

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.kb_status_table_name,
        csv_columns=etld_lib_config.status_table_csv_columns(),
        csv_column_types=etld_lib_config.status_table_csv_column_types(),
        key=['STATUS_NAME'])


def drop_and_create_all_tables(sqlite_obj):
    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.kb_table_name,
        csv_columns=etld_lib_config.kb_csv_columns(),
        csv_column_types=etld_lib_config.kb_csv_column_types(),
        key=['QID'])

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.kb_status_table_name,
        csv_columns=etld_lib_config.status_table_csv_columns(),
        csv_column_types=etld_lib_config.status_table_csv_column_types(),
        key=['STATUS_NAME'])


def drop_and_create_all_views(sqlite_obj):
    drop_view = f"DROP VIEW IF EXISTS {etld_lib_config.kb_table_name_cve_list_view}"
    sqlite_obj.execute_statement(drop_view)
    create_view_select_statement = \
        '''select SUBSTR(CVE_LIST_ITEM_PREFIX, 0, CVE_LIST_ITEM_PREFIX_LENGTH) AS CVE, * from 
(
select 
Q_KnowledgeBase.*,
INSTR(json_each.value,'CVE') as BEGIN_CVE_LIST_ITEM, 
json_each.value as CVE_LIST_ITEM_JSON, 
SUBSTR(json_each.value, INSTR(json_each.value,'CVE')) AS CVE_LIST_ITEM_PREFIX,
INSTR(SUBSTR(json_each.value, INSTR(json_each.value,'CVE')),'","') as CVE_LIST_ITEM_PREFIX_LENGTH 
from Q_KnowledgeBase, json_each( Q_KnowledgeBase.CVE_LIST, '$.CVE' )
where CVE_LIST like '%{%'
) 
ORDER BY CVE DESC'''

    create_view = \
        f"CREATE VIEW {etld_lib_config.kb_table_name_cve_list_view} as " \
        f"{create_view_select_statement}"
    sqlite_obj.execute_statement(create_view)


def insert_one_row_into_table(
        item_dict: dict,
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        table_name: str,
        counter_obj: dict
):

    def prepare_field(field_data: dict, field_name_tmp):
        if field_data is None:
            field_data = ""
        elif 'DATE' in field_name_tmp:
            field_data = field_data.replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif isinstance(field_data, int):
            field_data = str(field_data)
        elif 'CVE_LIST' in field_name_tmp:
            if 'CVE' in field_data.keys():
                if isinstance(field_data['CVE'], dict):
                    one_item_dict = [field_data['CVE']]
                    field_data['CVE'] = one_item_dict
                    field_data = json.dumps(field_data)
                else:
                    field_data = json.dumps(field_data)
        elif not isinstance(field_data, str):
            field_data = json.dumps(field_data)

        return field_data

    row_in_sqlite_form = []
    for field_name in etld_lib_config.kb_csv_columns():  # Iterate through expected columns (contract)
        if field_name in item_dict.keys():  # Iterate through columns found in dictionary
            item_dict[field_name] = \
                prepare_field(item_dict[field_name], field_name)
            row_in_sqlite_form.append(item_dict[field_name])
        else:
            row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field

    result = sqlite_obj.insert_or_replace_row(table_name, row_in_sqlite_form)

    if result is True:
        counter_obj['counter_obj_kb'].display_counter_to_log()
    else:
        counter_obj['counter_obj_kb_duplicates'].display_counter_to_log()


def insert_xml_file_into_sqlite(xml_file: Path,
                                sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
                                table_name: str,
                                counter_obj: dict,
                                compression_method=open):

    def callback_to_insert_host_into_sqlite(element_names: tuple, document_item: dict):
        if len(element_names) > 2 and "VULN" != element_names[3][0]:
            return True
        document_item['BATCH_DATE'] = batch_date
        document_item['BATCH_NUMBER'] = int(batch_number)
        insert_one_row_into_table(
            document_item, sqlite_obj, table_name, counter_obj=counter_obj)
        return True

    with compression_method(str(xml_file), "rt", encoding='utf-8') as xml_file_fd:
        batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(xml_file)
        batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(xml_file)
        xmltodict.parse(xml_file_fd.read(), item_depth=4,
                        item_callback=callback_to_insert_host_into_sqlite)


def kb_transform_and_load_all_xml_files_into_sqlite():
    # TODO Drop Merge Table if exists, load new data into merge table,
    #  if not 1970, load data from old table where not exists into merge table,
    #  rename merge table to old table name.
    start_msg_kb_to_sqlite()
    xml_file_path = ""
    try:
        kb_sqlite_obj = etld_lib_sqlite_tables.SqliteObj(sqlite_file=etld_lib_config.kb_sqlite_file)
        xml_file_list = []
        rebuild_flag = False
        for file_name in sorted(Path(etld_lib_config.kb_extract_dir).glob(etld_lib_config.kb_extract_dir_file_search_blob)):
            if str(file_name).endswith('.xml') or str(file_name).endswith('.xml.gz'):
                xml_file_list.append(file_name)

        xml_file_to_import_into_sqlite = ""
        if len(xml_file_list) > 0:
            xml_file_to_import_into_sqlite = xml_file_list[-1]
            if xml_file_to_import_into_sqlite.name.__contains__("1970"):
                rebuild_flag = True
        else:
            etld_lib_functions.logger.error("No xml files to process, rerun extract when ready.")
            etld_lib_functions.logger.error(f"Directory: {etld_lib_config.kb_extract_dir}")
            exit(1)

        if rebuild_flag is True:
            # REBUILD KNOWLEDGEBASE
            counter_obj_dict = create_counter_objects(table_name=etld_lib_config.kb_table_name)
            drop_and_create_all_tables(sqlite_obj=kb_sqlite_obj)
            drop_and_create_all_views(sqlite_obj=kb_sqlite_obj)
            insert_xml_file_into_sqlite(
                xml_file=xml_file_to_import_into_sqlite,
                sqlite_obj=kb_sqlite_obj,
                table_name=etld_lib_config.kb_table_name,
                counter_obj=counter_obj_dict,
                compression_method=etld_lib_config.kb_open_file_compression_method)
        else:
            counter_obj_dict = create_counter_objects(table_name=etld_lib_config.kb_table_name)
            drop_and_create_all_views(sqlite_obj=kb_sqlite_obj)
            insert_xml_file_into_sqlite(
                xml_file=xml_file_to_import_into_sqlite,
                sqlite_obj=kb_sqlite_obj,
                table_name=etld_lib_config.kb_table_name,
                counter_obj=counter_obj_dict,
                compression_method=etld_lib_config.kb_open_file_compression_method)
        batch_name = etld_lib_extract_transform_load.get_batch_name_from_filename(
            file_name=xml_file_to_import_into_sqlite)
        batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(
            file_name=xml_file_to_import_into_sqlite)
        batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(
            file_name=xml_file_to_import_into_sqlite)
        etld_lib_functions.logger.info(f"Received batch file from multiprocessing Queue: {batch_name}")

        status_name, status_detail_dict, status_count = \
            kb_sqlite_obj.update_status_table(
                batch_date=batch_date, batch_number=batch_number,
                total_rows_added_to_database=counter_obj_dict['counter_obj_kb'].get_counter(),
                status_table_name=etld_lib_config.kb_status_table_name,
                status_table_columns=etld_lib_config.status_table_csv_columns(),
                status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                status_name_column='KNOWLEDGEBASE_LOAD_STATUS', status_column='final')

        kb_sqlite_obj.commit_changes()
        etld_lib_functions.log_file_info(xml_file_to_import_into_sqlite, "File loaded into database")
        kb_sqlite_obj.vacuum_database()
        kb_sqlite_obj.commit_changes()
        etld_lib_functions.log_file_info(etld_lib_config.kb_sqlite_file, "Database Vacuum Completed")
        kb_sqlite_obj.close_connection()
        counter_obj_dict['counter_obj_kb'].display_final_counter_to_log()
        end_msg_kb_to_sqlite()

    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Issue with xml file: {xml_file_path}")
        exit(1)


def end_msg_kb_to_sqlite():
    etld_lib_functions.logger.info(f"end")


def start_msg_kb_to_sqlite():
    etld_lib_functions.logger.info("start")


def main():
    kb_transform_and_load_all_xml_files_into_sqlite()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='knowledgebase_05_transform_load_xml_to_sqlite')
    etld_lib_config.main()
    main()
