#import shelve
#import json
#import time
#from pathlib import Path
#import re
#from shelve import DbfilenameShelf
#from typing import Dict, Any, List
#
#from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
#from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
#from qualys_etl.etld_lib import etld_lib_datetime as etld_lib_datetime
#global count_items_added_to_shelve
#global count_items_added_to_shelve_display_progress
#global shelve_database
#global shelve_software_unique_database
#global shelve_software_os_unique_database
#global shelve_software_assetid_database
#global shelve_temp_database
#global json_dir
#global json_dir_search_glob
#global json_file_list
#global software_full_name_dict
#
#
#def transform_epoch_dates(item):
#    item['sensor_lastVMScanDate'] = ""
#    item['sensor_lastComplianceScanDate'] = ""
#    item['sensor_lastFullScanDate'] = ""
#    item['agent_lastActivityDate'] = ""
#    item['agent_lastCheckedInDate'] = ""
#    item['agent_lastInventoryDate'] = ""
#    item['inventory_createdDate'] = ""
#    item['inventory_lastUpdatedDate'] = ""
#    if 'sensor' in item.keys() and item['sensor'] is not None:
#        if 'lastVMScan' in item['sensor']:
#            item['sensor_lastVMScanDate'] = \
#                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastVMScan'])
#        if 'lastComplianceScan' in item['sensor']:
#            item['sensor_lastComplianceScanDate'] = \
#                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastComplianceScan'])
#        if 'lastFullScan' in item['sensor']:
#            item['sensor_lastFullScanDate'] = \
#                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastFullScan'])
#
#    if 'agent' in item.keys() and item['agent'] is not None:
#        if 'lastActivity' in item['agent']:
#            item['agent_lastActivityDate'] = \
#                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['agent']['lastActivity'])
#        if 'lastCheckedIn' in item['agent']:
#            item['agent_lastCheckedInDate'] = \
#                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['agent']['lastCheckedIn'])
#        if 'lastInventory' in item['agent']:
#            item['agent_lastInventoryDate'] = \
#                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['agent']['lastInventory'])
#
#    if 'inventory' in item.keys() and item['inventory'] is not None:
#        if 'created' in item['inventory']:
#            item['inventory_createdDate'] = \
#                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['inventory']['created'])
#        if 'lastUpdated' in item['inventory']:
#            item['inventory_lastUpdatedDate'] = \
#                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['inventory']['lastUpdated'])
#    return item
#
#
#def transform_and_load_asset_into_shelve(item=None, asset_inventory_dict=None, asset_inventory_shelve_file=None):
#    global count_items_added_to_shelve
#    global count_items_added_to_shelve_display_progress
#    global json_dir
#    global json_dir_search_glob
#
#    item_key = item['assetId']
#    item = transform_epoch_dates(item)
#    max_retries = 5
#    for i in range(max_retries):
#        try:
#            asset_inventory_dict[str(item_key)] = item
#            count_items_added_to_shelve += 1
#            count_items_added_to_shelve_display_progress += 1
#
#        except Exception as e:
#            time.sleep(1)
#            etld_lib_functions.logger.warning(
#                f"Retry #{i + 1:02d} writing assetId {item_key} to {str(asset_inventory_shelve_file)} Exception {e}")
#            time.sleep(5)
#            continue
#        else:
#            break # Success
#    else:
#        etld_lib_functions.logger.error(f"max retries attempted: {max_retries}"
#                                        f"error writing assetId:{item_key} "
#                                        f"to file: {str(asset_inventory_shelve_file)} ")
#        exit(1)
#
#    return True
#
#
#def transform_and_load_software_assetid_into_shelve(item=None, software_assetid_dict=None):
#    if item['softwareListData'] is not None:
#        for software_item in item['softwareListData']['software']:
#            if 'fullName' in software_item:
#                assetid_fullname = \
#                    f"{item['assetId']}|{str(software_item['fullName']).replace('|',' ')}"
#                if assetid_fullname not in software_assetid_dict:
#                    software_assetid_dict[assetid_fullname] = ""
#
#
#def transform_and_load_software_unique_into_shelve(item=None, software_unique_dict=None):
#    if item['softwareListData'] is not None:
#        for software_item in item['softwareListData']['software']:
#            if 'fullName' in software_item:
#                fullname = f"{str(software_item['fullName']).replace('|', ' ')}"
#                if fullname not in software_unique_dict:
#                    software_unique_dict[fullname] = ""
#
#
#def transform_and_load_software_os_unique_into_shelve(item=None, software_os_unique_dict=None):
#    if item['softwareListData'] is not None:
#        for software_item in item['softwareListData']['software']:
#            if 'fullName' in software_item:
#                osname = "None"
#                if 'operatingSystem' in item:
#                    if 'osName' in item['operatingSystem']:
#                        osname = item['operatingSystem']['osName']
#                fullname_osname = f"{str(software_item['fullName']).replace('|', ' ')}|{osname}"
#                # fullName|osName
#                if fullname_osname not in software_os_unique_dict:
#                    if 'lifecycle' in software_item:
#                        software_os_unique_dict[fullname_osname] = software_item['lifecycle']
#                    else:
#                        software_os_unique_dict[fullname_osname] = {'gaDate': None, 'eolDate': None, 'eosDate': None,
#                                                                 'stage': None,
#                                                                 'lifeCycleConfidence': 'Not Available QETL',
#                                                                 'eolSupportStage': '', 'eosSupportStage': ''}
#
#
#def transform_and_load_asset_inventory_into_shelves():
#    global count_items_added_to_shelve
#    global shelve_database
#    global shelve_temp_database
#    global json_dir
#    global json_dir_search_glob
#    global json_file_list
#
#    counter_obj = etld_lib_functions.DisplayCounterToLog(display_counter_at=10000,
#                                                         logger_func=etld_lib_functions.logger.info,
#                                                         display_counter_log_message="count assets saved to shelve")
#
#    try:
#        json_file_list = sorted(Path(json_dir).glob(json_dir_search_glob), reverse=True)
#        with shelve.open(str(shelve_database), flag='nf') as asset_inventory_dict, \
#                shelve.open(str(shelve_software_unique_database), flag='nf') as software_unique_dict, \
#                shelve.open(str(shelve_software_os_unique_database), flag='nf') as software_os_unique_dict, \
#                shelve.open(str(shelve_software_assetid_database), flag='nf') as software_assetid_dict:
#            for json_file in json_file_list:
#                with open(str(json_file), "r", encoding='utf-8') as read_file:
#                    sd_temp = json.load(read_file)
#                    for item in sd_temp['assetListData']['asset']:
#                        asset_id = str(item['assetId'])
#                        if asset_id in asset_inventory_dict:
#                            pass
#                            # etld_lib_functions.logger.info(f"Asset already exists in shelve: {asset_id}")
#                        else:
#                            transform_and_load_asset_into_shelve(item, asset_inventory_dict, str(shelve_database))
#                            transform_and_load_software_assetid_into_shelve(item, software_assetid_dict)
#                            transform_and_load_software_unique_into_shelve(item, software_unique_dict)
#                            transform_and_load_software_os_unique_into_shelve(item, software_os_unique_dict)
#                            counter_obj.display_counter_to_log()
#
#            asset_inventory_dict.sync()
#            software_assetid_dict.sync()
#            software_unique_dict.sync()
#            counter_obj.display_final_counter_to_log()
#    except Exception as e:
#        etld_lib_functions.logger.error(f"Exception: {e}")
#        etld_lib_functions.logger.error(f"Potential JSON File corruption detected: {json_file}")
#        exit(1)
#
#
#def end_msg_asset_inventory_shelve():
#    global count_items_added_to_shelve
#    global json_dir_search_glob
#    global json_dir
#    global json_file_list
#
#    etld_lib_functions.logger.info(
#        f"count host ids added to shelve: {count_items_added_to_shelve:,} for {str(shelve_database)}")
#    for json_file in json_file_list:
#        etld_lib_functions.log_file_info(json_file, 'in')
#    etld_lib_functions.log_file_info(str(shelve_database))
#    etld_lib_functions.log_file_info(str(shelve_software_unique_database))
#    etld_lib_functions.log_file_info(str(shelve_software_os_unique_database))
#    etld_lib_functions.log_file_info(str(shelve_software_assetid_database))
#    etld_lib_functions.log_dbm_count_of_keys_found(str(shelve_database))
#    etld_lib_functions.log_dbm_count_of_keys_found(str(shelve_software_unique_database))
#    etld_lib_functions.log_dbm_count_of_keys_found(str(shelve_software_os_unique_database))
#    etld_lib_functions.log_dbm_count_of_keys_found(str(shelve_software_assetid_database))
#
#    etld_lib_functions.logger.info(f"end")
#
#
#def start_msg_asset_inventory_shelve():
#    etld_lib_functions.logger.info("start")
#
#
#def setup_shelve_vars():
#    global count_items_added_to_shelve
#    global count_items_added_to_shelve_display_progress
#    global shelve_database
#    global shelve_software_unique_database
#    global shelve_software_os_unique_database
#    global shelve_software_assetid_database
#    global shelve_temp_database
#    global json_dir
#    global json_dir_search_glob
#
#    count_items_added_to_shelve = 0
#    count_items_added_to_shelve_display_progress = 0
#    shelve_database = etld_lib_config.asset_inventory_shelve_file
#    shelve_software_unique_database = etld_lib_config.asset_inventory_shelve_software_unique_file
#    shelve_software_os_unique_database = etld_lib_config.asset_inventory_shelve_software_os_unique_file
#    shelve_software_assetid_database = etld_lib_config.asset_inventory_shelve_software_assetid_file
#    shelve_temp_database = etld_lib_config.asset_inventory_temp_shelve_file
#    json_dir = etld_lib_config.asset_inventory_json_dir
#    json_dir_search_glob = 'asset_inventory_utc*.json'
#
#
#def main():
#    start_msg_asset_inventory_shelve()
#    setup_shelve_vars()
#    transform_and_load_asset_inventory_into_shelves()
#    end_msg_asset_inventory_shelve()
#
#
#if __name__ == "__main__":
#    etld_lib_functions.main(my_logger_prog_name='asset_inventory_transform_to_shelve')
#    etld_lib_config.main()
#    main()
#