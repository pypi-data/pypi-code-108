import os
from configparser import ConfigParser
from harvest import logger


USER_AGENT = "Python Harvest API (ramon@vyscond.io)"


class Credential(object):
    def get_headers(self):
        return {}

    def get_params(self):
        return {}


class PersonalAccessAuthCredential(Credential):
    def __init__(self, token, account_id):
        self.token = token
        self.account_id = account_id

    def get_headers(self):
        ret = {
            "Harvest-Account-ID": self.account_id,
            "Authorization": f"Bearer {self.token}",
            "User-Agent": USER_AGENT,
        }
        logger.debug(ret)
        return ret


class PersonalAccessAuthConfigCredential(Credential):
    def __init__(self, config_path=None):
        config_path = config_path or os.environ.get(
            "HARVEST_CFG", os.path.expanduser("~/.harvest.cfg"),
        )
        config = ConfigParser()
        config.read(config_path)
        self.token = config.get("authentication", "token")
        self.account_id = config.get("authentication", "account_id")

    def get_headers(self):
        ret = {
            "Harvest-Account-ID": self.account_id,
            "Authorization": f"Bearer {self.token}",
            "User-Agent": USER_AGENT,
        }
        logger.debug(ret)
        return ret


class PersonalAccessAuthEnvCredential(Credential):
    def __init__(self):
        self.token = os.environ.get("HARVEST_PA_TOKEN", "")
        self.account_id = os.environ.get("HARVEST_PA_ACCOUNT_ID", "")

    def get_headers(self):
        ret = {
            "Harvest-Account-ID": self.account_id,
            "Authorization": f"Bearer {self.token}",
            "User-Agent": USER_AGENT,
        }
        logger.debug(ret)
        return ret


class OAuth2Credential(Credential):
    def __init__(self, access_token, scope):
        self.access_token = access_token
        self.scope = scope

    def get_headers(self):
        ret = {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": USER_AGENT,
            "Harvest-Account-Id": self.scope,
        }
        logger.debug(ret)
        return ret
