from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables as etld_lib_sqlite_tables

global kb_sqlite_file


def kb_sqlite():
    global kb_sqlite_file
    sqlite_kb = etld_lib_sqlite_tables.SqliteObj(etld_lib_config.kb_sqlite_file)
    sqlite_kb.drop_and_recreate_table(etld_lib_config.kb_table_name,
                                      etld_lib_config.kb_csv_columns(),
                                      key='QID')
    sqlite_kb.bulk_insert_csv_file(etld_lib_config.kb_table_name,
                                   etld_lib_config.kb_csv_file,
                                   etld_lib_config.kb_csv_columns(),
                                   "knowledgebase")

    sqlite_kb.commit_changes()
    sqlite_kb.close_connection()
    etld_lib_functions.logger.info(f"count rows added to {etld_lib_config.kb_table_name} table: "
                                   f"{sqlite_kb.count_rows_added_to_table:,}")


def start_msg_kb_sqlite():
    etld_lib_functions.logger.info(f"start")


def setup_vars():
    global kb_sqlite_file
    # Location of kb_sqlite_file can be injected prior to running main.
    try:
        kb_sqlite_file
    except:
        kb_sqlite_file = etld_lib_config.kb_sqlite_file


def end_msg_kb_sqlite():
    global kb_sqlite_file

    etld_lib_functions.log_file_info(etld_lib_config.kb_csv_file, 'in')
    etld_lib_functions.log_file_info(kb_sqlite_file)
    etld_lib_functions.logger.info(f"end")


def main():
    start_msg_kb_sqlite()
    setup_vars()
    kb_sqlite()
    end_msg_kb_sqlite()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='kb_load_sqlite')
    etld_lib_config.main()
    main()
