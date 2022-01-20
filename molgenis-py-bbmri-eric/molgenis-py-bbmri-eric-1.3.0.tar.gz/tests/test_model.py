# noinspection PyProtectedMember
from unittest.mock import MagicMock

from molgenis.bbmri_eric.model import (
    ExternalServerNode,
    Node,
    NodeData,
    Source,
    Table,
    TableType,
)


def test_table_type_order():
    assert TableType.get_import_order() == [
        TableType.PERSONS,
        TableType.NETWORKS,
        TableType.BIOBANKS,
        TableType.COLLECTIONS,
    ]


def test_table_type_base_ids():
    assert TableType.PERSONS.base_id == "eu_bbmri_eric_persons"
    assert TableType.NETWORKS.base_id == "eu_bbmri_eric_networks"
    assert TableType.BIOBANKS.base_id == "eu_bbmri_eric_biobanks"
    assert TableType.COLLECTIONS.base_id == "eu_bbmri_eric_collections"


def test_table_factory_method():
    row1 = {"id": "1"}
    row2 = {"id": "2"}
    rows = [row1, row2]

    table = Table.of(TableType.PERSONS, MagicMock(), rows)

    assert table.rows_by_id["2"] == row2
    assert table.rows[0] == row1
    assert table.rows[1] == row2


def test_node_staging_id():
    node = Node("NL", "NL")

    assert node.get_staging_id(TableType.PERSONS) == "eu_bbmri_eric_NL_persons"
    assert node.get_staging_id(TableType.NETWORKS) == "eu_bbmri_eric_NL_networks"
    assert node.get_staging_id(TableType.BIOBANKS) == "eu_bbmri_eric_NL_biobanks"
    assert node.get_staging_id(TableType.COLLECTIONS) == "eu_bbmri_eric_NL_collections"


def test_node_id_prefix():
    node = Node("BE", "BE")

    assert node.get_id_prefix(TableType.PERSONS) == "bbmri-eric:contactID:BE_"
    assert node.get_id_prefix(TableType.NETWORKS) == "bbmri-eric:networkID:BE_"
    assert node.get_id_prefix(TableType.BIOBANKS) == "bbmri-eric:ID:BE_"
    assert node.get_id_prefix(TableType.COLLECTIONS) == "bbmri-eric:ID:BE_"


def test_node_eu_id_prefix():
    node = Node("BE", "BE")

    assert node.get_eu_id_prefix(TableType.PERSONS) == "bbmri-eric:contactID:EU_"
    assert node.get_eu_id_prefix(TableType.NETWORKS) == "bbmri-eric:networkID:EU_"
    assert node.get_eu_id_prefix(TableType.BIOBANKS) == "bbmri-eric:ID:EU_"
    assert node.get_eu_id_prefix(TableType.COLLECTIONS) == "bbmri-eric:ID:EU_"


def test_external_server_node():
    node = ExternalServerNode("NL", description="NL", url="test.nl")

    assert node.get_staging_id(TableType.PERSONS) == "eu_bbmri_eric_NL_persons"
    assert node.url == "test.nl"


def test_node_data_order():
    persons = Table.of(TableType.PERSONS, MagicMock(), [{"id": "1"}])
    networks = Table.of(TableType.NETWORKS, MagicMock(), [{"id": "1"}])
    biobanks = Table.of(TableType.BIOBANKS, MagicMock(), [{"id": "1"}])
    collections = Table.of(TableType.COLLECTIONS, MagicMock(), [{"id": "1"}])
    node = Node("NL", "NL")

    node_data = NodeData(
        node,
        source=Source.STAGING,
        persons=persons,
        networks=networks,
        biobanks=biobanks,
        collections=collections,
        table_by_type=MagicMock(),
    )

    assert node_data.import_order == [persons, networks, biobanks, collections]
