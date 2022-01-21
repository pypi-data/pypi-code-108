import shelve
import xmltodict
import time

from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
global count_qids_added_to_shelve
global count_items_added_to_shelve
global kb_shelve_database
global counter_obj


def transform_kb_item_to_shelve(_, kb_item):
    QID = kb_item['QID']
    global count_qids_added_to_shelve
    global kb_shelve_database
    global count_items_added_to_shelve
    global counter_obj
    count_qids_added_to_shelve = count_qids_added_to_shelve + 1
    # Retry logic to help with dbm slowness.
    # TODO update for loop to else syntax.
    for i in range(5):
        try:
            kb_shelve_database[QID] = kb_item
            count_items_added_to_shelve += 1
            counter_obj.display_counter_to_log()
            break
        except Exception as e:
            time.sleep(1)
            etld_lib_functions.logger.info(
                f"Retry #{i + 1:02d} writing QID {QID} to "
                f"{str(etld_lib_config.kb_shelve_file)} Exception {e}")
            if i > 4:
                etld_lib_functions.logger.error(f"Error Writing QID {QID} ")
                etld_lib_functions.logger.error(f"Error in File: {__file__} Line: {etld_lib_functions.lineno()}")
                etld_lib_functions.logger.error(f"Error writing to {str(etld_lib_config.kb_shelve_file)} ")
                etld_lib_functions.logger.error(f"Exception: {e}")
                exit(1)
    return True


def kb_shelve():
    global kb_shelve_database
    global count_qids_added_to_shelve
    global count_items_added_to_shelve
    global counter_obj
    count_qids_added_to_shelve = 0
    count_items_added_to_shelve = 0
    counter_obj = \
        etld_lib_functions.DisplayCounterToLog(display_counter_at=10000,
                                               logger_func=etld_lib_functions.logger.info,
                                               display_counter_log_message=
                                               "count knowledgebase records written to shelve")
    etld_lib_functions.log_dbm_info(etld_lib_config.kb_shelve_file)
    try:
        with open(etld_lib_config.kb_xml_file, 'r', encoding='utf-8') as xml_file:
            with shelve.open(str(etld_lib_config.kb_shelve_file), flag='c') as kb_shelve_database:
                xmltodict.parse(xml_file.read(), item_depth=4, item_callback=transform_kb_item_to_shelve)
        counter_obj.display_final_counter_to_log()
    except Exception as e:
        etld_lib_functions.logger.error(f"XML File corruption detected: {etld_lib_config.kb_xml_file}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def end_msg_kb_shelve():
    global count_qids_added_to_shelve
    etld_lib_functions.logger.info(
        f"count qids added to shelve: {count_qids_added_to_shelve:,} for {str(etld_lib_config.kb_shelve_file)}")
    etld_lib_functions.log_file_info(etld_lib_config.kb_xml_file, 'in')
    etld_lib_functions.log_dbm_info(etld_lib_config.kb_shelve_file)
    etld_lib_functions.log_file_info(etld_lib_config.kb_shelve_file)
    etld_lib_functions.logger.info(f"end")


def start_msg_kb_shelve():
    etld_lib_functions.logger.info(f"start")


def main():
    start_msg_kb_shelve()
    kb_shelve()
    end_msg_kb_shelve()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name="kb_shelve")
    etld_lib_config.main()
    main()
