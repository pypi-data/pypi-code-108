from unittest.mock import patch

from tests.utils import start_year, end_year
from hestia_earth.aggregation.cycle import aggregate_country, aggregate_global

class_path = 'hestia_earth.aggregation.cycle'


@patch(f"{class_path}.aggregate_by_country", return_value=[])
@patch(f"{class_path}._format_for_grouping", side_effect=lambda n: n)
@patch(f"{class_path}._group_by_product")
@patch(f"{class_path}.aggregate_by_term")
def test_aggregate_country(mock_aggregate, mock_group_by, *args):
    # no groupped data
    mock_group_by.return_value = {}
    aggregate_country({}, {}, [], {}, start_year, end_year)
    mock_aggregate.assert_not_called()

    # with groupped data
    mock_group_by.return_value = {'cycles': {}}
    aggregate_country({}, {}, [], {}, start_year, end_year)
    mock_aggregate.assert_called_once()


@patch(f"{class_path}._format_for_grouping", side_effect=lambda n: n)
@patch(f"{class_path}._group_by_product")
@patch(f"{class_path}.aggregate_world")
def test_aggregate_global(mock_aggregate, mock_group_by, *args):
    # no groupped data
    mock_group_by.return_value = {}
    aggregate_global({}, {}, [], {}, start_year, end_year)
    mock_aggregate.assert_not_called()

    # with groupped data
    mock_group_by.return_value = {'cycles': {}}
    aggregate_global({}, {}, [], {}, start_year, end_year)
    mock_aggregate.assert_called_once()
