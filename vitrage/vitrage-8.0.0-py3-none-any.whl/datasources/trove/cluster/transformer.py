# Copyright 2018 Samsung Electronics
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from vitrage.common.constants import DatasourceProperties as DSProps
from vitrage.common.constants import EdgeLabel
from vitrage.common.constants import EntityCategory
from vitrage.common.constants import VertexProperties as VProps
from vitrage.datasources.resource_transformer_base import \
    ResourceTransformerBase
from vitrage.datasources import transformer_base as tbase
from vitrage.datasources.transformer_base import extract_field_value
from vitrage.datasources.trove.cluster import TROVE_CLUSTER_DATASOURCE
from vitrage.datasources.trove.instance import TROVE_INSTANCE_DATASOURCE
from vitrage.datasources.trove.properties import \
    TroveClusterProperties as TProps
import vitrage.graph.utils as graph_utils


class TroveClusterTransformer(ResourceTransformerBase):

    def _create_snapshot_entity_vertex(self, entity_event):
        return self._create_vertex(entity_event)

    def _create_update_entity_vertex(self, entity_event):
        return self._create_vertex(entity_event)

    def _create_vertex(self, entity_event):
        # TODO(bzurkowski): Add project ID
        entity_id = entity_event[TProps.ID]
        name = entity_event[TProps.NAME]
        state = extract_field_value(entity_event, *TProps.STATE)
        update_timestamp = entity_event[TProps.UPDATE_TIMESTAMP]
        sample_timestamp = entity_event[DSProps.SAMPLE_DATE]
        metadata = {
            VProps.NAME: name
        }
        return graph_utils.create_vertex(
            self._create_entity_key(entity_event),
            vitrage_category=EntityCategory.RESOURCE,
            vitrage_type=TROVE_CLUSTER_DATASOURCE,
            vitrage_sample_timestamp=sample_timestamp,
            entity_id=entity_id,
            update_timestamp=update_timestamp,
            entity_state=state,
            metadata=metadata)

    def _create_snapshot_neighbors(self, entity_event):
        return self._create_entity_neighbours(entity_event)

    def _create_update_neighbors(self, entity_event):
        return self._create_entity_neighbours(entity_event)

    def _create_entity_neighbours(self, entity_event):
        neighbours = []
        for instance in entity_event[TProps.INSTANCES]:
            instance_neighbour = self._create_neighbor(
                entity_event,
                instance[TProps.ID],
                TROVE_INSTANCE_DATASOURCE,
                EdgeLabel.CONTAINS,
                is_entity_source=True)
            neighbours.append(instance_neighbour)
        return neighbours

    def _create_entity_key(self, entity_event):
        entity_id = entity_event[TProps.ID]
        key_fields = self._key_values(TROVE_CLUSTER_DATASOURCE, entity_id)
        return tbase.build_key(key_fields)

    @staticmethod
    def get_vitrage_type():
        return TROVE_CLUSTER_DATASOURCE
