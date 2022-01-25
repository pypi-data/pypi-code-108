class AppRegistrationClientSecret:
    def __init__(self, key_id=None, value=None, start_date=None, end_date=None, description=None):
        self.key_id = key_id
        self.start_date = start_date
        self.end_date = end_date
        self.value = value
        self.__description = description

    # todo: move logic to manager
    # description can not be more than 15 characters - known issue: https://github.com/Azure/azure-docs-powershell-azuread/issues/296
    @property
    def description(self): return self.__description[0:14] if self.__description else None


class AppRegistration:
    def __init__(
            self,
            name: str,
            app_id: str = None,
            client_secret: AppRegistrationClientSecret = None,
            client_secret_description: str = None
    ):
        self.name = name
        self.app_id = app_id

        # todo: move this logic to manager - see issue description above in AppRegistrationClientSecret
        # client secret description will default to app reg name
        self.client_secret_description = client_secret_description or self.name

        # todo: possibly flatten? not sure there is a reason for nested class here
        self.client_secret = AppRegistrationClientSecret(description=self.client_secret_description)
