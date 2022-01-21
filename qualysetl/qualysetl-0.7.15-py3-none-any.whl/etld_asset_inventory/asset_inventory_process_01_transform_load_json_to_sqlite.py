import json
from pathlib import Path
import re

from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_datetime as etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_sqlite_tables as etld_lib_sqlite_tables
global json_dir
global json_dir_search_glob
global json_file_list
global software_full_name_dict


def transform_epoch_dates(item):
    item['sensor_lastVMScanDate'] = ""
    item['sensor_lastComplianceScanDate'] = ""
    item['sensor_lastFullScanDate'] = ""
    item['agent_lastActivityDate'] = ""
    item['agent_lastCheckedInDate'] = ""
    item['agent_lastInventoryDate'] = ""
    item['inventory_createdDate'] = ""
    item['inventory_lastUpdatedDate'] = ""
    if 'sensor' in item.keys() and item['sensor'] is not None:
        if 'lastVMScan' in item['sensor']:
            item['sensor_lastVMScanDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastVMScan'])
        if 'lastComplianceScan' in item['sensor']:
            item['sensor_lastComplianceScanDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastComplianceScan'])
        if 'lastFullScan' in item['sensor']:
            item['sensor_lastFullScanDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastFullScan'])

    if 'agent' in item.keys() and item['agent'] is not None:
        if 'lastActivity' in item['agent']:
            item['agent_lastActivityDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['agent']['lastActivity'])
        if 'lastCheckedIn' in item['agent']:
            item['agent_lastCheckedInDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['agent']['lastCheckedIn'])
        if 'lastInventory' in item['agent']:
            item['agent_lastInventoryDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['agent']['lastInventory'])

    if 'inventory' in item.keys() and item['inventory'] is not None:
        if 'created' in item['inventory']:
            item['inventory_createdDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['inventory']['created'])
        if 'lastUpdated' in item['inventory']:
            item['inventory_lastUpdatedDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['inventory']['lastUpdated'])
    return item


def insert_one_row_into_table_q_asset_inventory(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        table_name: str,
        table_fields: list,
        asset_item_dict: dict,
        counter_obj,
        counter_obj_duplicates):

    def prepare_asset_inventory_field(field_data, field_name_tmp):
        if field_data is None:
            field_data = ""
        elif 'Date' in field_name_tmp:
            field_data = field_data.replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif 'lastBoot' in field_name_tmp:
            field_data = field_data.replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif isinstance(field_data, int):
            field_data = str(field_data)
        elif not isinstance(field_data, str):
            field_data = json.dumps(field_data)

        return field_data

    row_in_sqlite_form = []
    for field_name in table_fields:  # Iterate through expected columns (contract)
        if field_name in asset_item_dict.keys():  # Iterate through columns found in dictionary
            asset_item_dict[field_name] = \
                prepare_asset_inventory_field(asset_item_dict[field_name], field_name)
            row_in_sqlite_form.append(asset_item_dict[field_name])
        else:
            row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field

    result = sqlite_obj.insert_unique_row_ignore_duplicates(table_name, row_in_sqlite_form)
    if result is True:
        counter_obj.display_counter_to_log()
    else:
        counter_obj_duplicates.display_counter_to_log()


def insert_one_row_into_table_q_asset_inventory_software_assetid(
        asset_item_dict: dict,
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        counter_obj):

    if asset_item_dict['softwareListData'] is not None:
        for software_item in asset_item_dict['softwareListData']['software']:
            if 'fullName' in software_item:
                assetid = str(asset_item_dict['assetId'])
                fullname = software_item['fullName']
                row = {'assetId': assetid, 'fullName': fullname}
                sqlite_row = []
                for field in etld_lib_functions.asset_inventory_software_assetid_csv_columns():
                    if field in row.keys():
                        sqlite_row.append(row[field])
                    else:
                        sqlite_row.append("")

                result = sqlite_obj.insert_unique_row_ignore_duplicates(
                    etld_lib_config.asset_inventory_table_name_software_assetid,
                    sqlite_row)
                if result is True:
                    counter_obj.display_counter_to_log()
                else:
                    pass
                    #etld_lib_functions.logger.info("found dups in software assetid")


def insert_one_row_into_table_q_asset_inventory_software_os_unique(
        asset_item_dict: dict,
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        counter_obj):

    if asset_item_dict['softwareListData'] is not None:
        for software_item in asset_item_dict['softwareListData']['software']:
            if 'fullName' in software_item:
                fullname = str(software_item['fullName'])
                osname = "None"
                isignored = "None"
                ignoredreason = "None"
                category = "None"
                if 'operatingSystem' in asset_item_dict:
                    if 'osName' in asset_item_dict['operatingSystem']:
                        osname = str(asset_item_dict['operatingSystem']['osName'])
                if 'lifecycle' in software_item:
                    lifecycle = json.dumps(software_item['lifecycle'])
                else:
                    lifecycle = {'gaDate': None, 'eolDate': None, 'eosDate': None, 'stage': None,
                                 'lifeCycleConfidence': 'Not Available QETL', 'eolSupportStage': '',
                                 'eosSupportStage': ''}
                if 'isIgnored' in software_item:
                    isignored = str(software_item['isIgnored'])
                if 'ignoredReason' in software_item:
                    ignoredreason = str(software_item['ignoredReason'])
                if 'category' in software_item:
                    category = \
                        f"{software_item['category']} | {software_item['category']} | {software_item['category']}"

                row = {'fullName': fullname, 'osName': osname,
                       'isIgnored': isignored, 'ignoredReason': ignoredreason, 'category': category,
                       'lifecycle': lifecycle}
                sqlite_row = []
                for field in etld_lib_functions.asset_inventory_software_os_unique_csv_columns():
                    if field in row.keys():
                        sqlite_row.append(row[field])
                    else:
                        sqlite_row.append("")

                result = sqlite_obj.insert_unique_row_ignore_duplicates(
                    etld_lib_config.asset_inventory_table_name_software_os_unique,
                    sqlite_row)
                if result is True:
                    counter_obj.display_counter_to_log()


def drop_and_create_all_tables(sqlite_obj):
    sqlite_obj.create_table(
        table_name=etld_lib_config.asset_inventory_table_name,
        csv_columns=etld_lib_functions.asset_inventory_csv_columns(),
        csv_column_types=etld_lib_functions.asset_inventory_csv_column_types(),
        key='assetId')
    sqlite_obj.create_table(
        table_name=etld_lib_config.asset_inventory_table_name_software_os_unique,
        csv_columns=etld_lib_functions.asset_inventory_software_os_unique_csv_columns(),
        key=['fullName', 'osName'])
    sqlite_obj.create_table(
        table_name=etld_lib_config.asset_inventory_table_name_software_assetid,
        csv_columns=etld_lib_functions.asset_inventory_software_assetid_csv_columns(),
        csv_column_types=etld_lib_functions.asset_inventory_software_assetid_csv_column_types(),
        key=['assetId', 'fullName'])


def create_counter_objects():
    counter_obj_asset_inventory = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to table {etld_lib_config.asset_inventory_table_name}")
    counter_obj_asset_inventory_duplicates = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"duplicate rows not added to table {etld_lib_config.asset_inventory_table_name}")
    counter_obj_software_os = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to table {etld_lib_config.asset_inventory_table_name_software_os_unique}")
    counter_obj_software_assetid = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to table {etld_lib_config.asset_inventory_table_name_software_assetid}")
    counter_objects = {'counter_obj_asset_inventory': counter_obj_asset_inventory,
                       'counter_obj_asset_inventory_duplicates': counter_obj_asset_inventory_duplicates,
                       'counter_obj_software_os': counter_obj_software_os,
                       'counter_obj_software_assetid': counter_obj_software_assetid}

    return counter_objects


def insert_one_asset_into_multiple_tables(asset_item, sqlite_obj, counter_objects):
    item = transform_epoch_dates(asset_item)
    insert_one_row_into_table_q_asset_inventory_software_os_unique(
        asset_item_dict=item,
        sqlite_obj=sqlite_obj,
        counter_obj=counter_objects['counter_obj_software_os'])
    insert_one_row_into_table_q_asset_inventory_software_assetid(
        asset_item_dict=item,
        sqlite_obj=sqlite_obj,
        counter_obj=counter_objects['counter_obj_software_assetid'])
    insert_one_row_into_table_q_asset_inventory(
        sqlite_obj=sqlite_obj,
        table_name=etld_lib_config.asset_inventory_table_name,
        table_fields=etld_lib_functions.asset_inventory_csv_columns(),
        asset_item_dict=item,
        counter_obj=counter_objects['counter_obj_asset_inventory'],
        counter_obj_duplicates=counter_objects['counter_obj_asset_inventory_duplicates']
    )


def transform_and_load_all_assets_into_sqlite():
    global json_dir
    global json_dir_search_glob
    global json_file_list

    try:
        sqlite_asset_inventory = etld_lib_sqlite_tables.SqliteObj(etld_lib_config.asset_inventory_sqlite_file)
        drop_and_create_all_tables(sqlite_asset_inventory)
        counter_objects = create_counter_objects()
        json_file_list = sorted(Path(json_dir).glob(json_dir_search_glob))
        for json_file in json_file_list:
            with open(str(json_file), "r", encoding='utf-8') as read_file:
                all_items = json.load(read_file)
                for item in all_items['assetListData']['asset']:
                    insert_one_asset_into_multiple_tables(item, sqlite_asset_inventory, counter_objects)

        sqlite_asset_inventory.commit_changes()
        sqlite_asset_inventory.close_connection()
        counter_objects['counter_obj_asset_inventory_duplicates'].display_final_counter_to_log()
        counter_objects['counter_obj_asset_inventory'].display_final_counter_to_log()
        counter_objects['counter_obj_software_os'].display_final_counter_to_log()
        counter_objects['counter_obj_software_assetid'].display_final_counter_to_log()

    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Potential JSON File corruption detected: {json_file}")
        exit(1)


def end_msg_asset_inventory_sqlite():
    global json_dir_search_glob
    global json_dir
    global json_file_list

    for json_file in json_file_list:
        etld_lib_functions.log_file_info(json_file, 'in')
    etld_lib_functions.logger.info(f"end")


def end_msg_asset_inventory_to_sqlite():
    etld_lib_functions.logger.info(f"end")


def start_msg_asset_inventory_sqlite():
    etld_lib_functions.logger.info("start")


def setup_global_variables():
    global json_dir
    global json_dir_search_glob

    json_dir = etld_lib_config.asset_inventory_json_dir
    json_dir_search_glob = 'asset_inventory_utc*.json'


def main():
    start_msg_asset_inventory_sqlite()
    setup_global_variables()
    transform_and_load_all_assets_into_sqlite()
    end_msg_asset_inventory_to_sqlite()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='asset_inventory_json_to_sqlite')
    etld_lib_config.main()
    main()
