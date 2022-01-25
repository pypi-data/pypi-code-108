from whizbang.domain.manager.az.az_resource_manager_base import IAzResourceManager, AzResourceManagerBase
from whizbang.domain.models.sql.sql_database_resource import SqlServerDatabaseResource
from whizbang.domain.repository.az.az_sql_database_repository import IAzSqlDatabaseRepository


class IAzSqlDatabaseManager(IAzResourceManager):
    """"""

    def get_connection_string(self, database: SqlServerDatabaseResource, client_type: str,
                              username: str, password: str, auth_type: str = 'SqlPassword') -> str:
        """"""


class AzSqlDatabaseManager(AzResourceManagerBase, IAzSqlDatabaseManager):
    def __init__(self, repository: IAzSqlDatabaseRepository):
        AzResourceManagerBase.__init__(self, repository)
        self._repository: IAzSqlDatabaseRepository

    def get_connection_string(self, database: SqlServerDatabaseResource, client_type: str,
                              username: str, password: str, auth_type: str = 'SqlPassword') -> str:
        result = self._repository.get_connection_string(database=database, client_type=client_type, auth_type=auth_type)

        result_with_username = result.replace('<username>', username)
        connection_string = result_with_username.replace('<password>', password)

        return connection_string
