import requests
import slumber
from loguru import logger


class Dedibox(object):
    def __init__(self, token: str):
        self.token = token
        self.api_session = requests.session()
        self.api_session.headers['Authorization'] = f'Bearer {token}'
        self.api_client = slumber.API('https://api.online.net/api/v1/', session=self.api_session,
                                      append_slash=False)

    @logger.catch
    def is_server_available(self, server_id: str):
        return self.api_client.dedibox.availability(server_id).get()

    # @logger.catch
    def order_server(self, server_id: int, datacenter: int = 5, support: str = 'basic'):
        self.api_client = slumber.API('https://api.online.net/api/v1/', session=self.api_session,
                                      append_slash=True, )
        return self.api_client.dedibox().post({'product': server_id, 'datacenter': datacenter,
                                               'support': support}, )
