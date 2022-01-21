import shelve
import json
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_extract_transform_load_distribute as etld_lib_extract_transform_load_distribute

global count_host_id_loaded_to_json


def host_list_json():
    global count_host_id_loaded_to_json
    shelve_db = etld_lib_config.host_list_shelve_file
    load_json_file = etld_lib_config.host_list_json_file
    count_host_id_loaded_to_json = etld_lib_extract_transform_load_distribute.load_json(load_json_file,shelve_db)


def start_msg_host_list_json():
    etld_lib_functions.logger.info(f"start")


def end_msg_host_list_json():
    global count_host_id_loaded_to_json
    etld_lib_functions.logger.info(f"count host_id loaded to json: {count_host_id_loaded_to_json:,}")
    etld_lib_functions.log_file_info(etld_lib_config.host_list_shelve_file, 'in')
    etld_lib_functions.log_dbm_info(etld_lib_config.host_list_shelve_file)
    etld_lib_functions.log_file_info(etld_lib_config.host_list_json_file)
    etld_lib_functions.logger.info(f"end")


def main():
    start_msg_host_list_json()
    host_list_json()
    end_msg_host_list_json()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_json')
    etld_lib_config.main()
    main()

