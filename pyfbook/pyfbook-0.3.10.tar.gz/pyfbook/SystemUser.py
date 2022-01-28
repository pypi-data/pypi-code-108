import datetime
import os


class SystemUser:
    def __init__(self, id, app_id_name, app_secret_name, access_token_name):
        self.id = id
        self.app_id_name = app_id_name
        self.app_id = os.environ[app_id_name]
        self.app_secret_name = app_secret_name
        self.app_secret = os.environ[app_secret_name]
        self.access_token_name = access_token_name
        self.access_token = os.environ[access_token_name]

    @staticmethod
    def all(facebook):
        schema_name = facebook.schema_name if facebook.schema_name else facebook.config.get('schema_name')
        r = facebook.transactional_dbstream.execute_query(
            'SELECT id, app_id_name, app_secret_name, access_token_name FROM %s.app_system_user' % schema_name)
        return [SystemUser(**result) for result in r]

    @staticmethod
    def get(_id, facebook):
        schema_name = facebook.schema_name if facebook.schema_name else facebook.config.get('schema_name')
        r = facebook.transactional_dbstream.execute_query(
            'SELECT id, app_id_name, app_secret_name, access_token_name FROM %s.app_system_user WHERE id=%s' % (
            schema_name, _id))
        if not r:
            print('SystemUser does not exist')
            exit(1)
        return SystemUser(**r[0])

    @staticmethod
    def create(facebook, app_id_name, app_secret_name, access_token_name):
        schema_name = facebook.schema_name if facebook.schema_name else facebook.config.get('schema_name')
        try:
            max_id = facebook.transactional_dbstream.execute_query('SELECT max(id) as max_id FROM %s.app_system_user' % schema_name)[
                0].get('max_id')
        except:
            max_id = 1
        data = {
            "table_name": '%s.app_system_user' % schema_name,
            "columns_name": ['id', 'app_id_name', 'app_secret_name', 'access_token_name', 'created_at', 'updated_at'],
            "rows": [[max_id + 1, app_id_name, app_secret_name, access_token_name, datetime.datetime.now(),
                      datetime.datetime.now()]]
        }
        facebook.transactional_dbstream.send_data(data, replace=False)
