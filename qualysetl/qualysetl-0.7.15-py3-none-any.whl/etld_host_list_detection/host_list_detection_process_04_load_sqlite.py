from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables as etld_lib_sqlite_tables
from qualys_etl.etld_knowledgebase import knowledgebase_process_04_load_sqlite
from qualys_etl.etld_host_list import host_list_process_04_load_sqlite
from qualys_etl.etld_lib import etld_lib_sqlite_tables

global host_list_detection_updated_csv_columns


def host_list_detection_sqlite():
    global host_list_detection_updated_csv_columns
    sqlite_host_list_detection = etld_lib_sqlite_tables.SqliteObj(etld_lib_config.host_list_detection_sqlite_file)

    sqlite_host_list_detection.create_table_statement_no_primary_key(etld_lib_config.host_list_detection_table_name,
                                                                     host_list_detection_updated_csv_columns)

    sqlite_host_list_detection.bulk_insert_csv_file(etld_lib_config.host_list_detection_table_name,
                                                    etld_lib_config.host_list_detection_csv_file,
                                                    host_list_detection_updated_csv_columns,
                                                    "host list detection",
                                                    display_progress_counter_at_this_number=100000)
    sqlite_host_list_detection.commit_changes()
    sqlite_host_list_detection.close_connection()
    etld_lib_functions.logger.info(f"count rows added to {etld_lib_config.host_list_detection_table_name} table: "
                                   f"{sqlite_host_list_detection.count_rows_added_to_table:,}")


def start_msg_host_list_detection_sqlite():
    etld_lib_functions.logger.info(f"start")


def end_msg_host_list_detection_sqlite():
    etld_lib_functions.log_file_info(etld_lib_config.host_list_detection_csv_file, 'in')
    etld_lib_functions.log_file_info(etld_lib_config.host_list_detection_sqlite_file)
    etld_lib_functions.logger.info(f"end")


def combine_csv_columns_host_and_detection():
    global host_list_detection_updated_csv_columns
    csv_host_columns = etld_lib_functions.host_list_detection_csv_columns()
    csv_host_detection_columns = etld_lib_functions.host_list_detection_qid_csv_columns()
    csv_columns = csv_host_columns + csv_host_detection_columns
    idx = 0
    for column in csv_host_columns:
        if column in 'DETECTION_LIST':
            csv_columns.__delitem__(idx)
        idx = idx + 1
    host_list_detection_updated_csv_columns = csv_columns


def main():
    start_msg_host_list_detection_sqlite()
    combine_csv_columns_host_and_detection()
    host_list_detection_sqlite()
    knowledgebase_process_04_load_sqlite.kb_sqlite_file = etld_lib_config.host_list_detection_sqlite_file
    knowledgebase_process_04_load_sqlite.main()
    host_list_process_04_load_sqlite.host_list_sqlite_file = etld_lib_config.host_list_detection_sqlite_file
    host_list_process_04_load_sqlite.main()
    etld_lib_sqlite_tables.create_table_q_knowledgebase_in_host_list_detection(
        etld_lib_config.host_list_detection_sqlite_file)
    end_msg_host_list_detection_sqlite()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_sqlite')
    etld_lib_config.main()
    main()
