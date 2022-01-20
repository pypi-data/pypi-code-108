from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from molgenis.bbmri_eric.errors import EricError, EricWarning
from molgenis.bbmri_eric.model import ExternalServerNode, Node, NodeData, Source


@pytest.fixture
def stager_init():
    with patch("molgenis.bbmri_eric.eric.Stager") as stager_mock:
        yield stager_mock


@pytest.fixture
def validator_init():
    with patch("molgenis.bbmri_eric.eric.Validator") as validator_mock:
        yield validator_mock


@pytest.fixture
def publisher_init():
    with patch("molgenis.bbmri_eric.eric.Publisher") as publisher_mock:
        yield publisher_mock


def test_stage_external_nodes(stager_init, eric, printer):
    error = EricError("error")
    stager_init.return_value.stage.side_effect = [None, error]
    nl = ExternalServerNode("NL", "will succeed", "url.nl")
    be = ExternalServerNode("BE", "wil fail", "url.be")

    report = eric.stage_external_nodes([nl, be])

    assert printer.print_node_title.mock_calls == [mock.call(nl), mock.call(be)]
    assert stager_init.mock_calls == [
        mock.call(eric.session, eric.printer),
        mock.call().stage(nl),
        mock.call(eric.session, eric.printer),
        mock.call().stage(be),
    ]
    assert nl not in report.errors
    assert report.errors[be] == error
    printer.print_summary.assert_called_once_with(report)


def test_publish_node_staging_fails(
    eric,
    session,
    pid_service,
    stager_init,
    validator_init,
    publisher_init,
):
    nl = ExternalServerNode("NL", "Netherlands", "url")
    error = EricError("error")
    stager_init.return_value.stage.side_effect = error

    report = eric.publish_nodes([nl])

    eric.printer.print_node_title.assert_called_once_with(nl)
    publisher_init.assert_called_with(session, eric.printer, pid_service)
    stager_init.assert_called_with(session, eric.printer)
    stager_init.return_value.stage.assert_called_with(nl)
    assert not session.get_published_node_data.called
    assert not validator_init.called
    assert not publisher_init.return_value.publish.called
    assert report.errors[nl] == error
    eric.printer.print_summary.assert_called_once_with(report)


def test_publish_node_get_data_fails(
    eric,
    pid_service,
    publisher_init,
    validator_init,
    stager_init,
    session,
):
    nl = ExternalServerNode("NL", "Netherlands", "url")
    error = EricError("error")
    session.get_staging_node_data.side_effect = error

    report = eric.publish_nodes([nl])

    eric.printer.print_node_title.assert_called_once_with(nl)
    publisher_init.assert_called_with(session, eric.printer, pid_service)
    stager_init.assert_called_with(session, eric.printer)
    stager_init.return_value.stage.assert_called_with(nl)
    session.get_staging_node_data.assert_called_with(nl)
    assert not validator_init.called
    assert not publisher_init.return_value.publish.called
    assert report.errors[nl] == error
    eric.printer.print_summary.assert_called_once_with(report)


def test_publish_nodes(
    eric, pid_service, publisher_init, validator_init, stager_init, session
):
    no = Node("NO", "succeeds with validation warnings")
    nl = ExternalServerNode("NL", "fails during publishing", "url")
    no_data = _mock_node_data(no)
    nl_data = _mock_node_data(nl)
    session.get_staging_node_data.side_effect = [no_data, nl_data]
    warning = EricWarning("warning")
    validator_init.return_value.validate.side_effect = [[warning], []]
    error = EricError("error")
    publisher_init.return_value.publish.side_effect = [[], error]

    report = eric.publish_nodes([no, nl])

    assert eric.printer.print_node_title.mock_calls == [mock.call(no), mock.call(nl)]
    stager_init.assert_called_with(session, eric.printer)
    stager_init.return_value.stage.assert_called_with(nl)
    assert validator_init.mock_calls == [
        mock.call(no_data, eric.printer),
        mock.call().validate(),
        mock.call(nl_data, eric.printer),
        mock.call().validate(),
    ]
    assert publisher_init.mock_calls == [
        mock.call(session, eric.printer, pid_service),
        mock.call().publish(no_data),
        mock.call().publish(nl_data),
    ]
    assert no not in report.errors
    assert report.errors[nl] == error
    assert nl not in report.warnings
    assert report.warnings[no] == [warning]
    eric.printer.print_summary.assert_called_once_with(report)


def _mock_node_data(node: Node):
    return NodeData(
        node=node,
        source=Source.STAGING,
        persons=MagicMock(),
        biobanks=MagicMock(),
        networks=MagicMock(),
        collections=MagicMock(),
        table_by_type=MagicMock(),
    )
