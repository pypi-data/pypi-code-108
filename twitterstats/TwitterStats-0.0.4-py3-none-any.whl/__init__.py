import os
from .api_client import TwitterAPI as _Fetcher

VERSION = "0.0.4"


def Fetcher(**kwargs):
    if all([param is None for _, param in kwargs.items()]):
        kwargs["consumer_key"] = os.getenv("TWITTER_CONSUMER_KEY")
        kwargs["consumer_secret"] = os.getenv("TWITTER_CONSUMER_SECRET")
        kwargs["access_token"] = os.getenv("TWITTER_ACCESS_KEY")
        kwargs["access_token_secret"] = os.getenv("TWITTER_ACCESS_KEY_SECRET")
    return _Fetcher(**kwargs)


__all__ = ["VERSION", "Fetcher"]
