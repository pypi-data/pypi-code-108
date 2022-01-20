from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from molgenis.bbmri_eric.model import NodeData, QualityInfo, TableType


@pytest.fixture
def enricher_init():
    with patch("molgenis.bbmri_eric.publisher.Enricher") as enricher_mock:
        yield enricher_mock


@pytest.fixture
def pid_manager_factory():
    with patch(
        "molgenis.bbmri_eric.publisher.PidManagerFactory"
    ) as pid_manager_factory_mock:
        yield pid_manager_factory_mock


def test_publish(
    publisher,
    enricher_init,
    pid_manager_factory,
    pid_service,
    node_data: NodeData,
    session,
    printer,
):
    publisher._delete_rows = MagicMock()
    existing_node_data = MagicMock()
    biobanks = MagicMock()
    collections = MagicMock()
    networks = MagicMock()
    persons = MagicMock()
    existing_node_data.table_by_type = {
        TableType.BIOBANKS: biobanks,
        TableType.PERSONS: persons,
        TableType.NETWORKS: networks,
        TableType.COLLECTIONS: collections,
    }
    session.get_published_node_data.return_value = existing_node_data
    pid_manager = pid_manager_factory.create.return_value = MagicMock()

    publisher.publish(node_data)

    assert enricher_init.called_with(node_data, printer)
    enricher_init.return_value.enrich.assert_called_once()

    assert pid_manager.called_with(pid_service, printer, "url")
    assert pid_manager.assign_biobank_pids.called_with(node_data.biobanks)
    assert pid_manager.update_biobank_pids.called_with(
        node_data.biobanks, existing_node_data.biobanks
    )

    assert session.upsert_batched.mock_calls == [
        mock.call(node_data.persons.type.base_id, node_data.persons.rows),
        mock.call(node_data.networks.type.base_id, node_data.networks.rows),
        mock.call(node_data.biobanks.type.base_id, node_data.biobanks.rows),
        mock.call(node_data.collections.type.base_id, node_data.collections.rows),
    ]

    assert publisher._delete_rows.mock_calls == [
        mock.call(node_data.collections, collections),
        mock.call(node_data.biobanks, biobanks),
        mock.call(node_data.networks, networks),
        mock.call(node_data.persons, persons),
    ]


def test_delete_rows(publisher, pid_service, node_data: NodeData, session):
    publisher.quality_info = QualityInfo(
        biobanks={"undeletable_id": ["quality"]}, collections={}
    )
    existing_biobanks_table = MagicMock()
    existing_biobanks_table.rows_by_id.return_value = {
        "bbmri-eric:ID:NO_OUS": {"pid": "pid1"},
        "delete_this_row": {"pid": "pid2"},
        "undeletable_id": {"pid": "pid3"},
    }
    existing_biobanks_table.rows_by_id.keys.return_value = {
        "bbmri-eric:ID:NO_OUS",
        "delete_this_row",
        "undeletable_id",
    }

    publisher._delete_rows(node_data.biobanks, existing_biobanks_table)

    publisher.pid_manager.terminate_biobanks({"pid2"})
    session.delete_list.assert_called_with(
        "eu_bbmri_eric_biobanks", ["delete_this_row"]
    )
    publisher.warnings = [
        "Prevented the deletion of a row that is referenced from "
        "the quality info: biobanks undeletable_id."
    ]
