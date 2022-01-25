import pymysql

import connection_pool


class DbConfigurer():
    __data: dict = {
        "creator": pymysql,
        "maxconnections": 6,
        "mincached": 2,
        "maxcached": 5,
        "maxshared": 3,
        "blocking": True,
        "maxusage": None,
        "setsession": [],
        "ping": 0,
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "123456",
        "database": "test",
        "charset": "utf8",
        "cursor": pymysql.cursors.DictCursor
    }

    def end(self) -> None:
        connection_pool._init_pool(**self.__data)

    def set_creator(self, creator) -> 'DbConfigurer':
        self.__data['creator'] = creator
        return self

    def set_maxconnections(self, maxconnections: int) -> 'DbConfigurer':
        self.__data['maxconnections'] = maxconnections
        return self

    def set_mincached(self, mincached: int) -> 'DbConfigurer':
        self.__data['mincached'] = mincached
        return self

    def set_maxcached(self, maxcached: int) -> 'DbConfigurer':
        self.__data['maxcached'] = maxcached
        return self

    def set_maxshared(self, maxshared: int) -> 'DbConfigurer':
        self.__data['maxshared'] = maxshared
        return self

    def set_blocking(self, blocking: bool) -> 'DbConfigurer':
        self.__data['blocking'] = blocking
        return self

    def set_maxusage(self, maxusage: int) -> 'DbConfigurer':
        self.__data['creator'] = maxusage
        return self

    def set_setsession(self, setsession: list[str]) -> 'DbConfigurer':
        self.__data['setsession'] = setsession
        return self

    def set_host(self, host: str) -> 'DbConfigurer':
        self.__data['host'] = host
        return self

    def set_port(self, port: int) -> 'DbConfigurer':
        self.__data['port'] = port
        return self

    def set_user(self, user: str) -> 'DbConfigurer':
        self.__data['user'] = user
        return self

    def set_password(self, password: str) -> 'DbConfigurer':
        self.__data['password'] = password
        return self

    def set_database(self, database: str) -> 'DbConfigurer':
        self.__data['database'] = database
        return self

    def set_charset(self, charset: str) -> 'DbConfigurer':
        self.__data['charset'] = charset
        return self

    def set_cursor(self, cursor) -> 'DbConfigurer':
        self.__data['cursor'] = cursor
        return self


db_configurer: DbConfigurer = DbConfigurer()
