import csv
import shelve
from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions

global count_cve_qid_rows_written


def kb_cve_qid_csv_report():
    global count_cve_qid_rows_written
    count_cve_qid_rows_written = 0
    counter_obj = \
        etld_lib_functions.DisplayCounterToLog(display_counter_at=10000,
                                               logger_func=etld_lib_functions.logger.info,
                                               display_counter_log_message=
                                               "count knowledgebase cve->qid list records written to csv")
    kb_cve_qid_file = str(etld_lib_config.kb_cve_qid_file)
    csv_columns = ['CVE', 'QID_LIST']
    csv_headers = {}
    for header in csv_columns:
        csv_headers[header] = ""
    try:
        with open(kb_cve_qid_file, 'w', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            csv_record = csv_headers.copy()
            with shelve.open(str(etld_lib_config.kb_cve_qid_map_shelve), flag='r') as kb_cve_qid_list:
                for kb_cve_qid in kb_cve_qid_list.keys():
                    csv_record['CVE'] = kb_cve_qid
                    csv_record['QID_LIST'] = kb_cve_qid_list[kb_cve_qid]
                    writer.writerow(csv_record)
                    count_cve_qid_rows_written = count_cve_qid_rows_written + 1
                    counter_obj.display_counter_to_log()
                    csv_record = csv_headers.copy()
        counter_obj.display_final_counter_to_log()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error in File: {__file__} Line: {etld_lib_functions.lineno()}")
        etld_lib_functions.logger.error(f"Error writing to file: {str(kb_cve_qid_file)}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def start_msg_kb_cve_qid_csv():
    etld_lib_functions.logger.info(f"start")


def end_msg_kb_cve_qid_csv():
    global count_cve_qid_rows_written
    etld_lib_functions.logger.info(f"count cve -> qid list rows written to csv: {count_cve_qid_rows_written:,}")
    etld_lib_functions.log_file_info(etld_lib_config.kb_cve_qid_map_shelve, 'in')
    etld_lib_functions.log_dbm_info(etld_lib_config.kb_cve_qid_map_shelve)
    etld_lib_functions.log_file_info(etld_lib_config.kb_cve_qid_file)
    etld_lib_functions.logger.info(f"end")


def kb_cve_qid_csv():
    kb_cve_qid_csv_report()


def main():
    start_msg_kb_cve_qid_csv()
    kb_cve_qid_csv_report()
    end_msg_kb_cve_qid_csv()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='kb_load_cve_qid_csv')
    etld_lib_config.main()
    main()
