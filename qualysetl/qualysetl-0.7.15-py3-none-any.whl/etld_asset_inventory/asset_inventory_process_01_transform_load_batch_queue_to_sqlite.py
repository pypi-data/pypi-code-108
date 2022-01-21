import shelve
import json
import time
from pathlib import Path
import re

from shelve import DbfilenameShelf
from typing import Dict, Any, List

from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_datetime as etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_sqlite_tables as etld_lib_sqlite_tables
global count_items_added_to_shelve
global count_items_added_to_shelve_display_progress
global shelve_database
global shelve_software_unique_database
global shelve_software_os_unique_database
global shelve_software_assetid_database
global shelve_temp_database
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


# def insert_one_row_into_table_q_asset_inventory(item=None, sqlite_obj=None, table_name=None,
#                                          table_fields=list(), values_var=list()):
#     global count_items_added_to_shelve
#     global count_items_added_to_shelve_display_progress
#     global json_dir
#     global json_dir_search_glob
#
#     item_key = item['assetId']
#     item = transform_epoch_dates(item)
#     row = [item_key, json.dumps(item)]
#     sqlite_obj.insert_row(table_name, values_var, row)


def transform_and_load_asset_into_shelve(item=None, asset_inventory_dict=None, asset_inventory_shelve_file=None):
    global count_items_added_to_shelve
    global count_items_added_to_shelve_display_progress
    global json_dir
    global json_dir_search_glob

    item_key = item['assetId']
    item = transform_epoch_dates(item)
    max_retries = 5
    for i in range(max_retries):
        try:
            asset_inventory_dict[str(item_key)] = item
            count_items_added_to_shelve += 1
            count_items_added_to_shelve_display_progress += 1

        except Exception as e:
            time.sleep(1)
            etld_lib_functions.logger.warning(
                f"Retry #{i + 1:02d} writing assetId {item_key} to {str(asset_inventory_shelve_file)} Exception {e}")
            time.sleep(5)
            continue
        else:
            break # Success
    else:
        etld_lib_functions.logger.error(f"max retries attempted: {max_retries}"
                                        f"error writing assetId:{item_key} "
                                        f"to file: {str(asset_inventory_shelve_file)} ")
        exit(1)

    return True


def transform_and_load_software_assetid_into_shelve(item=None, software_assetid_dict=None):
    if item['softwareListData'] is not None:
        for software_item in item['softwareListData']['software']:
            if 'fullName' in software_item:
                assetid_fullname = \
                    f"{item['assetId']}|{str(software_item['fullName']).replace('|',' ')}"
                if assetid_fullname not in software_assetid_dict:
                    software_assetid_dict[assetid_fullname] = ""


def transform_and_load_software_unique_into_shelve(item=None, software_unique_dict=None):
    if item['softwareListData'] is not None:
        for software_item in item['softwareListData']['software']:
            if 'fullName' in software_item:
                fullname = f"{str(software_item['fullName']).replace('|', ' ')}"
                if fullname not in software_unique_dict:
                    software_unique_dict[fullname] = ""


def transform_and_load_software_os_unique_into_shelve(item=None, software_os_unique_dict=None):
    if item['softwareListData'] is not None:
        for software_item in item['softwareListData']['software']:
            if 'fullName' in software_item:
                osname = "None"
                if 'operatingSystem' in item:
                    if 'osName' in item['operatingSystem']:
                        osname = item['operatingSystem']['osName']
                fullname_osname = f"{str(software_item['fullName']).replace('|', ' ')}|{osname}"
                # fullName|osName
                if fullname_osname not in software_os_unique_dict:
                    if 'lifecycle' in software_item:
                        software_os_unique_dict[fullname_osname] = software_item['lifecycle']
                    else:
                        software_os_unique_dict[fullname_osname] = {'gaDate': None, 'eolDate': None, 'eosDate': None,
                                                                 'stage': None,
                                                                 'lifeCycleConfidence': 'Not Available QETL',
                                                                 'eolSupportStage': '', 'eosSupportStage': ''}


