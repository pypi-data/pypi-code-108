from htg_url.redis.client import RedisWrapper
from abc import ABC, abstractmethod


class AbstractHtgUrlGenerator(ABC):
    _HTG_PREFIX = 'HTG_'
    _DOC_PREFIX = 'DOC_'

    def __init__(self, **kwargs):
        super(AbstractHtgUrlGenerator, self).__init__()
        self.properties = kwargs
        self.unique_identifier = self.create_unique_identifier(**self.properties)

    @property
    def url(self):
        htg_identifier = self.get_htg_identifier()
        existing_token = self._get_from_redis(htg_identifier)

        if existing_token:
            self.update_ttl(existing_token)
            return existing_token

        return self.generate_new_token(htg_identifier)

    @staticmethod
    @abstractmethod
    def create_unique_identifier(**properties):
        """Get unique identifier based on passed properties
        :return: :string
        """

    def get_htg_identifier(self):
        return self._HTG_PREFIX + self.unique_identifier

    def get_doc_identifier(self):
        return self._DOC_PREFIX + self.unique_identifier

    def generate_new_token(self, unique_identifier):
        generated_token = self._generate_hex()
        self._write_to_redis(unique_identifier, generated_token)
        self._write_properties_to_redis(generated_token, self.properties)
        self.update_ttl(generated_token)
        return generated_token

    @staticmethod
    def _generate_hex():
        import secrets
        return secrets.token_hex(16)

    @staticmethod
    def _get_from_redis(key):
        return RedisWrapper.get(key)

    @staticmethod
    def _write_to_redis(key, value):
        return RedisWrapper.set(key, value)

    @staticmethod
    def _write_properties_to_redis(dict_name, data: dict):
        for key, value in data.items():
            RedisWrapper.set_dict(dict_name, key, value)

    def update_ttl(self, token):
        for key in self._get_redis_keys(token):
            RedisWrapper.set_ttl(key)

    def _get_redis_keys(self, token):
        return [self.get_htg_identifier(), self.get_doc_identifier(), token]
