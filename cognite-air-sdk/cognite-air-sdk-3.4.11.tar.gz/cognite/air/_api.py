class AIRClientError(Exception):
    pass


class BaseAPIClient:
    def __init__(self, config):
        self._config = config
        self.client = config.client
