#  Copyright (c) 2020. Sinri Edogawa
from typing import Iterable, Optional, Union, List

from pymysql.cursors import Cursor

from nehushtan.mysql import constant
from nehushtan.mysql.constant import MYSQL_QUERY_ROW_TYPE_UNKNOWN


class MySQLQueryResult:

    def __init__(self, row_type: str):
        self._sql: str = ''
        self._status: str = constant.MYSQL_QUERY_STATUS_INIT
        self._error: str = 'Not executed yet!'

        self._last_inserted_id: int = -1
        self._affected_rows: int = -1
        self._result_rows: List[Union[tuple, dict]] = []
        self._result_stream: Optional[Cursor] = None

        self._row_type = row_type

    def is_queried(self) -> bool:
        return self._status == constant.MYSQL_QUERY_STATUS_QUERIED

    def is_executed(self) -> bool:
        return self._status == constant.MYSQL_QUERY_STATUS_EXECUTED

    def is_streamed(self) -> bool:
        return self._status == constant.MYSQL_QUERY_STATUS_STREAMED

    def get_last_inserted_id(self) -> int:
        return self._last_inserted_id

    def set_last_inserted_id(self, last_inserted_id: int):
        self._last_inserted_id = last_inserted_id
        return self

    def get_affected_rows(self) -> int:
        return self._affected_rows

    def set_affected_rows(self, affected_rows: int):
        self._affected_rows = affected_rows
        return self

    def get_sql(self) -> str:
        return self._sql

    def set_sql(self, sql: str):
        self._sql = sql
        return self

    def get_status(self) -> str:
        return self._status

    def set_status(self, status):
        self._status = status
        if (
                constant.MYSQL_QUERY_STATUS_QUERIED,
                constant.MYSQL_QUERY_STATUS_STREAMING,
                constant.MYSQL_QUERY_STATUS_STREAMED,
                constant.MYSQL_QUERY_STATUS_EXECUTED,
        ).__contains__(self._status):
            self._error = 'NO ERROR'
        return self

    def get_error(self) -> str:
        return self._error

    def set_error(self, error: str):
        self._error = error
        return self

    def append_result_rows(self, rows: Iterable[Union[tuple, dict]]):
        """

        :param rows: Array (list ot tuple) of result rows, each row would be a dict or tuple
        :return:
        """
        if type(rows) is tuple:
            rows = list(rows)
        self._result_rows += rows
        return self

    def set_stream(self, cursor: Cursor):
        self._result_stream = cursor
        return self

    def get_stream(self) -> Cursor:
        if self._result_stream is None:
            raise IOError("No available stream!")
        return self._result_stream

    def read_next_row(self):
        if self._status != constant.MYSQL_QUERY_STATUS_STREAMING:
            raise IOError("Now no stream to read!")
        row = self.get_stream().fetchone()
        if row is None:
            self._status = constant.MYSQL_QUERY_STATUS_STREAMED
            self._result_stream.close()
            del self._result_stream
            return None
        return row

    # def get_result(self):
    #     """
    #     Removed since 0.3.2
    #     """
    #     warnings.warn('Deprecated since 0.1.12. Use `get_fetched_rows_as_tuple` instead.', DeprecationWarning)
    #     if self._status != constant.MYSQL_QUERY_STATUS_QUERIED:
    #         raise Exception('Cannot fetch query result as status is not QUERIED.')
    #     return self._result_rows

    def get_fetched_rows_as_tuple(self):
        if self._status != constant.MYSQL_QUERY_STATUS_QUERIED:
            raise IOError('Cannot fetch query result as status is not QUERIED.')
        return tuple(self._result_rows)

    def get_column_from_fetched_rows_as_tuple(self, field_key) -> tuple:
        """
        Since 0.3.2
        """
        if self._status != constant.MYSQL_QUERY_STATUS_QUERIED:
            raise IOError('Cannot fetch query result as status is not QUERIED.')

        column = []
        for row in self._result_rows:
            x = row[field_key]
            column.append(x)

        return tuple(column)

    def get_fetched_first_row_as_tuple(self) -> tuple:
        """
        Since 0.3.2
        """
        if self._status != constant.MYSQL_QUERY_STATUS_QUERIED:
            raise IOError('Cannot fetch query result as status is not QUERIED.')
        if self._row_type != constant.MYSQL_QUERY_ROW_TYPE_TUPLE:
            raise AssertionError('Row format is not tuple')
        return self._result_rows[0]

    def get_fetched_first_row_as_dict(self) -> dict:
        """
        Since 0.3.2
        """
        if self._status != constant.MYSQL_QUERY_STATUS_QUERIED:
            raise IOError('Cannot fetch query result as status is not QUERIED.')
        if self._row_type != constant.MYSQL_QUERY_ROW_TYPE_DICT:
            raise AssertionError('Row format is not tuple')
        return self._result_rows[0]

    def get_fetched_first_cell(self, field_key):
        """
        Since 0.3.2
        """
        if self._status != constant.MYSQL_QUERY_STATUS_QUERIED:
            raise IOError('Cannot fetch query result as status is not QUERIED.')
        return self._result_rows[0][field_key]

    @staticmethod
    def create_error_result(error_message: str):
        return MySQLQueryResult(MYSQL_QUERY_ROW_TYPE_UNKNOWN) \
            .set_status(constant.MYSQL_QUERY_STATUS_ERROR) \
            .set_error(error_message)
