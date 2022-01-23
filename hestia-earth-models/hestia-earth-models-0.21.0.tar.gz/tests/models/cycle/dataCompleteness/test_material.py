from unittest.mock import patch

from hestia_earth.models.cycle.dataCompleteness.material import run, MODEL_KEY

class_path = f"hestia_earth.models.cycle.dataCompleteness.{MODEL_KEY}"


@patch(f"{class_path}.find_term_match", return_value=None)
def test_run(mock_find_term):
    cycle = {}

    # on cropland => not complete
    cycle['site'] = {'siteType': 'cropland'}
    assert not run(cycle)

    # with input => complete
    mock_find_term.return_value = {'value': [10]}
    assert run(cycle) is True
