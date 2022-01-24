class MySQLKitConfig:
    """
    A standard config class for MySQLKit
    Since 0.1.4
    """

    def __init__(self, config_dict: dict = None):
        """
        Parameter `config_dict` is like:
        {
            'host': '',
            'port': 3306,
            'user': '',
            'password': '',
            'db': '',
            'charset': 'utf8',
            'auto_commit': True,
        }
        """
        if config_dict is None:
            config_dict = {}

        self._host = config_dict.get('host', '')
        self._port = config_dict.get('port', 3306)
        self._user = config_dict.get('user', 'anonymous')
        self._password = config_dict.get('password', '')
        self._db = config_dict.get('db', '')
        self._charset = config_dict.get('charset', 'utf8')
        self._auto_commit = config_dict.get('auto_commit', True)

    def get_host(self):
        return self._host

    def set_host(self, host: str):
        self._host = host
        return self

    def get_port(self):
        return self._port

    def set_port(self, port: int):
        self._port = port
        return self

    def get_user(self):
        return self._user

    def set_user(self, user: str):
        self._user = user
        return self

    def get_password(self):
        return self._password

    def set_password(self, password: str):
        self._password = password
        return self

    def get_db(self):
        return self._db

    def set_db(self, db: str):
        self._db = db
        return self

    def get_charset(self):
        return self._charset

    def set_charset(self, charset: str):
        self._charset = charset
        return self

    def get_auto_commit(self):
        return self._auto_commit

    def set_auto_commit(self, auto_commit: bool):
        self._auto_commit = auto_commit
        return self
