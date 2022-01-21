from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_extract_transform_load_distribute as etld_lib_extract_transform_load_distribute

global count_qid_loaded_to_json


def kb_json():
    global count_qid_loaded_to_json
    start_msg_kb_json()
    shelve_db = etld_lib_config.kb_shelve_file
    load_json_file = etld_lib_config.kb_json_file
    count_qid_loaded_to_json = etld_lib_extract_transform_load_distribute.load_json(load_json_file,shelve_db)
    end_msg_kb_json()


def start_msg_kb_json():
    etld_lib_functions.logger.info(f"start")


def end_msg_kb_json():
    global count_qid_loaded_to_json
    etld_lib_functions.logger.info(f"count qid loaded to json: {count_qid_loaded_to_json:,}")
    etld_lib_functions.log_file_info(etld_lib_config.kb_shelve_file, 'in')
    etld_lib_functions.log_dbm_info(etld_lib_config.kb_shelve_file)
    etld_lib_functions.log_file_info(etld_lib_config.kb_json_file)
    etld_lib_functions.logger.info(f"end")


def main():
    kb_json()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name="kb_load_json")
    etld_lib_config.main()
    main()
