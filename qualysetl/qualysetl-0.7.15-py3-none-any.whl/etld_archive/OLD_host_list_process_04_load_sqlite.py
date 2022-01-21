from qualys_etl.etld_lib import etld_lib_config as etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables as etld_lib_sqlite_tables

global host_list_sqlite_file


def host_list_sqlite():
    global host_list_sqlite_file
    sqlite_host_list = etld_lib_sqlite_tables.SqliteObj(host_list_sqlite_file)
    sqlite_host_list.drop_and_recreate_table(etld_lib_config.host_list_table_name,
                                             etld_lib_config.host_list_csv_columns(),
                                             key='ID')

    sqlite_host_list.bulk_insert_csv_file(etld_lib_config.host_list_table_name,
                                          etld_lib_config.host_list_csv_file,
                                          etld_lib_config.host_list_csv_columns(),
                                          "host list")

    sqlite_host_list.commit_changes()
    sqlite_host_list.close_connection()
    etld_lib_functions.logger.info(f"count rows added to {etld_lib_config.host_list_table_name} table: "
                                   f"{sqlite_host_list.count_rows_added_to_table:,}")


def start_msg_host_list_sqlite():
    etld_lib_functions.logger.info(f"start")


def end_msg_host_list_sqlite():
    etld_lib_functions.log_file_info(etld_lib_config.host_list_csv_file, 'input file')
    etld_lib_functions.log_file_info(host_list_sqlite_file)
    etld_lib_functions.logger.info(f"end")


def setup_vars():
    global host_list_sqlite_file
    try:
        host_list_sqlite_file
    except:
        host_list_sqlite_file = etld_lib_config.host_list_sqlite_file


def main():
    start_msg_host_list_sqlite()
    setup_vars()
    host_list_sqlite()
    end_msg_host_list_sqlite()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_sqlite')
    etld_lib_config.main()
    main()

