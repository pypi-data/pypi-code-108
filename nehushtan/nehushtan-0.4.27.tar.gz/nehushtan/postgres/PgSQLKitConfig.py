class PgSQLKitConfig:
    """
    Since 0.4.22
    """

    def __init__(self, config_dict: dict):
        # host – database host address (defaults to UNIX socket if not provided)
        # port – connection port number (defaults to 5432 if not provided)
        # dbname - the database name (database is a deprecated alias)
        # user – user name used to authenticate
        # password – password used to authenticate
        # autocommit - BOOL
        self.__config_dict = config_dict

    def dsn(self):
        dsn = []
        for k in ('host', 'port', 'dbname', 'user', 'password'):
            v = self.__config_dict.get(k)
            if v:
                dsn.append(f'{k}={v}')
        return ' '.join(dsn)

    def autocommit(self) -> bool:
        return self.__config_dict.get('autocommit') is True

    def __str__(self):
        return self.dsn()
