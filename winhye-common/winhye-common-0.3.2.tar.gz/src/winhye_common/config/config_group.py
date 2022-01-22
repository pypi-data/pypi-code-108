from .apollo_client import ApolloClient


class ConfigGroup(object):
    """
    Config group, supporting <group>.<item> operation to get value conveniently

    :param client: ApolloClient, pyapollo client
    :param namespace: str, config namespace
    :param group: str, config common prefix
    """
    def __init__(self, client: ApolloClient, namespace: str, group: str):
        self._client = client
        self._namespace = namespace
        self._group = group

    def __getattr__(self, item):
        return self._client.get_value("{group}.{item}".format(group=self._group, item=item), namespace=self._namespace)

    def to_connection_string(self, dialect: str) -> str:
        """
        Convert config_group to connection string for database configs

        :param dialect: str, identifying name of the dialect, such as sqlite, mysql, postgresql, oracle, or mssql.
        :return:
        """
        driver = "mysqldb" if dialect == "mysql" else "psycopg2"
        try:
            return "{dialect}+{driver}://{user}:{password}@{host}:{port}/{db_name}".format(
                dialect=dialect, driver=driver,
                user=self._client.get_value("{group}.db_user".format(group=self._group), namespace=self._namespace),
                password=self._client.get_value("{group}.db_passwd".format(group=self._group), namespace=self._namespace),
                host=self._client.get_value("{group}.db_host".format(group=self._group), namespace=self._namespace),
                port=self._client.get_value("{group}.db_port".format(group=self._group), namespace=self._namespace),
                db_name=self._client.get_value("{group}.db_name".format(group=self._group), namespace=self._namespace)
            )
        except:
            return ""
