import hashlib

from ._settings import SECRET_KEY


__all__ = ("Token",)


class Token:

    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key or SECRET_KEY

    def get_secret_data(self, data: str) -> str:
        token = self.secret_key + data
        return hashlib.md5(token.encode()).hexdigest()

    def get_data(self, token: str, data: str) -> str:
        if token != self.get_secret_data(data):
            raise KeyError
        return data
