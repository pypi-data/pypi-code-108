from loguru import logger
from namecom import Name


class Namecom(object):
    def __init__(self, username: str, token: str):
        self.username = username
        self.token = token
        self.api_client = Name(username, token)

    @logger.catch
    def create_domain(self, domain_name: str):
        return self.api_client.post('/domains', {'domain': {'domainName': domain_name}})
