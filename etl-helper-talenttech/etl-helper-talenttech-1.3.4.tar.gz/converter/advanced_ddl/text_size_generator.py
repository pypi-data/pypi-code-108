import math
import time
from sqlalchemy.sql import func
from sqlalchemy import Table, select

from converter.config.config_converter import base_converter_params


def round_nearest_large(x, num=50):
    if x == 0:
        return num
    else:
        return math.ceil(x / num) * num


class TextSizeGenerator:
    def __init__(self, db_worker, query_limit_sec=60, mult_index=1):
        """
        class for generating text fiels sizes by using historing values
        :param converter:
        :param mult_index:
        """
        self.mult_index = mult_index
        self.db_worker = db_worker
        self.query_limit_sec = query_limit_sec

    def __get_text_fields(self, table_name):
        columns = self.db_worker.get_columns(table_name)
        string_columns = []
        for s in columns:
            if (
                "text" in base_converter_params[self.db_worker.db]
                and columns[s] in base_converter_params[self.db_worker.db]["text"]
            ):
                if s != "date":
                    string_columns.append(s)
        return string_columns

    def __get_string_size(self, table, column):
        table_sql = Table(table, self.db_worker.meta)
        select_st = select(
            [func.max(func.length(table_sql.c[column])).label(column)]
        )  # create select from deleted table
        # print(select_st)
        res = self.db_worker.conn.execute(select_st)
        res_max = [r[0] for r in res][0]
        if res_max is None:
            res_max = 100
        return {column: round_nearest_large(int(res_max * self.mult_index))}

    def get_text_sizes(self, table):
        result = {}
        string_columns = self.__get_text_fields(table)
        start_time = time.time()
        for column in string_columns:
            result.update(self.__get_string_size(table, column))
            if (time.time() - start_time) > self.query_limit_sec:
                return {}
        return result
