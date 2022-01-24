from abc import abstractmethod

import pymysql
from pymysql.cursors import SSDictCursor, SSCursor

from nehushtan.mysql import constant
from nehushtan.mysql.MySQLKit import MySQLKit
from nehushtan.mysql.MySQLQueryResult import MySQLQueryResult


class MySQLSelectionMixin:
    """
    Since 0.3.6
    """

    @abstractmethod
    def get_mysql_kit(self) -> MySQLKit:
        pass

    @abstractmethod
    def generate_sql(self) -> str:
        pass

    def query_for_result_matrix(self, row_type: type):
        result = MySQLQueryResult(self.parse_row_type_to_str(row_type))
        try:
            sql = self.generate_sql()
            result.set_sql(sql)
            if row_type is dict:
                matrix = self.get_mysql_kit().raw_query_for_all_dict_rows(sql)
            else:
                matrix = self.get_mysql_kit().raw_query_for_all_tuple_rows(sql)
            result.set_status(constant.MYSQL_QUERY_STATUS_QUERIED)
            result.append_result_rows(matrix)
        except pymysql.MySQLError as e:
            result.set_status(constant.MYSQL_QUERY_STATUS_ERROR)
            result.set_error(f"MySQL Error {e.__class__} [{e.args[0]}] {e.args[1]}")
        except Exception as pe:
            result.set_status(constant.MYSQL_QUERY_STATUS_ERROR)
            result.set_error(f"Python Error {pe.__class__}: {pe}")
        finally:
            return result

    def query_for_result_as_tuple_of_dict(self):
        return self.query_for_result_matrix(dict)

    def query_for_result_as_tuple_of_tuple(self):
        return self.query_for_result_matrix(tuple)

    def query_for_result_stream(self, row_type: type):
        result = MySQLQueryResult(self.parse_row_type_to_str(row_type))
        try:
            sql = self.generate_sql()
            result.set_sql(sql)
            if row_type is dict:
                cursor = self.get_mysql_kit().get_raw_connection().cursor(SSDictCursor)
            else:
                cursor = self.get_mysql_kit().get_raw_connection().cursor(SSCursor)
            cursor.execute(sql)
            result.set_status(constant.MYSQL_QUERY_STATUS_STREAMING)
            result.set_stream(cursor)
            return result
        except pymysql.MySQLError as e:
            result.set_status(constant.MYSQL_QUERY_STATUS_ERROR)
            result.set_error(f"MySQL Error {e.__class__} [{e.args[0]}] {e.args[1]}")
        except Exception as pe:
            result.set_status(constant.MYSQL_QUERY_STATUS_ERROR)
            result.set_error(f"Python Error {pe.__class__}: {pe}")
        finally:
            return result

    def query_for_result_stream_as_dict(self):
        return self.query_for_result_stream(row_type=dict)

    def query_for_result_stream_as_tuple(self):
        return self.query_for_result_stream(row_type=tuple)

    @staticmethod
    def parse_row_type_to_str(row_type: type):
        if row_type is dict:
            return constant.MYSQL_QUERY_ROW_TYPE_DICT
        elif row_type is tuple:
            return constant.MYSQL_QUERY_ROW_TYPE_TUPLE
        else:
            return constant.MYSQL_QUERY_ROW_TYPE_UNKNOWN
