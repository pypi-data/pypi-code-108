from unittest.mock import patch

from tests.utils import start_year, end_year
from hestia_earth.aggregation.impact_assessment import aggregate_country, aggregate_global

class_path = 'hestia_earth.aggregation.impact_assessment'


@patch(f"{class_path}._format_for_grouping", side_effect=lambda n: n)
@patch(f"{class_path}._group_by_product", return_value={})
@patch(f"{class_path}.aggregate_by_country", return_value=[])
@patch(f"{class_path}.aggregate_by_term")
def test_aggregate_country(mock_aggregate, *args):
    aggregate_country({}, {}, [], {}, start_year, end_year)
    mock_aggregate.assert_called_once()


@patch(f"{class_path}._group_by_product", return_value={})
@patch(f"{class_path}.aggregate_world")
def test_aggregate_global(mock_aggregate, *args):
    aggregate_global({}, {}, [], {}, start_year, end_year)
    mock_aggregate.assert_called_once()
