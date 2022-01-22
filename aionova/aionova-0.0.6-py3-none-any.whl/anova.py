from typing import Union, Optional

from .legacy import AnovaCookerLegacy


class AnovaCooker:
    def __init__(self, cooker_id: str, cooker_secret: str = None, username: str = None, password: str = None):
        if (not ((username is None) ^ (password is None))) ^ (cooker_secret is None):
            raise ValueError('You must set cooker_secret or both the username and password')

        if cooker_secret is not None:
            self.cooker = AnovaCookerLegacy(cooker_id, cooker_secret)
        else:
            raise NotImplementedError

