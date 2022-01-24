from nehushtan.mysql.MySQLKit import MySQLKit
from nehushtan.mysql.MySQLViewMixin import MySQLViewMixin


class MySQLAnyView(MySQLViewMixin):
    """
    Since 0.2.17
    """

    def __init__(self, mysql_kit: MySQLKit, view_name: str, schema_name: str = ''):
        super().__init__()
        self.__mysql_kit = mysql_kit
        self.__view_name = view_name
        self.__schema_name = schema_name

    def __del__(self):
        """
        Since 0.4.10
        """
        self.__mysql_kit = None

    def get_mysql_kit(self) -> MySQLKit:
        return self.__mysql_kit

    def mapping_table_name(self) -> str:
        return self.__view_name

    def mapping_schema_name(self) -> str:
        return self.__schema_name