def transform_and_load_asset_inventory_into_shelves():
    global count_items_added_to_shelve
    global shelve_database
    global shelve_temp_database
    global json_dir
    global json_dir_search_glob
    global json_file_list

    counter_obj = etld_lib_functions.DisplayCounterToLog(display_counter_at=10000,
                                                         logger_func=etld_lib_functions.logger.info,
                                                         display_counter_log_message="count assets saved to shelve")

    try:
        json_file_list = sorted(Path(json_dir).glob(json_dir_search_glob), reverse=True)
        with shelve.open(str(shelve_database), flag='nf') as asset_inventory_dict, \
                shelve.open(str(shelve_software_unique_database), flag='nf') as software_unique_dict, \
                shelve.open(str(shelve_software_os_unique_database), flag='nf') as software_os_unique_dict, \
                shelve.open(str(shelve_software_assetid_database), flag='nf') as software_assetid_dict:
            for json_file in json_file_list:
                with open(str(json_file), "r", encoding='utf-8') as read_file:
                    sd_temp = json.load(read_file)
                    for item in sd_temp['assetListData']['asset']:
                        asset_id = str(item['assetId'])
                        if asset_id in asset_inventory_dict:
                            pass
                            # etld_lib_functions.logger.info(f"Asset already exists in shelve: {asset_id}")
                        else:
                            transform_and_load_asset_into_shelve(item, asset_inventory_dict, str(shelve_database))
                            transform_and_load_software_assetid_into_shelve(item, software_assetid_dict)
                            transform_and_load_software_unique_into_shelve(item, software_unique_dict)
                            transform_and_load_software_os_unique_into_shelve(item, software_os_unique_dict)
                            counter_obj.display_counter_to_log()

            asset_inventory_dict.sync()
            software_assetid_dict.sync()
            software_unique_dict.sync()
            counter_obj.display_final_counter_to_log()
    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Potential JSON File corruption detected: {json_file}")
        exit(1)


def transform_and_load_asset_into_sqlite(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        table_name: str,
        table_fields: list,
        var_values: list,
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

    # Write CSV row, Prepare for next row.
    result = sqlite_obj.insert_unique_row_ignore_duplicates(table_name, var_values, row_in_sqlite_form)
    if result is True:
        counter_obj.display_counter_to_log()
    else:
        counter_obj_duplicates.display_counter_to_log()


def transform_and_load_software_assetid_into_sqlite(
        asset_item_dict: dict,
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        var_values: list,
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
                    var_values, sqlite_row)
                if result is True:
                    counter_obj.display_counter_to_log()
                else:
                    pass
                    #etld_lib_functions.logger.info("found dups in software assetid")


def transform_and_load_software_os_unique_into_sqlite(
        asset_item_dict: dict,
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        var_values: list,
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
                    var_values, sqlite_row)
                if result is True:
                    counter_obj.display_counter_to_log()


def transform_and_load_asset_inventory_into_sqlite():
    global count_items_added_to_shelve
    global shelve_database
    global shelve_temp_database
    global json_dir
    global json_dir_search_glob
    global json_file_list

    sqlite_asset_inventory = etld_lib_sqlite_tables.SqliteObj(etld_lib_config.asset_inventory_sqlite_file)
    sqlite_asset_inventory.create_table(
        table_name=etld_lib_config.asset_inventory_table_name,
        csv_columns=etld_lib_functions.asset_inventory_csv_columns(),
        key='assetId')
    var_values_asset_inventory = sqlite_asset_inventory.get_values_var(etld_lib_functions.asset_inventory_csv_columns())
    counter_obj_asset_inventory = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to table {etld_lib_config.asset_inventory_table_name}")
    counter_obj_asset_inventory_duplicates = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"duplicate rows not added to table {etld_lib_config.asset_inventory_table_name}")

    sqlite_asset_inventory.create_table(
        table_name=etld_lib_config.asset_inventory_table_name_software_os_unique,
        csv_columns=etld_lib_functions.asset_inventory_software_os_unique_csv_columns(),
        key=['fullName', 'osName'])
    var_values_asset_inventory_software_os_unique = \
        sqlite_asset_inventory.get_values_var(etld_lib_functions.asset_inventory_software_os_unique_csv_columns())
    counter_obj_software_os = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to table {etld_lib_config.asset_inventory_table_name_software_os_unique}")

    sqlite_asset_inventory.create_table(
        table_name=etld_lib_config.asset_inventory_table_name_software_assetid,
        csv_columns=etld_lib_functions.asset_inventory_software_assetid_csv_columns(),
        key=['assetId', 'fullName'],
        csv_column_types=etld_lib_functions.asset_inventory_software_assetid_csv_column_types())
    var_values_asset_inventory_software_assetid = \
        sqlite_asset_inventory.get_values_var(etld_lib_functions.asset_inventory_software_assetid_csv_columns())
    counter_obj_software_assetid = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to table {etld_lib_config.asset_inventory_table_name_software_assetid}")

    try:
        json_file_list = sorted(Path(json_dir).glob(json_dir_search_glob))
        for json_file in json_file_list:
            with open(str(json_file), "r", encoding='utf-8') as read_file:
                all_items = json.load(read_file)
                for item in all_items['assetListData']['asset']:
                    item = transform_epoch_dates(item)
                    transform_and_load_software_os_unique_into_sqlite(
                        asset_item_dict=item,
                        sqlite_obj=sqlite_asset_inventory,
                        var_values=var_values_asset_inventory_software_os_unique,
                        counter_obj=counter_obj_software_os)
                    transform_and_load_software_assetid_into_sqlite(
                        asset_item_dict=item,
                        sqlite_obj=sqlite_asset_inventory,
                        var_values=var_values_asset_inventory_software_assetid,
                        counter_obj=counter_obj_software_assetid)
                    transform_and_load_asset_into_sqlite(
                        sqlite_obj=sqlite_asset_inventory,
                        table_name=etld_lib_config.asset_inventory_table_name,
                        table_fields=etld_lib_functions.asset_inventory_csv_columns(),
                        var_values=var_values_asset_inventory,
                        asset_item_dict=item,
                        counter_obj=counter_obj_asset_inventory,
                        counter_obj_duplicates=counter_obj_asset_inventory_duplicates
                    )

        sqlite_asset_inventory.commit_changes()
        sqlite_asset_inventory.close_connection()
        counter_obj_asset_inventory_duplicates.display_final_counter_to_log()
        counter_obj_asset_inventory.display_final_counter_to_log()
        counter_obj_software_os.display_final_counter_to_log()
        counter_obj_software_assetid.display_final_counter_to_log()

    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Potential JSON File corruption detected: {json_file}")
        exit(1)


