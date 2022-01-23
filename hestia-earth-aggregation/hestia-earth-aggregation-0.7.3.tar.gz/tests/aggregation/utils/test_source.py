from unittest.mock import patch

from hestia_earth.aggregation.utils.source import get_source

class_path = 'hestia_earth.aggregation.utils.source'


@patch(f"{class_path}.find_node_exact", return_value={})
def test_get_source(mock_find_node):
    get_source()
    mock_find_node.assert_called_once()
