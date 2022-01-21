from agilicus_api import Configuration


class ServiceConfiguration(Configuration):
    def __init__(self, service_token=None):
        Configuration.__init__(self)
        self.service_token = service_token

    def auth_settings(self):
        """A derived method that makes use of a service token
        to refresh the access_token automatically"""
        if self.service_token:
            self.access_token = self.service_token.get()
        return Configuration.auth_settings(self)