def end_msg_asset_inventory_shelve():
    global count_items_added_to_shelve
    global json_dir_search_glob
    global json_dir
    global json_file_list

    etld_lib_functions.logger.info(
        f"count host ids added to shelve: {count_items_added_to_shelve:,} for {str(shelve_database)}")
    for json_file in json_file_list:
        etld_lib_functions.log_file_info(json_file, 'in')
    etld_lib_functions.log_file_info(str(shelve_database))
    etld_lib_functions.log_file_info(str(shelve_software_unique_database))
    etld_lib_functions.log_file_info(str(shelve_software_os_unique_database))
    etld_lib_functions.log_file_info(str(shelve_software_assetid_database))
    etld_lib_functions.log_dbm_count_of_keys_found(str(shelve_database))
    etld_lib_functions.log_dbm_count_of_keys_found(str(shelve_software_unique_database))
    etld_lib_functions.log_dbm_count_of_keys_found(str(shelve_software_os_unique_database))
    etld_lib_functions.log_dbm_count_of_keys_found(str(shelve_software_assetid_database))

    etld_lib_functions.logger.info(f"end")


def end_msg_asset_inventory_to_sqlite():
    etld_lib_functions.logger.info(f"end")


def start_msg_asset_inventory_shelve():
    etld_lib_functions.logger.info("start")


def setup_shelve_vars():
    global count_items_added_to_shelve
    global count_items_added_to_shelve_display_progress
    global shelve_database
    global shelve_software_unique_database
    global shelve_software_os_unique_database
    global shelve_software_assetid_database
    global shelve_temp_database
    global json_dir
    global json_dir_search_glob

    count_items_added_to_shelve = 0
    count_items_added_to_shelve_display_progress = 0
    shelve_database = etld_lib_config.asset_inventory_shelve_file
    shelve_software_unique_database = etld_lib_config.asset_inventory_shelve_software_unique_file
    shelve_software_os_unique_database = etld_lib_config.asset_inventory_shelve_software_os_unique_file
    shelve_software_assetid_database = etld_lib_config.asset_inventory_shelve_software_assetid_file
    shelve_temp_database = etld_lib_config.asset_inventory_temp_shelve_file
    json_dir = etld_lib_config.asset_inventory_json_dir
    json_dir_search_glob = 'asset_inventory_utc*.json'


def main(batch_queue):
    start_msg_asset_inventory_shelve()
    setup_shelve_vars()
    #transform_and_load_asset_inventory_into_shelves()
    transform_and_load_asset_inventory_into_sqlite()
    end_msg_asset_inventory_to_sqlite()
    # end_msg_asset_inventory_shelve()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='asset_inventory_transform_to_shelve')
    etld_lib_config.main()
    main()
