import sqlite3
import re
import csv
import sys
import json
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config
global count_rows_added_to_table


def get_q_knowledgebase_min_max_dates(sqlite_file):
    min_date = None
    max_date = None
    try:
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        select_statement = 'select min(LAST_SERVICE_MODIFICATION_DATETIME) MIN_DATE, ' \
                           'max(LAST_SERVICE_MODIFICATION_DATETIME) MAX_DATE ' \
                           'from Q_KnowledgeBase;'
        cursor.execute(select_statement)
        records = cursor.fetchall()
        for row in records:
            min_date = row[0]
            max_date = row[1]
        conn.close()
    except Exception as e:
        min_date = 'Not Found'
        max_date = 'Not Found'

    return min_date, max_date


def get_q_table_min_max_dates(sqlite_file, datetime_field_name, table_name):
    min_date = None
    max_date = None
    try:
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        select_statement = f'select min({datetime_field_name}) MIN_DATE, ' \
                           f'max({datetime_field_name}) MAX_DATE ' \
                           f'from {table_name};'
        cursor.execute(select_statement)
        records = cursor.fetchall()
        for row in records:
            min_date = row[0]
            max_date = row[1]
        conn.close()
    except Exception as e:
        min_date = 'Not Found'
        max_date = 'Not Found'

    return min_date, max_date


def create_table_q_knowledgebase_in_host_list_detection():

    table_name = 'Q_KnowledgeBase_In_Host_List_Detection'
    kb_table_name = 'Q_KnowledgeBase'
    table_statement = f'CREATE TABLE {table_name} as ' \
                      f'select * from {kb_table_name} ' \
                      f'where QID in (select distinct(QID) from Q_Host_List_Detection);'
    try:

        conn = sqlite3.connect()
        conn.execute(f"DROP TABLE IF EXISTS {table_name};")
        conn.execute(table_statement)
        conn.execute(f"DROP TABLE IF EXISTS {kb_table_name};")
        conn.commit()
        conn.close()
        conn = sqlite3.connect(sqlite_file)
        conn.isolation_level = None
        conn.execute("VACUUM")
        conn.close()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error creating table: {table_name}, please retry after fixing error")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


