import abc
from typing import Optional, Dict, Tuple, List

import pandas as pd

from pyrasgo.api.session import Session
from pyrasgo.storage.dataframe import utils as dfutils


class DataWarehouse(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def user_connection(self):
        pass

    @property
    @abc.abstractmethod
    def user_credentials(self):
        pass

    @abc.abstractmethod
    def get_source_table(self, table_name: str, database: Optional[str] = None, schema: Optional[str] = None,
                         record_limit: Optional[int] = None) -> pd.DataFrame:
        # TODO: This likely should not be "table" for s3 storage
        pass

    @abc.abstractmethod
    def get_source_tables(self, database: Optional[str] = None, schema: Optional[str] = None) -> pd.DataFrame:
        # TODO: This likely should not be "tables" for s3 storage
        pass

    @abc.abstractmethod
    def get_source_columns(self, table: Optional[str] = None, database: Optional[str] = None, schema: Optional[str] = None, data_type: Optional[str] = None) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def _write_dataframe_to_table(self, df: pd.DataFrame, *,
                                  table_name: str,
                                  append: Optional[bool] = False):
        pass

    @staticmethod
    def make_select_statement(
            table_metadata: Dict[str, str],
            filters: Optional[List[str]] = None,
            order_by: Optional[List[str]] = None,
            columns: Optional[List[str]] = None,
            limit: Optional[int] = None
    ) -> str:
        """
        Makes and returns SQL select statement, table_metadata param
        must include fqtn, or database + schema + table

        You can supply SQL WHERE clause filters, order the dataset by columns, only
        return selected columns, and add a return limit as well when crating the query

        Args:
            table_metadata:
            filters: List of SQL WHERE filters strings to filter on in query
            order_by: List of columns to order by in query
            columns: List of columns to return in the query
            limit: Limit the number of rows returned in the query
        """
        # Get table fqtn
        fqtn = table_metadata.get('fqtn')
        if not fqtn:
            fqtn = "{database}.{schema}.{table}".format(**table_metadata)

        # Create Initial select statement
        columns = ', '.join(columns) if columns else '*'
        query = f"SELECT {columns} FROM {fqtn} "

        # Add filters, orders, and limit if supplied
        if filters:
            query += "WHERE " + " AND ".join(filters) + " "
        if order_by:
            query += "ORDER BY " + ', '.join(order_by) + " "
        if isinstance(limit, int):
            query += f"LIMIT {limit}"

        return query.strip()

    @staticmethod
    def make_select_statement_filter_dict(
            table_metadata: Dict,
            filters: Dict,
            limit: Optional[int] = None,
            columns: str = '*'
    ) -> Tuple:
        """
        Constructs select * query for table

        Uses a a Filter Dict param type input over the List one
        on function make_select_statement() of this class
        """
        query = f"SELECT {columns} FROM "
        query += "{database}.{schema}.{table}".format(**table_metadata) if not 'fqtn' in table_metadata else table_metadata['fqtn']
        values = []
        if filters:
            comparisons = []
            for k, v in filters.items():
                if isinstance(v, list):
                    comparisons.append(f"{k} IN ({', '.join(['%s'] * len(v))})")
                    values += v
                elif v[:1] in ['>', '<', '='] \
                        or v[:2] in ['>=', '<=', '<>', '!='] \
                        or v[:4] == 'IN (' \
                        or v[:8] == 'BETWEEN ':
                    comparisons.append(f'{k} {v}')
                else:
                    comparisons.append(f"{k}=%s")
                    values.append(v)
            query += " WHERE " + " and ".join(comparisons)
        if limit:
            query += " LIMIT {}".format(limit)
        return query, values

    @classmethod
    def connect(cls):
        """
        Returns an instance of the account's Data Warehouse connection
        :param session: Session object describing the current user's session
        :return:
        """
        # TODO: Provide the setup for other warehouses here:
        from pyrasgo.storage import SnowflakeDataWarehouse

        return SnowflakeDataWarehouse()

    def write_dataframe_to_table(self, df: pd.DataFrame, *,
                                 table_name: str,
                                 append: Optional[bool] = False):
        with self.user_connection.cursor() as cursor:
            cursor.execute(dfutils.generate_ddl(df=df, table_name=table_name, append=append))
        self._write_dataframe_to_table(df=df, table_name=table_name, append=append)


class DataWarehouseSession(type(DataWarehouse), type(Session)):
    pass
