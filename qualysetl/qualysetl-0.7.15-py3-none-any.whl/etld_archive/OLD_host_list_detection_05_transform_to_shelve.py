import shelve
import xmltodict
import time
from pathlib import Path

from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
global count_items_added_to_shelve
global host_list_detection_shelve_database
global shelve_file
global shelve_database
global xml_dir
global xml_dir_search_glob
global xml_file_list
global callback_item
global counter_obj


def transform_xml_item_to_shelve(_, item):
    global count_items_added_to_shelve
    global shelve_database
    global xml_dir
    global shelve_file
    global xml_dir_search_glob
    global callback_item
    global counter_obj

    if len(_) > 2 and "HOST" != _[3][0]:
        return True
    ID = item['ID']
    # Retry logic to help with windows dbm.dumb slow writer.
    max_retries = 5
    for i in range(max_retries):
        try:
            shelve_database[ID] = item
            count_items_added_to_shelve += 1
            counter_obj.display_counter_to_log()
        except Exception as e:
            time.sleep(1)
            etld_lib_functions.logger.warning(
                f"Retry #{i + 1:02d} writing ID {ID} to {str(shelve_file)} Exception {e}")
            etld_lib_functions.logger.warning(f"issue writing ID:{ID} ")
            etld_lib_functions.logger.warning(f"issue writing to {str(shelve_file)} ")
            etld_lib_functions.logger.warning(f"exception: {e}")
            time.sleep(5)
            continue
        else:
            break # Success
    else:
        etld_lib_functions.logger.error(f"max retries attempted: {max_retries}")
        etld_lib_functions.logger.error(f"error writing ID:{ID} ")
        etld_lib_functions.logger.error(f"issue writing to file: {str(shelve_file)} ")
        exit(1)

    return True


def host_list_detection_shelve():
    global count_items_added_to_shelve
    global xml_dir
    global shelve_file
    global shelve_database
    global xml_dir_search_glob
    global xml_file_list
    global callback_item
    global counter_obj

    if Path(shelve_file).is_file():
        Path(shelve_file).unlink()  # Remove old host list detection shelve
    try:
        xml_file_list = sorted(Path(xml_dir).glob(xml_dir_search_glob))
        for xml_file in xml_file_list:
            with open(xml_file, 'r', encoding='utf-8') as t_xml_file:
                with shelve.open(str(shelve_file), flag='c') as shelve_database:
                    xmltodict.parse(t_xml_file.read(), item_depth=4,
                                    item_callback=callback_item)
    except Exception as e:
        etld_lib_functions.logger.error(f"XML File corruption detected: {xml_file}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def end_msg_host_list_detection_shelve():
    global count_items_added_to_shelve
    global shelve_file
    global xml_dir_search_glob
    global xml_dir
    global xml_file_list

    counter_obj.display_final_counter_to_log()
    etld_lib_functions.logger.info(
        f"total count host list detection records written to shelve: {count_items_added_to_shelve:,} for {str(shelve_file)}")
    for xml_file in xml_file_list:
        etld_lib_functions.log_file_info(xml_file, 'input file')
    etld_lib_functions.log_dbm_info(shelve_file)
    etld_lib_functions.log_file_info(shelve_file)
    etld_lib_functions.logger.info(f"end")


def start_msg_host_list_detection_shelve():
    etld_lib_functions.logger.info("start")


def main():
    start_msg_host_list_detection_shelve()
    setup_shelve_vars()
    host_list_detection_shelve()
    end_msg_host_list_detection_shelve()


def setup_shelve_vars():
    global count_items_added_to_shelve
    global host_list_detection_shelve_database
    global xml_dir
    global shelve_file
    global shelve_database
    global xml_dir_search_glob
    global callback_item
    global counter_obj
    count_items_added_to_shelve = 0
    callback_item = transform_xml_item_to_shelve
    shelve_file = etld_lib_config.host_list_detection_shelve_file
    xml_dir = etld_lib_config.host_list_detection_extract_dir
    shelve_database = etld_lib_config.host_list_detection_shelve_file
    xml_dir_search_glob = 'host_list_detection*.xml'
    counter_obj = \
        etld_lib_functions.DisplayCounterToLog(display_counter_at=10000,
                                               logger_func=etld_lib_functions.logger.info,
                                               display_counter_log_message=
                                               "count host list detection records written to shelve")


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_shelve')
    etld_lib_config.main()
    main()
