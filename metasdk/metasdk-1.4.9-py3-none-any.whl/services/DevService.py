import json


class DevService:
    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}

    def fetch_db_credentials(self):
        """
        """
        data = {}
        dr = self.__app.native_api_call('dev', 'fetch-db-credentials', data, self.__options, False, None, False, http_path="/api/meta/v1/", http_method='POST')
        return json.loads(dr.text)

    def issue_access_token(self, user_id, scopes):
        """
        Выпустить новый access token
        Длительность системно зашита - 10m, установить ее не получится.
        Сделано это для безопасности
        """
        data = {
            "userId": user_id,
            "scopes": scopes
        }
        dr = self.__app.native_api_call('dev', 'issue-access-token', data, self.__options, False, None, False, http_path="/api/meta/v1/", http_method='POST')
        return json.loads(dr.text)

    def clear_cache(self):
        """
        Очистить общий кеш на всех инстансах
        """
        data = {}
        dr = self.__app.native_api_call('dev', 'clear-cache', data, self.__options, False, None, False, http_path="/api/meta/v1/", http_method='POST')
        return dr.ok
