#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

# Test dependencies
import json
import redis
import unittest

# Library dependencies
from kink import inject
from fb_metadata.types import ModuleOrigin
from fb_metadata.routing import RoutingKey
from unittest.mock import patch

# Library libs
from fb_redisdb_exchange_plugin.bootstrap import register_services
from fb_redisdb_exchange_plugin.connection import Connection
from fb_redisdb_exchange_plugin.publisher import Publisher


class TestPublisher(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        register_services()

    # -----------------------------------------------------------------------------

    @inject
    def test_publish(self, publisher: Publisher, redis_client: Connection):
        message = {
            "routing_key": RoutingKey(RoutingKey.DEVICES_ENTITY_UPDATED).value,
            "origin": ModuleOrigin(ModuleOrigin.DEVICES_MODULE).value,
            "sender_id": redis_client.identifier,
            "data": {
                "key_one": "value_one",
                "key_two": "value_two",
            },
        }

        with patch.object(redis.Redis, "publish") as mock_redis_publish:
            mock_redis_publish.return_value = True

            publisher.publish(
                origin=ModuleOrigin(ModuleOrigin.DEVICES_MODULE),
                routing_key=RoutingKey(RoutingKey.DEVICES_ENTITY_UPDATED),
                data={
                    "key_one": "value_one",
                    "key_two": "value_two",
                },
            )

        mock_redis_publish.assert_called_with(channel="fb_exchange", message=json.dumps(message))


if __name__ == '__main__':
    unittest.main()