class SqliteObj:
    def __init__(self, sqlite_file, read_only=False):
        self.sqlite_file = str(sqlite_file)
        self.read_only = read_only
        self.connection = None
        self.cursor = None
        self.isolation_level = None
        self.count_rows_added_to_table = 0
        self.status_table_recreated = False
        self.open_connection_and_cursor(read_only=read_only)

    def open_connection_and_cursor(self, read_only=False, open_cursor=True, enable_row_factory=True):
        try:
            if read_only is True and Path(self.sqlite_file).exists:
                self.connection = sqlite3.connect(f'file:{str(self.sqlite_file)}?mode=ro', uri=True, timeout=300)
            else:
                self.connection = sqlite3.connect(database=self.sqlite_file, timeout=300)
            if enable_row_factory is True:
                self.connection.row_factory = sqlite3.Row
            if open_cursor is True:
                self.cursor = self.connection.cursor()

        except Exception as e:
            etld_lib_functions.logger.error(f"Error getting cursor obj: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    def attach_database_to_connection(self, database_as_name, database_sqlite_file: str, mode='ro'):
        attach_database_sql = f'ATTACH DATABASE ? AS {database_as_name}'
        # unsupported on redhat 8.4 self.connection.execute(attach_database_sql, (f'file:{str(database_sqlite_file)}?mode={mode}',))
        try:
            self.connection.execute(attach_database_sql, (str(database_sqlite_file),))
        except sqlite3.Error as err:
            etld_lib_functions.logger.error(f"sqlite3.Error attaching database: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {err}")
            exit(1)
        except Exception as e:
            etld_lib_functions.logger.error(f"Error attaching database: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    def get_table_columns(self, table_name) -> list:
        try:
            sql = f"select * from {table_name} where 1=0;"
            self.cursor.execute(sql)
            return [d[0] for d in self.cursor.description]
        except Exception as e:
            etld_lib_functions.logger.info(f"Table not found: {table_name}")
            etld_lib_functions.logger.info(f"Exception: {e}")
            return []

    def get_min_max_dates_from_table_column(self, table_name, column_name):
        select_statement = f'select min({column_name}) MIN_DATE, ' \
                           f'max({column_name}) MAX_DATE ' \
                           f'from {table_name};'
        self.cursor.execute(select_statement)
        records = self.cursor.fetchall()
        min_date=""
        max_date=""
        if len(records) == 1:
            min_date = records[0][0]
            max_date = records[0][1]
        return {'min_date': min_date, 'max_date': max_date}

    def execute_statement(self, statement):
        self.cursor.execute(f"{statement};")

    def reopen_connection_and_cursor_as_sqlite3_row_factory(self):
        self.close_connection()
        try:
            self.connection = sqlite3.connect(database=self.sqlite_file, timeout=300)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
        except Exception as e:
            etld_lib_functions.logger.error(f"Error getting row factory connnection cursor obj: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    def create_table(self,
                     table_name=None, csv_columns=[],
                     key=False, csv_column_types={}):
        try:
            if key is False:
                table_statement = self.create_table_statement_no_primary_key(table_name, csv_columns)
            else:
                table_statement = self.create_table_statement(key, table_name, csv_columns, csv_column_types)

            self.cursor.execute(table_statement)
            table_statement_one_line = table_statement.replace("\n", " ")
            etld_lib_functions.logger.info(f"sqlite create table statement: {table_statement_one_line}")
            self.connection.commit()
        except Exception as e:
            etld_lib_functions.logger.error(f"Error creating table: {table_name}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    def drop_and_recreate_table(self,
                                table_name=None, csv_columns=[],
                                key=False, csv_column_types={}):
        try:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            if key is False:
                table_statement = \
                    self.create_table_statement_no_primary_key_and_column_types(
                        table_name, csv_columns, csv_column_types)
            else:
                table_statement = self.create_table_statement(key, table_name, csv_columns, csv_column_types)

            self.cursor.execute(table_statement)
            table_statement_one_line = table_statement.replace("\n", " ")
            etld_lib_functions.logger.info(f"sqlite create table statement: {table_statement_one_line}")
            self.connection.commit()
        except Exception as e:
            etld_lib_functions.logger.error(f"Error creating table: {table_name}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    @staticmethod
    def create_table_statement(primary_key, table_name, csv_columns, csv_column_types={}):
        table_statement = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        primary_keys = ""
        if isinstance(primary_key, list):
            pass
        elif primary_key in csv_column_types.keys():
            table_statement = f"{table_statement}{primary_key} {csv_column_types[primary_key]} PRIMARY KEY NOT NULL,\n"
        else:
            table_statement = f"{table_statement}{primary_key} CHAR PRIMARY KEY NOT NULL,\n"

        for column in csv_columns:
            if isinstance(primary_key, list) or primary_key != column:
                if column in csv_column_types.keys():
                    column_type = csv_column_types[column]
                    table_statement = f"{table_statement}{column} {column_type},\n"
                else:
                    table_statement = f"{table_statement}{column} TEXT,\n"

        table_statement = f"{table_statement}Row_Last_Updated TEXT,\n"

        table_statement = re.sub(",\n$", "", table_statement)

        if isinstance(primary_key, list):
            primary_keys = ", ".join(primary_key)
            table_statement = f"{table_statement},\nPRIMARY KEY ({primary_keys})\n"

        table_statement = table_statement + ");"
        return table_statement

    @staticmethod
    def create_table_statement_no_primary_key_and_column_types(table_name, csv_columns, csv_column_types={}):
        table_statement = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        for column in csv_columns:
            if column in csv_column_types.keys():
                column_type = csv_column_types[column]
                table_statement = f"{table_statement}{column} {column_type},\n"
            else:
                table_statement = f"{table_statement}{column} TEXT,\n"

        table_statement = f"{table_statement}Row_Last_Updated TEXT,\n"

        table_statement = re.sub(",\n$", "", table_statement)

        table_statement = table_statement + ");"
        return table_statement

    @staticmethod
    def create_table_statement_no_primary_key(table_name, csv_columns):
        table_statement_list = []
        table_statement_list.append(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
        for column in csv_columns:
            table_statement_list.append(f"{column} TEXT,\n")
        table_statement_list.append(f"Row_Last_Updated TEXT")
        table_statement_list.append(");")
        table_statement = "".join(table_statement_list)
        return table_statement

    def insert_or_replace_row(self, table_name: str, row: list):
        result = True
        try:
            self.cursor.execute(f"INSERT OR REPLACE INTO {table_name} "
                                f"VALUES({self.get_values_var(row)},datetime('now','utc'))",
                                row)
        except Exception as e:
            etld_lib_functions.logger.error(
                f"Error inserting or replacing row into table: {table_name}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)
        return result

    def insert_unique_row_ignore_duplicates(self, table_name: str, row: list):
        result = True
        try:
            self.cursor.execute(f"INSERT INTO {table_name} VALUES({self.get_values_var(row)},datetime('now','utc'))", row)
        except sqlite3.IntegrityError as err:
            if 'unique constraint failed' in str(err).lower():
                result = "duplicate"
                pass
            else:
                etld_lib_functions.logger.error(
                    f"Integrity Error inserting into: {table_name}, please retry after fixing error")
                etld_lib_functions.logger.error(f"Exception: {err}")
                exit(1)

        except sqlite3.Error as err:
            etld_lib_functions.logger.error(
                f"Error inserting row into table: {table_name}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {err}")
            exit(1)
        except Exception as e:
            etld_lib_functions.logger.error(
                f"Error inserting row into table: {table_name}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)
        return result

    def insert_unique_row(self, table_name: str, values_var: list, row: list, conflict: str):
        try:
            self.cursor.execute(f"INSERT INTO {table_name} VALUES({values_var},datetime('now','utc'))", row)
        except sqlite3.Error as err:
            etld_lib_functions.logger.error(
                f"Error inserting row into table: {table_name}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {err}")
            exit(1)
        except Exception as e:
            etld_lib_functions.logger.error(
                f"Error inserting row into table: {table_name}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    def commit_changes(self):
        try:
            self.connection.commit()
        except Exception as e:
            etld_lib_functions.logger.error(
                f"Error committing to: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    def close_connection(self):
        try:
            self.connection.close()
        except Exception as e:
            etld_lib_functions.logger.error(
                f"Error closing: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    def vacuum_database(self):
        try:
            self.isolation_level = self.connection.isolation_level
            self.connection.isolation_level = None
            self.connection.execute("VACUUM")
            self.connection.isolation_level = self.isolation_level
        except Exception as e:
            etld_lib_functions.logger.error(
                f"Error vacuuming database: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    def select_all_from_table(self, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        return self.cursor.fetchall()

    def select_all_from_table_where_table_column_equals_value(
            self, table_name, table_column, where_table_column_equals_value):
        self.cursor.execute(f"SELECT * FROM {table_name} WHERE {table_column} LIKE '{where_table_column_equals_value}'")
        return self.cursor.fetchall()

    @staticmethod
    def get_values_var(csv_columns: list):
        values_var = ""
        for column in csv_columns:
            values_var = f"{values_var}?, "
        values_var = re.sub("\?, $", "?", values_var)
        return values_var

    @staticmethod
    def status_table_prepare_fields_for_update(status_name='HOST_LIST_LOAD_STATUS', batch_date="", batch_number=0,
                                               status='COMPLETED', total_rows_added=0):
        status_name = status_name
        status_detail_dict = {'BATCH_DATE': batch_date, 'BATCH_NUMBER': batch_number, 'STATUS': status,
                              'TOTAL_ROWS_ADDED': total_rows_added}
        status_count = int(batch_number)
        return status_name, status_detail_dict, status_count

    def status_table_insert_or_replace_row_in_sqlite(self,
                                                     table_name: str, status_name: str, status_detail_dict: dict,
                                                     status_count: int, commit_changes: bool = True):
        status_detail_json = json.dumps(status_detail_dict)
        row_to_insert = [status_name,
                         status_detail_json,
                         status_count]
        result = self.insert_or_replace_row(
            table_name=table_name,
            row=row_to_insert
        )
        if commit_changes is True:
            self.commit_changes()

    def status_table_select_status_row_from_sqlite(self,
                                                   table_name: str, table_column: str,
                                                   where_table_column_equals_value: str):
        result = self.select_all_from_table_where_table_column_equals_value(
            table_name=table_name,
            table_column=table_column,
            where_table_column_equals_value=where_table_column_equals_value
        )
        status_name = result[0]['STATUS_NAME']
        status_detail_dict = json.loads(result[0]['STATUS_DETAIL'])
        status_count = result[0]['STATUS_COUNT']
        return status_name, status_detail_dict, status_count

    def update_status_table(self,
                            batch_date: str,
                            batch_number: int,
                            total_rows_added_to_database: int,
                            status_table_name: str,
                            status_table_columns: list,
                            status_table_column_types: list,
                            status_name_column: str = 'HOST_LIST_LOAD_STATUS',
                            status_column: str = 'begin'):

        status_column_dict = {'begin': 'BEGIN LOADING BATCH',
                              'end': 'END LOADING BATCH',
                              'final': 'FINAL BATCH LOADED',
                              }

        if status_column in status_column_dict.keys():
            status_column_display = status_column_dict[status_column]
        else:
            status_column_display = status_column

        status_name, status_detail_dict, status_count = \
            self.status_table_prepare_fields_for_update(
                status_name=status_name_column,
                batch_date=batch_date,
                batch_number=batch_number,
                status=status_column_display,
                total_rows_added=total_rows_added_to_database)

        self.status_table_insert_or_replace_row_in_sqlite(
            table_name=status_table_name,
            status_name=status_name, status_detail_dict=status_detail_dict, status_count=status_count
        )
        status_name, status_detail_dict, status_count = \
            self.status_table_select_status_row_from_sqlite(
                table_name=status_table_name,
                table_column='STATUS_NAME',
                where_table_column_equals_value=status_name)
        etld_lib_functions.logger.info(f"Updated {status_table_name} - "
                                       f"status_name={status_name} - status_detail_dict={status_detail_dict}")

        return status_name, status_detail_dict, status_count

    def bulk_insert_csv_file(self, table_name, csv_file_name, csv_columns, message="",
                             display_progress_counter_at_this_number=10000):
        csv.field_size_limit(sys.maxsize)
        sqlite_rows_written = \
            etld_lib_functions.DisplayCounterToLog(
                display_counter_at=display_progress_counter_at_this_number,
                logger_func=etld_lib_functions.logger.info,
                display_counter_log_message=f"count {table_name} sqlite rows written")
        # etld_lib_functions.logger.info(f"csv.field_size_limit(sys.maxsize): {str(sys.maxsize)}")
        try:
            values_var = ""
            for column in csv_columns:
                values_var = f"{values_var}?, "
            values_var = re.sub("\?, $", "?", values_var)
            csv_headers = ""
            csv_row_list = []
            bulk_insert_count = 100000
            with open(csv_file_name, "r", encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                self.count_rows_added_to_table = 0
                csv_headers = next(csv_reader)  # Skip Header
                for row in csv_reader:
                    self.cursor.execute(
                        f"INSERT OR REPLACE INTO {table_name} VALUES({values_var},datetime('now','utc'))", row)
                    sqlite_rows_written.display_counter_to_log()
                    self.count_rows_added_to_table += 1
                self.commit_changes()
                sqlite_rows_written.display_final_counter_to_log()

        except sqlite3.Error as err:
            etld_lib_functions.logger.error(
                f"Error inserting row into table: {table_name}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {err}")
            exit(1)
        except Exception as e:
            etld_lib_functions.logger.error(f"Error creating table from: {csv_file_name}, retry after fixing error")
            etld_lib_functions.logger.error(f"Row Number: {self.count_rows_added_to_table}")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)
