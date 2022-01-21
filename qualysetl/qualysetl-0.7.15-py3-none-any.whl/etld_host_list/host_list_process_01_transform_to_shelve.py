import shelve
import xmltodict
import time
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions

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
    ID = item['ID']
    # Retry logic to help with windows dbm.dumb slow writer.
    # TODO update for loop to else syntax.
    for i in range(5):
        try:
            host_list_shelve_database[ID] = item
            count_host_ids_added_to_shelve += 1
            counter_obj.display_counter_to_log()
            break
        except Exception as e:
            time.sleep(1)
            etld_lib_functions.logger.info(
                f"Retry #{i + 1:02d} writing ID {ID} to {str(etld_lib_config.host_list_shelve_file)} Exception {e}")
            if i > 4:
                etld_lib_functions.logger.error(f"Error Writing ID {ID} ")
                etld_lib_functions.logger.error(f"Error in File: {__file__} Line: {etld_lib_functions.lineno()}")
                etld_lib_functions.logger.error(f"Error writing to {str(etld_lib_config.kb_shelve_file)} ")
                etld_lib_functions.logger.error(f"Exception: {e}")
                exit(1)

    return True


def host_list_shelve():
    global count_host_ids_added_to_shelve
    global host_list_shelve_database
    global host_list_xml_files_selected
    global counter_obj

    count_host_ids_added_to_shelve = 0
    counter_obj = \
        etld_lib_functions.DisplayCounterToLog(display_counter_at=10000,
                                               logger_func=etld_lib_functions.logger.info,
                                               display_counter_log_message="count host list records written to shelve")

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
        counter_obj.display_final_counter_to_log()
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
