import pytest
import logbook

from pydbt import logger
from pydbt.constants import StatusColor

from dbt.contracts.results import NodeStatus


@pytest.mark.parametrize(
    "input,expected",
    [
        (NodeStatus.Success, logbook.INFO),
        (NodeStatus.Error, logbook.ERROR),
        (NodeStatus.Fail, logbook.ERROR),
        (NodeStatus.Warn, logbook.WARNING),
        (NodeStatus.Skipped, logbook.WARNING),
        (NodeStatus.Pass, logbook.INFO),
        (NodeStatus.RuntimeErr, logbook.CRITICAL),
        ("unknown_status", logbook.NOTSET),
    ],
)
def test_dbt_to_log_status(input, expected):
    result = logger.dbt_to_log_status(input)
    assert result == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (logbook.CRITICAL, StatusColor.CRITICAL),
        (logbook.ERROR, StatusColor.ERROR),
        (logbook.WARNING, StatusColor.WARNING),
        (logbook.NOTICE, StatusColor.NOTICE),
        (logbook.INFO, StatusColor.INFO),
        (logbook.DEBUG, StatusColor.DEBUG),
        (logbook.NOTSET, StatusColor.DEBUG),
        (5000, StatusColor.INFO),
    ],
)
def test_logbook_status_to_color(input, expected):
    result = logger.logbook_status_to_color(input)
    assert result == expected
