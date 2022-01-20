from dofast.security._hmac import generate_token

from .config import AUTH_KEY


class Auth:
    @staticmethod
    def generate_token(expire_time: int = 30) -> str:
        return generate_token(AUTH_KEY, expire_time)
