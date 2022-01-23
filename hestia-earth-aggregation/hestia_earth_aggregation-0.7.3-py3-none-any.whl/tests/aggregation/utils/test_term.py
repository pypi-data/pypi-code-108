from unittest.mock import patch
from hestia_earth.schema import TermTermType

from hestia_earth.aggregation.utils.term import _fetch_all, _format_country_name

class_path = 'hestia_earth.aggregation.utils.term'


@patch(f"{class_path}.find_node", return_value=[])
def test_fetch_all(mock_find_node):
    _fetch_all(TermTermType.EMISSION)
    mock_find_node.assert_called_once()


def test_format_country_name():
    assert _format_country_name('Virgin Islands, U.S.') == 'virgin-islands-us'
    assert _format_country_name('Turkey (Country)') == 'turkey-country'
    assert _format_country_name("Côte d'Ivoire") == 'cote-divoire'
    assert _format_country_name('Åland') == 'aland'
    assert _format_country_name('Réunion') == 'reunion'
    assert _format_country_name('São Tomé and Príncipe') == 'sao-tome-and-principe'
