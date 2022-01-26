import json


class UserManagementService:
    def __init__(self, app):
        """
        :type app: metasdk.MetaApp
        """
        self.__app = app
        self.__options = {}

    def send_recovery_notice(self, login, app_alias, state=None):
        """
        Выслать письмо о восстановлении пароля
        """
        data = {
            "login": login,
            "appAlias": app_alias,
            "state": state,
        }
        response = self.__app.native_api_call('user-management', 'sendRecoveryNotice', data, self.__options, False, None, False, http_path="/api/meta/v1/", http_method="POST")
        return json.loads(response.text)
