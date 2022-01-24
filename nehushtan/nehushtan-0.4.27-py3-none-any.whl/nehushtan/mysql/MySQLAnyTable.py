#  Copyright (c) 2020. Sinri Edogawa

from nehushtan.mysql.MySQLKit import MySQLKit
from nehushtan.mysql.MySQLTableMixin import MySQLTableMixin


class MySQLAnyTable(MySQLTableMixin):

    def __init__(self, mysql_kit: MySQLKit, table_name: str, schema_name: str = ''):
        super().__init__()
        self._mysql_kit = mysql_kit
        self._table_name = table_name
        self._schema_name = schema_name

    def __del__(self):
        """
        Since 0.4.10
        """
        self._mysql_kit = None

    def get_mysql_kit(self) -> MySQLKit:
        return self._mysql_kit

    def mapping_table_name(self) -> str:
        return self._table_name

    def mapping_schema_name(self) -> str:
        return self._schema_name
