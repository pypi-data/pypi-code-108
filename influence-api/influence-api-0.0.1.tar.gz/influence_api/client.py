import logging

from authlib.integrations.django_client import OAuth

API_BASE_URL = "https://api.influenceth.io"


logger = logging.getLogger(__name__)

_oauth_registry = OAuth()

_oauth_registry.register("influence")
_oauth_client = _oauth_registry.influence


class InfluenceClient:
    def __init__(self) -> None:
        pass

    def get_by_url(self, url):
        if url.startswith("/"):
            url = API_BASE_URL + url
        result = _oauth_client.get(url)
        result.raise_for_status()
        result_json = result.json()
        return result_json

    def get_asteroid(self, id):
        return self.get_by_url("/v1/asteroids/{}".format(id))
