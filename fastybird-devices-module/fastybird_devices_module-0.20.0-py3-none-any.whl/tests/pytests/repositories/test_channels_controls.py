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
import uuid

# Library dependencies
from fastybird_metadata.routing import RoutingKey
from kink import inject

# Library libs
from fastybird_devices_module.entities.channel import ChannelControlEntity
from fastybird_devices_module.repositories.channel import ChannelsControlsRepository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestChannelsControlsRepository(DbTestCase):
    @inject
    def test_repository_iterator(self, control_repository: ChannelsControlsRepository) -> None:
        self.assertEqual(2, len(control_repository.get_all()))

    # -----------------------------------------------------------------------------

    @inject
    def test_get_item(self, control_repository: ChannelsControlsRepository) -> None:
        entity = control_repository.get_by_id(control_id=uuid.UUID("15db9bef-3b57-4a87-bf67-e3c19fc3ba34", version=4))

        self.assertIsInstance(entity, ChannelControlEntity)
        self.assertEqual("configure", entity.name)

    # -----------------------------------------------------------------------------

    @inject
    def test_transform_to_dict(self, control_repository: ChannelsControlsRepository) -> None:
        entity = control_repository.get_by_id(control_id=uuid.UUID("15db9bef-3b57-4a87-bf67-e3c19fc3ba34", version=4))

        self.assertIsInstance(entity, ChannelControlEntity)
        self.assertEqual(
            {
                "id": "15db9bef-3b57-4a87-bf67-e3c19fc3ba34",
                "name": "configure",
                "channel": "17c59dfa-2edd-438e-8c49-faa4e38e5a5e",
                "owner": "455354e8-96bd-4c29-84e7-9f10e1d4db4b",
            },
            entity.to_dict(),
        )
        self.assertIsInstance(
            self.validate_exchange_data(
                routing_key=RoutingKey.CHANNELS_CONTROL_ENTITY_REPORTED,
                data=entity.to_dict(),
            ),
            dict,
        )
