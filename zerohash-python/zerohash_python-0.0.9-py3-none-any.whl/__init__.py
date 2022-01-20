__version__ = "0.0.9"  # Do not update directly, use bumpversion


credentials = None

default_http_client = None
proxy_url = None

api_base = (
    "https://api.cert.zerohash.com"  # set to https://api.zerohash.com in production
)

max_network_retries = 0

from zerohash.resources import *


class Credential:
    def __init__(self, private_key, public_key, passphrase):
        self.private_key = private_key
        self.public_key = public_key
        self.passphrase = passphrase


def set_credentials(private_key, public_key, passphrase):
    return Credential(private_key, public_key, passphrase)
