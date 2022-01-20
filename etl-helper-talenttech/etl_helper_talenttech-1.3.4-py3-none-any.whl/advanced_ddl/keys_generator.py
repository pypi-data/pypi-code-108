from sqlalchemy.sql import func
from sqlalchemy import Table, select, distinct, inspect


class KeysGenerator:
    def __init__(self, db_worker):
        """
        Search and set primary key for table
        :param converter:
        :param mult_index:
        """
        self.db_worker = db_worker
        self.inspect = inspect(self.db_worker.engine)

    def get_pk_constraint(self, table_name):
        if (
            "constrained_columns" in self.inspect.get_pk_constraint(table_name)
            and len(self.inspect.get_pk_constraint(table_name)["constrained_columns"])
            > 0
        ):
            return self.inspect.get_pk_constraint(table_name)["constrained_columns"][0]
        columns = self.db_worker.get_columns(table_name)
        if "id" in columns and self.__check_identity(
            table_name=table_name, column="id"
        ):
            return "id"
        else:
            return []

    def __check_identity(self, table_name, column=None):
        table_sql = Table(table_name, self.db_worker.meta)
        select_st = select(
            [
                func.count(distinct(table_sql.c[column])).label(
                    "count_distinct_" + column
                ),
                func.count(table_sql.c[column]).label("count_" + column),
            ]
        )

        res = self.db_worker.conn.execute(select_st)
        res_lst = [dict(r) for r in res]
        count_distinct = res_lst[0]["count_distinct_id"]
        count = res_lst[0]["count_id"]
        if count_distinct == count:
            return True
        else:
            return False
