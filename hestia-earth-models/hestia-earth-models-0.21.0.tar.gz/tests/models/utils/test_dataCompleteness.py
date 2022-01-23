from unittest.mock import patch
from hestia_earth.schema import TermTermType

from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete, _is_term_type_incomplete

class_path = 'hestia_earth.models.utils.dataCompleteness'


@patch(f"{class_path}.download_hestia")
def test_is_term_type_complete(mock_download):
    cycle = {'dataCompleteness': {}}

    cycle['dataCompleteness'][TermTermType.CROPRESIDUE.value] = True
    mock_download.return_value = {
        'termType': TermTermType.CROPRESIDUE.value
    }
    assert _is_term_type_complete(cycle, 'termid')

    cycle['dataCompleteness'][TermTermType.CROPRESIDUE.value] = False
    mock_download.return_value = {
        'termType': TermTermType.CROPRESIDUE.value
    }
    assert not _is_term_type_complete(cycle, 'termid')

    # termType not in dataCompleteness
    mock_download.return_value = {
        'termType': TermTermType.CROPRESIDUEMANAGEMENT.value
    }
    assert not _is_term_type_complete(cycle, 'termid')


@patch(f"{class_path}.download_hestia")
def test_is_term_type_incomplete(mock_download):
    cycle = {'dataCompleteness': {}}

    cycle['dataCompleteness'][TermTermType.CROPRESIDUE.value] = True
    mock_download.return_value = {
        'termType': TermTermType.CROPRESIDUE.value
    }
    assert not _is_term_type_incomplete(cycle, 'termid')

    cycle['dataCompleteness'][TermTermType.CROPRESIDUE.value] = False
    mock_download.return_value = {
        'termType': TermTermType.CROPRESIDUE.value
    }
    assert _is_term_type_incomplete(cycle, 'termid')

    # termType not in dataCompleteness
    mock_download.return_value = {
        'termType': TermTermType.CROPRESIDUEMANAGEMENT.value
    }
    assert _is_term_type_incomplete(cycle, 'termid')
