from unittest.mock import patch

from hestia_earth.models.cycle.post_checks import run

class_path = 'hestia_earth.models.cycle.post_checks'


@patch(f"{class_path}._run_in_serie", return_value={})
def test_run(mock_run_in_serie):
    run({})
    mock_run_in_serie.assert_called_once()
