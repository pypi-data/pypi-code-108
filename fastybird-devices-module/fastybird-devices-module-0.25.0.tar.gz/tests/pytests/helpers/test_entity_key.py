#!/usr/bin/python3

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
import unittest
from unittest.mock import Mock, patch

# Library libs
from fastybird_devices_module.entities.base import Base
from fastybird_devices_module.helpers import KeyHashHelpers


class TestKeyHashUtils(unittest.TestCase):
    @patch("fastybird_devices_module.helpers.time")
    def test_default_generator(self, mock_time) -> None:
        mock_time.time_ns = Mock(return_value=1630831410968578000)

        entity_key_generator = KeyHashHelpers()

        entity = Mock()

        self.assertEqual("5nFZ6Gt59", entity_key_generator.generate_key(entity))

    # -----------------------------------------------------------------------------

    def test_custom_generator(self) -> None:
        entity_key_generator = KeyHashHelpers()
        entity_key_generator.set_generator(self.__custom_generator)

        entity = Mock()

        self.assertEqual("custom-generated", entity_key_generator.generate_key(entity))

    # -----------------------------------------------------------------------------

    @staticmethod
    def __custom_generator(entity: Base) -> str:
        return "custom-generated"


if __name__ == "__main__":
    unittest.main()
