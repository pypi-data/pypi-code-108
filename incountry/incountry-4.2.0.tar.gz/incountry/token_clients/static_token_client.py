from .token_client import TokenClient


class StaticTokenClient(TokenClient):
    def __init__(self, token: str):
        self.token = token

    def get_token(self, audience=None, region=None, refetch=False):
        return self.token

    def can_refetch(self):
        return False
