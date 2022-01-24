from abc import ABC
from typing import List, Iterable

import pymysql

from nehushtan.mysql import constant
from nehushtan.mysql.MySQLCondition import MySQLCondition
from nehushtan.mysql.MySQLQueryResult import MySQLQueryResult
from nehushtan.mysql.MySQLViewMixin import MySQLViewMixin


class MySQLTableMixin(MySQLViewMixin, ABC):
    """
    This class is rewritten with the raw PyMySQL execute many method for multi-query.
    Since 0.1.17
    """

    @staticmethod
    def _build_on_duplicate_key_update_sql(on_duplicate_key_update_rows: dict):
        sql_parts = []
        for field, value in on_duplicate_key_update_rows.items():
            sql_parts.append(f'{field}={value}')
        sql_parts = ", ".join(sql_parts)
        return f'ON DUPLICATE KEY UPDATE {sql_parts}'

    def _modify_with_sql(self, sql_template: str, args: list = None, for_many_rows=False, commit_immediately=False):
        result = MySQLQueryResult(constant.MYSQL_QUERY_ROW_TYPE_UNKNOWN)
        cursor = None

        try:
            result.set_sql(sql_template)

            cursor = self.get_mysql_kit().get_raw_connection().cursor()

            if for_many_rows:
                cursor.executemany(sql_template, args)
            else:
                cursor.execute(sql_template, args)

            result.set_status(constant.MYSQL_QUERY_STATUS_EXECUTED)
            result.set_last_inserted_id(cursor.lastrowid)
            result.set_affected_rows(cursor.rowcount)
            if commit_immediately:
                self.get_mysql_kit().get_raw_connection().commit()

        except pymysql.MySQLError as e:
            result.set_status(constant.MYSQL_QUERY_STATUS_ERROR)
            result.set_error(f"MySQL Error {e.__class__}: [{e.args[0]}] {e.args[1]}")

        except Exception as pe:
            result.set_status(constant.MYSQL_QUERY_STATUS_ERROR)
            result.set_error(f"Python Error {pe.__class__}: {pe}")

        finally:
            if cursor is not None:
                cursor.close()
            return result

    def insert_one_row(
            self,
            row_dict: dict,
            commit_immediately: bool = False,
            on_duplicate_key_update_rows: dict = None,
            with_ignore: bool = False
    ):
        ignore_part = ''
        if with_ignore:
            ignore_part = ' IGNORE'

        table_expression = self.get_table_expression()

        field_names = []
        value_placeholders = []
        values = []
        for k, v in row_dict.items():
            field_names.append(f'`{k}`')
            value_placeholders.append("%s")
            values.append(v)

        field_names = ",".join(field_names)
        value_placeholders = ",".join(value_placeholders)

        on_duplicate_key_update_rows_part = ''
        if type(on_duplicate_key_update_rows) is dict:
            on_duplicate_key_update_rows_part = self._build_on_duplicate_key_update_sql(on_duplicate_key_update_rows)

        sql_template = f"""
            INSERT {ignore_part} INTO {table_expression} ({field_names}) 
            VALUES ({value_placeholders})
            {on_duplicate_key_update_rows_part}
        """

        return self._modify_with_sql(sql_template, values, False, commit_immediately)

    def replace_one_row(self, row_dict: dict, commit_immediately: bool = False):
        table_expression = self.get_table_expression()

        field_names = []
        value_placeholders = []
        values = []
        for k, v in row_dict.items():
            field_names.append(f'`{k}`')
            value_placeholders.append("%s")
            values.append(v)

        field_names = ",".join(field_names)
        value_placeholders = ",".join(value_placeholders)

        sql_template = f"""
            REPLACE INTO {table_expression} ({field_names})
            VALUES ({value_placeholders})
        """

        return self._modify_with_sql(sql_template, values, False, commit_immediately)

    def insert_many_rows_with_dicts(
            self,
            row_dicts: List[dict],
            commit_immediately: bool = False,
            on_duplicate_key_update_rows: dict = None,
            with_ignore: bool = False
    ):
        ignore_part = ''
        if with_ignore:
            ignore_part = ' IGNORE'

        table_expression = self.get_table_expression()

        field_names = []
        placeholders = []
        matrix = []

        first_row = row_dicts[0]
        for k, v in first_row.items():
            field_names.append(f'`{k}`')
            placeholders.append("%s")

        for row_dict in row_dicts:
            x = []
            for k, v in row_dict.items():
                x.append(v)
            matrix.append(x)

        field_names = ",".join(field_names)
        placeholders = ",".join(placeholders)

        on_duplicate_key_update_rows_part = ''
        if type(on_duplicate_key_update_rows) is dict:
            on_duplicate_key_update_rows_part = self._build_on_duplicate_key_update_sql(on_duplicate_key_update_rows)

        sql_template = f"""
            INSERT {ignore_part} INTO {table_expression} ({field_names})
            VALUES ({placeholders})
            {on_duplicate_key_update_rows_part}
        """

        return self._modify_with_sql(sql_template, matrix, True, commit_immediately)

    def replace_many_rows_with_dicts(self, row_dicts: List[dict], commit_immediately: bool = False):
        table_expression = self.get_table_expression()

        field_names = []
        placeholders = []
        matrix = []

        first_row = row_dicts[0]
        for k, v in first_row.items():
            field_names.append(f'`{k}`')
            placeholders.append("%s")

        for row_dict in row_dicts:
            x = []
            for k, v in row_dict.items():
                x.append(v)
            matrix.append(x)

        field_names = ",".join(field_names)
        placeholders = ",".join(placeholders)

        sql_template = f"""
            REPLACE INTO {table_expression} ({field_names})
            VALUES ({placeholders})
        """

        return self._modify_with_sql(sql_template, matrix, True, commit_immediately)

    def insert_many_rows_with_matrix(
            self,
            fields: List[str],
            row_matrix: List[List],
            commit_immediately: bool = False,
            on_duplicate_key_update_rows: dict = None,
            with_ignore: bool = False
    ):
        ignore_part = ''
        if with_ignore:
            ignore_part = ' IGNORE'

        table_expression = self.get_table_expression()

        field_names = ",".join([f'`{k}`' for k in fields])
        placeholders = ["%s"] * len(fields)
        placeholders = ",".join(placeholders)

        on_duplicate_key_update_rows_part = ''
        if type(on_duplicate_key_update_rows) is dict:
            on_duplicate_key_update_rows_part = self._build_on_duplicate_key_update_sql(on_duplicate_key_update_rows)

        sql_template = f"""
            INSERT {ignore_part} INTO {table_expression} ({field_names})
            VALUES ({placeholders})
            {on_duplicate_key_update_rows_part}
        """

        return self._modify_with_sql(sql_template, row_matrix, True, commit_immediately)

    def replace_many_rows_with_matrix(
            self,
            fields: List[str],
            row_matrix: List[List],
            commit_immediately: bool = False
    ):
        table_expression = self.get_table_expression()

        field_names = ",".join([f'`{k}`' for k in fields])
        placeholders = ["%s"] * len(fields)
        placeholders = ",".join(placeholders)

        sql_template = f"""
            REPLACE INTO {table_expression} ({field_names})
            VALUES ({placeholders})
        """

        return self._modify_with_sql(sql_template, row_matrix, True, commit_immediately)

    def write_rows_with_raw_selection_sql(
            self,
            write_type: str,
            fields: List[str],
            selection_sql: str,
            with_ignore: bool = False,
            on_duplicate_key_update_rows: dict = None,
            commit_immediately: bool = False
    ):
        """
        < Experimental Method, Since 0.1.10>
        It is a low level method for
        [INSERT ... SELECT Statement](https://dev.mysql.com/doc/refman/8.0/en/insert-select.html)
        and [REPLACE Statement](https://dev.mysql.com/doc/refman/8.0/en/replace.html)
        Be Careful when use this.
        :param write_type: INSERT or REPLACE
        :param fields:
        :param selection_sql: 'SELECT ...' If select from one table, you may use MySQLTableSelection::generate_sql()
        :param with_ignore:
        :param on_duplicate_key_update_rows:
        :param commit_immediately:
        :return:
        """

        ignore_part = ''
        if with_ignore:
            ignore_part = ' IGNORE'

        fields_sql = ",".join([f'`{k}`' for k in fields])

        on_duplicate_key_update_rows_part = ''
        if type(on_duplicate_key_update_rows) is dict:
            on_duplicate_key_update_rows_part = self._build_on_duplicate_key_update_sql(on_duplicate_key_update_rows)

        sql_template = f"""
            {write_type}{ignore_part} INTO {self.get_table_expression()} ({fields_sql}) 
            {selection_sql}
            {on_duplicate_key_update_rows_part}
        """

        return self._modify_with_sql(sql_template, commit_immediately=commit_immediately)

    def update_rows(
            self,
            conditions: Iterable[MySQLCondition],
            modifications: dict,
            commit_immediately: bool = False,
            with_ignore: bool = False,
            sort_expression: str = '',
            limit: int = 0
    ):
        """
        [UPDATE Statement](https://dev.mysql.com/doc/refman/8.0/en/update.html)
        :param conditions:
        :param modifications:
        :param commit_immediately:
        :param with_ignore:
        :param sort_expression:
        :param limit:
        :return:
        """
        condition_sql = MySQLCondition.build_sql_component(conditions)

        modify_pairs = []
        for k, v in modifications.items():
            modify_pairs.append(f'`{k}`=' + self.get_mysql_kit().quote(v))
        modify_pairs = ",".join(modify_pairs)

        ignore = ''
        if with_ignore:
            ignore = ' IGNORE'

        sql = f"UPDATE{ignore} {self.get_table_expression()} SET {modify_pairs} WHERE {condition_sql}"

        if len(sort_expression) > 0:
            sql = f"{sql} ORDER BY {sort_expression}"

        if limit > 0:
            sql = f"{sql} LIMIT {limit}"

        return self._modify_with_sql(sql, None, False, commit_immediately)

    def delete_rows(
            self,
            conditions: Iterable[MySQLCondition],
            commit_immediately: bool = False,
            with_ignore: bool = False,
            sort_expression: str = '',
            limit: int = 0
    ):
        """
        [DELETE Statement](https://dev.mysql.com/doc/refman/8.0/en/delete.html)
        :param conditions:
        :param commit_immediately:
        :param with_ignore:
        :param sort_expression:
        :param limit:
        :return:
        """

        condition_sql = MySQLCondition.build_sql_component(conditions)

        ignore = ''
        if with_ignore:
            ignore = ' IGNORE'

        sql = f"DELETE{ignore} FROM {self.get_table_expression()} WHERE {condition_sql}"

        if len(sort_expression) > 0:
            sql = f"{sql} ORDER BY {sort_expression}"

        if limit > 0:
            sql = f"{sql} LIMIT {limit}"

        return self._modify_with_sql(sql, None, False, commit_immediately)

    def truncate(self):
        sql_template = f"TRUNCATE {self.get_table_expression()}"
        return self._modify_with_sql(sql_template)
