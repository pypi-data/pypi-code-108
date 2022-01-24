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
from fastybird_devices_module.entities.connector import ConnectorEntity
from fastybird_devices_module.repositories.connector import ConnectorsRepository

# Tests libs
from tests.pytests.tests import DbTestCase


class TestConnectorsRepository(DbTestCase):
    @inject
    def test_repository_iterator(self, connector_repository: ConnectorsRepository) -> None:
        self.assertEqual(1, len(connector_repository.get_all()))

    # -----------------------------------------------------------------------------

    @inject
    def test_get_item_by_id(self, connector_repository: ConnectorsRepository) -> None:
        entity = connector_repository.get_by_id(
            connector_id=uuid.UUID("17c59dfa-2edd-438e-8c49-faa4e38e5a5e", version=4)
        )

        self.assertIsInstance(entity, ConnectorEntity)
        self.assertEqual("bLikvZ", entity.key)

    # -----------------------------------------------------------------------------

    @inject
    def test_get_item_by_key(self, connector_repository: ConnectorsRepository) -> None:
        entity = connector_repository.get_by_key(connector_key="bLikvZ")

        self.assertIsInstance(entity, ConnectorEntity)
        self.assertEqual(uuid.UUID("17c59dfa-2edd-438e-8c49-faa4e38e5a5e", version=4), entity.id)

    # -----------------------------------------------------------------------------

    @inject
    def test_transform_to_dict(self, connector_repository: ConnectorsRepository) -> None:
        entity = connector_repository.get_by_id(
            connector_id=uuid.UUID("17c59dfa-2edd-438e-8c49-faa4e38e5a5e", version=4)
        )

        self.assertIsInstance(entity, ConnectorEntity)
        self.assertEqual(
            {
                "id": "17c59dfa-2edd-438e-8c49-faa4e38e5a5e",
                "type": "virtual",
                "key": "bLikvZ",
                "name": "Virtual",
                "enabled": True,
                "owner": None,
            },
            entity.to_dict(),
        )
        self.assertIsInstance(
            self.validate_exchange_data(
                routing_key=RoutingKey.CONNECTORS_ENTITY_REPORTED,
                data=entity.to_dict(),
            ),
            dict,
        )
