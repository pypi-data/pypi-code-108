import shelve
import xmltodict
import re
import json
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables as etld_lib_sqlite_tables

global count_host_ids_added_to_shelve
global host_list_shelve_database
global host_list_xml_files_selected
global counter_obj


def transform_host_list_item_to_shelve(_, item):
    global host_list_shelve_database
    global count_host_ids_added_to_shelve
    global counter_obj

    if len(_) > 2 and "HOST" != _[3][0]:
        return True
    hostid = item['ID']


def drop_and_create_all_tables(sqlite_obj):
    sqlite_obj.create_table(
        table_name=etld_lib_config.host_list_table_name,
        csv_columns=etld_lib_functions.host_list_csv_columns(),
        key='ID')


def create_counter_objects():
    counter_obj_host_list = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to table {etld_lib_config.host_list_table_name}")
    counter_objects = {'counter_obj_host_list': counter_obj_host_list}

    return counter_objects


def update_q_host_list_table(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        table_name: str,
        table_fields: list,
        item: dict,
        counter_obj):

    def prepare_asset_inventory_field(field_data, field_name_tmp):
        if field_data is None:
            field_data = ""
        elif 'DATE' in field_name_tmp:
            field_data = field_data.replace("T", " ").replace("Z", "")
        elif 'ASSET_GROUP_IDS' in field_name_tmp:
            asset_group_json_header = '''{"assetGroups": [ '''
            asset_group_json_trailer = ''']}'''
            asset_group_json_body = ['{"id": ', 'asset_group', '}']
            asset_groups_json = []
            for asset_group in str(field_data).split(","):
                asset_group_json_body[1] = asset_group
                asset_groups_json.append("".join(asset_group_json_body))
            if len(asset_groups_json) > 0:
                asset_groups_json.append(asset_group_json_trailer)
                field_data = f"{asset_group_json_header}{','.join(asset_groups_json)}{asset_group_json_trailer}"
            else:
                field_data = ""
        elif not isinstance(field_data, str):
            field_data = json.dumps(field_data)
        return field_data

    row_in_sqlite_form = []
    for field_name in table_fields:  # Iterate through expected columns (contract)
        if field_name in item.keys():  # Iterate through columns found in dictionary
            item[field_name] = \
                prepare_asset_inventory_field(item[field_name], field_name)
            row_in_sqlite_form.append(item[field_name])
        else:
            row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field

    result = sqlite_obj.insert_unique_row_ignore_duplicates(table_name, row_in_sqlite_form)
    if result is True:
        counter_obj.display_counter_to_log()


def insert_one_asset_into_tables(item, sqlite_obj, counter_objects):
    update_q_host_list_table(
        item=item,
        sqlite_obj=sqlite_obj,
        table_name=etld_lib_config.host_list_table_name,
        table_fields=etld_lib_functions.host_list_csv_columns(),
        counter_obj=counter_objects['counter_obj_host_list'])


def host_list_shelve():
    global count_host_ids_added_to_shelve
    global host_list_shelve_database
    global host_list_xml_files_selected
    global counter_obj

    # xml_files, other = (not ec2, google or azure). (ec2,google,azure = include metadata for each)
    host_list_xml_files_selected = {'host_list_other_xml_file': etld_lib_config.host_list_other_xml_file}
    etld_lib_functions.log_dbm_info(etld_lib_config.host_list_shelve_file)
    # TODO add ability to process over 1 million hosts
    host_list_xml_file = host_list_xml_files_selected['host_list_other_xml_file']
    try:
        for host_list_xml_file in host_list_xml_files_selected.values():
            with open(host_list_xml_file, 'r', encoding='utf-8') as xml_file:
                with shelve.open(str(etld_lib_config.host_list_shelve_file), flag='n') as host_list_shelve_database:
                    xmltodict.parse(xml_file.read(), item_depth=4, item_callback=transform_host_list_item_to_shelve)
    except Exception as e:
        etld_lib_functions.logger.error(f"XML File corruption detected: {host_list_xml_file}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def end_msg_host_list_shelve():
    global count_host_ids_added_to_shelve
    global host_list_xml_files_selected
    etld_lib_functions.logger.info(
        f"total count host list shelve records written: {count_host_ids_added_to_shelve:,} for {str(etld_lib_config.host_list_shelve_file)}")
    for host_list_xml_file in host_list_xml_files_selected.values():
        etld_lib_functions.log_file_info(host_list_xml_file, 'in')
    etld_lib_functions.log_dbm_info(etld_lib_config.host_list_shelve_file)
    etld_lib_functions.log_file_info(etld_lib_config.host_list_shelve_file)
    etld_lib_functions.logger.info(f"end")


def start_msg_host_list_shelve():
    etld_lib_functions.logger.info("start")


def main():
    start_msg_host_list_shelve()
    host_list_shelve()
    end_msg_host_list_shelve()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_shelve')
    etld_lib_config.main()
    main()
