from pyocs import pyocs_config
from pyocs.pyocs_database import pyocsDataBase

class dgDataBase:
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(dgDataBase, cls).__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = pyocs_config.PyocsConfig.get_config()
        self.database = pyocsDataBase(pyocsDataBase.sql_server(config['sql_host'], int(config['sql_port']), config['sql_user_name'],
                                                          config['sql_password'], config['sql_database_name']))

    def get_download_link_of_tcl_dt_by_engineer(self, engineer):
        link = self.database.get_value_of_key('tcl_oversea_checking_map', 'engineer', engineer)[0]
        if not link:
            raise KeyError()
        return link
