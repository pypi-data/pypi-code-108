from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from molgenis.bbmri_eric import utils
from molgenis.bbmri_eric.bbmri_client import EricSession
from molgenis.bbmri_eric.errors import EricError
from molgenis.bbmri_eric.model import ExternalServerNode, NodeData
from molgenis.bbmri_eric.printer import Printer
from molgenis.bbmri_eric.stager import Stager
from molgenis.client import MolgenisRequestError


@pytest.fixture
def external_server_init():
    with patch("molgenis.bbmri_eric.stager.ExternalServerSession") as ext_session_mock:
        yield ext_session_mock


def test_stager():
    stager = Stager(EricSession("url"), Printer())
    stager._clear_staging_area = MagicMock(name="_clear_staging_area")
    stager._import_node = MagicMock(name="_import_node")
    node = ExternalServerNode("NL", "NL", "url")

    stager.stage(node)

    stager._clear_staging_area.assert_called_with(node)
    stager._import_node.assert_called_with(node)


def test_clear_staging_area():
    session = EricSession("url")
    session.delete = MagicMock(name="delete")
    node = ExternalServerNode("NL", "Netherlands", "url.nl")

    Stager(session, Printer())._clear_staging_area(node)

    assert session.delete.mock_calls == [
        mock.call("eu_bbmri_eric_NL_collections"),
        mock.call("eu_bbmri_eric_NL_biobanks"),
        mock.call("eu_bbmri_eric_NL_networks"),
        mock.call("eu_bbmri_eric_NL_persons"),
    ]


def test_clear_staging_area_error():
    session = EricSession("url")
    session.delete = MagicMock(name="delete")
    session.delete.side_effect = MolgenisRequestError("error")
    node = ExternalServerNode("NL", "Netherlands", "url.nl")

    with pytest.raises(EricError) as e:
        Stager(session, Printer())._clear_staging_area(node)

    assert str(e.value) == "Error clearing staging area of node NL"


def test_import_node(external_server_init, node_data: NodeData):
    source_session_mock_instance = external_server_init.return_value
    source_session_mock_instance.get_node_data.return_value = node_data
    session = EricSession("url")
    session.add_batched = MagicMock(name="add_batched")
    node = ExternalServerNode("NO", "Norway", "url")

    Stager(session, Printer())._import_node(node)

    external_server_init.assert_called_with(node=node)
    source_session_mock_instance.get_node_data.assert_called_once()
    assert session.add_batched.mock_calls == [
        mock.call(
            "eu_bbmri_eric_NO_persons",
            utils.remove_one_to_manys(node_data.persons.rows, node_data.persons.meta),
        ),
        mock.call(
            "eu_bbmri_eric_NO_networks",
            utils.remove_one_to_manys(node_data.networks.rows, node_data.networks.meta),
        ),
        mock.call(
            "eu_bbmri_eric_NO_biobanks",
            utils.remove_one_to_manys(node_data.biobanks.rows, node_data.biobanks.meta),
        ),
        mock.call(
            "eu_bbmri_eric_NO_collections",
            utils.remove_one_to_manys(
                node_data.collections.rows, node_data.collections.meta
            ),
        ),
    ]


def test_import_node_get_node_error(external_server_init, node_data: NodeData):
    source_session_mock_instance = external_server_init.return_value
    source_session_mock_instance.get_node_data.side_effect = MolgenisRequestError("")
    session = EricSession("url")
    node = ExternalServerNode("NO", "Norway", "url")

    with pytest.raises(EricError) as e:
        Stager(session, Printer())._import_node(node)

    assert str(e.value) == "Error getting data from url"


def test_import_node_copy_node_error(external_server_init, node_data: NodeData):
    source_session_mock_instance = external_server_init.return_value
    source_session_mock_instance.get_node_data.return_value = node_data
    session = EricSession("url")
    session.add_batched = MagicMock(name="add_batched")
    session.add_batched.side_effect = MolgenisRequestError("error")
    node = ExternalServerNode("NO", "Norway", "url")

    with pytest.raises(EricError) as e:
        Stager(session, Printer())._import_node(node)

    assert str(e.value) == "Error copying from url to staging area"
