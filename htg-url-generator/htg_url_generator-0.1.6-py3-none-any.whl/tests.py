from unittest.mock import patch
from django.test import TestCase
from .generator import AbstractHtgUrlGenerator


class TestHtgUrl(TestCase):
    @patch("htg_url.generator.AbstractHtgUrlGenerator._get_from_redis")
    @patch("htg_url.generator.AbstractHtgUrlGenerator.generate_new_token")
    @patch("htg_url.generator.AbstractHtgUrlGenerator.update_ttl")
    def test_url_of_two_instances_with_same_parameters(self, mock_update_ttl,
                                                       mock_generate_new_token, mock_get_from_redis):
        class TestClass(AbstractHtgUrlGenerator):
            @staticmethod
            def create_unique_identifier(**properties):
                return '_'.join(properties.values())

        db_dict = {}

        def get_from_redis(identifier):
            return db_dict.get(identifier)

        def generate_new_token(identifier):
            token = '1234abcd5678efgh'
            db_dict.update({identifier: token})
            return token

        mock_get_from_redis.side_effect = get_from_redis
        mock_generate_new_token.side_effect = generate_new_token
        mock_update_ttl.side_effect = lambda *args: None

        test_properties = {'key1': 'test1', 'key2': 'test2', 'key3': 'test3'}

        instance = TestClass(**test_properties)
        other_instance = TestClass(**test_properties)

        instance_url = instance.url
        other_instance_url = other_instance.url

        self.assertEquals(instance_url, other_instance_url)
