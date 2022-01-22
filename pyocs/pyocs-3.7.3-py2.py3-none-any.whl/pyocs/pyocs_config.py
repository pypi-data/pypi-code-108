import os
from pyapollo.apollo_client import ApolloClient

CONFIG_NAME_MAPPER = {
    'public': 'http://fat.conf.cvte.com',
    'internal': 'http://dev.conf.cvte.com'
}
class PyocsConfig:
    _instance = None
    client = None

    # 单例模式
    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(PyocsConfig, cls).__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        flask_env = os.getenv('FLASK_CONFIG') or 'internal'
        config_server_url = CONFIG_NAME_MAPPER[flask_env]
        #print("配置环境：" + config_server_url)
        self.client = ApolloClient(app_id="NAOt2HhY", cluster="default", config_server_url=config_server_url,
                              cache_file_path=os.curdir)
        self.client.start()
    @staticmethod
    def get_config():
        config = dict()
        client = PyocsConfig().client
        config['ocs_user_name'] = client.get_value(key="OCS_COMMON_ACCOUNT", default_val="DefaultValue",
                                                   namespace="platform.pyocs")
        config['ocs_password'] = client.get_value(key="OCS_COMMON_PASSWORD", default_val="DefaultValue",
                                                  namespace="platform.pyocs")
        config['sql_host'] = client.get_value(key="SQL_HOST", default_val="DefaultValue",
                                                  namespace="platform.pyocs")
        config['sql_port'] = client.get_value(key="SQL_PORT", default_val="DefaultValue",
                                                  namespace="platform.pyocs")
        config['sql_user_name'] = client.get_value(key="SQL_USER_NAME", default_val="DefaultValue",
                                                       namespace="platform.pyocs")
        config['sql_password'] = client.get_value(key="SQL_PASSWORD", default_val="DefaultValue",
                                                      namespace="platform.pyocs")
        config['sql_database_name'] = client.get_value(key="SQL_DATABASE_NAME", default_val="DefaultValue",
                                                           namespace="platform.pyocs")

        return config