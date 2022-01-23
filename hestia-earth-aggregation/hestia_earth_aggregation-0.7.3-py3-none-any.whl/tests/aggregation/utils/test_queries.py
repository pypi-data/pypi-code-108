from unittest.mock import patch, MagicMock

from tests.utils import start_year, end_year
from hestia_earth.aggregation.utils.queries import (
    _download_node, _download_nodes, _query_all_nodes, _country_nodes, _global_nodes, find_nodes, get_countries,
    _get_time_ranges, _earliest_date, get_products, get_time_ranges
)

class_path = 'hestia_earth.aggregation.utils.queries'
country_name = 'Japan'


class FakePostRequest():
    def __init__(self, results=[]) -> None:
        self.results = results
        pass

    def json(self):
        return {'results': self.results}


@patch(f"{class_path}.download_hestia", return_value={})
def test_download_node(mock_download_hestia):
    _download_node('')({})
    mock_download_hestia.assert_called_once()


@patch(f"{class_path}._download_node")
def test_download_nodes(mock_download):
    mock = MagicMock()
    mock_download.return_value = mock
    nodes = [{}, {}]
    _download_nodes(nodes)
    assert mock.call_count == len(nodes)


@patch('requests.post', return_value=FakePostRequest())
def test_query_all_nodes(mock_post):
    _query_all_nodes('', '', start_year, end_year, 'Japan')
    mock_post.assert_called_once()


@patch(f"{class_path}._query_all_nodes", return_value=[])
@patch(f"{class_path}._download_nodes", return_value=[])
def test_country_nodes(mock_download, *args):
    _country_nodes('', '', start_year, end_year, 'Japan')
    mock_download.assert_called_once_with([], data_state='recalculated')


@patch('requests.post', return_value=FakePostRequest())
@patch(f"{class_path}._download_nodes", return_value=[])
def test_global_nodes(mock_download, *args):
    _global_nodes('', '', start_year, end_year)
    mock_download.assert_called_once_with([])


@patch(f"{class_path}._global_nodes", return_value=[])
@patch(f"{class_path}._country_nodes", return_value=[])
def test_find_nodes(mock_find_country, mock_find_global):
    find_nodes('', '', 0, 0, 'Japan')
    mock_find_country.assert_called_once()
    mock_find_global.assert_not_called()

    find_nodes('', '', 0, 0, 'World')
    mock_find_global.assert_called_once()


@patch(f"{class_path}.find_node", return_value=[])
def test_get_countries(mock_find):
    get_countries()
    mock_find.assert_called_once()


def test__get_time_ranges():
    assert _get_time_ranges('1996', '2021') == [(1990, 1999), (2000, 2009), (2010, 2019), (2020, 2029)]
    assert _get_time_ranges('2000', '2020') == [(2000, 2009), (2010, 2019), (2020, 2029)]


@patch(f"{class_path}._get_time_ranges", return_value=[(2000, 2009), (2010, 2019)])
@patch(f"{class_path}._latest_date", return_value='2021-01-01')
@patch(f"{class_path}._earliest_date")
def test_get_time_ranges(mock_earliest_date, *args):
    # no earliest date => no time ranges
    mock_earliest_date.return_value = None
    assert len(get_time_ranges('', '', '')) == 0

    # with earliest date => time ranges
    mock_earliest_date.return_value = 2000
    assert len(get_time_ranges('', '', '')) > 0


@patch(f"{class_path}._run_query")
def test_earliest_date(mock_find):
    # no results => no date
    mock_find.return_value = []
    assert not _earliest_date('', '', '')

    # with results => first date
    mock_find.return_value = [{'endDate': 2000}, {'endDate': 2010}]
    assert _earliest_date('', '', '') == 2000


@patch(f"{class_path}._run_query")
def test_get_products(mock_find):
    mock_find.return_value = [
        {
            '@id': 'wheatGrain',
            'name': 'Wheat, grain',
            'termType': 'crop'
        },
        {
            '@id': 'aboveGroundCropResidueBurnt',
            'name': 'Above ground crop residue burnt',
            'termType': 'cropResidue'
        }
    ]
    assert get_products() == [{
        '@id': 'wheatGrain',
        'name': 'Wheat, grain',
        'termType': 'crop'
    }]
