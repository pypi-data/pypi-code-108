import os
import warnings

import pytest

from seeq.spy._config import get_data_lab_project_url, get_data_lab_project_id

# noinspection HttpUrlsUsage
SERVER_URL = 'http://seeq.com'
PROJECT_UUID = '12345678-9ABC-DEF0-1234-56789ABCDEF0'


def setup_environment_variables():
    os.environ['SEEQ_SERVER_URL'] = SERVER_URL
    os.environ['SEEQ_PROJECT_UUID'] = PROJECT_UUID


def setup_module():
    setup_environment_variables()


@pytest.mark.unit
def test_sdl_project_uuid():
    assert get_data_lab_project_id() == PROJECT_UUID


@pytest.mark.unit
def test_sdl_project_url():
    expected_project_url = f'{SERVER_URL}/data-lab/{PROJECT_UUID}'
    assert get_data_lab_project_url() == expected_project_url


@pytest.mark.unit
def test_sdl_project_uuid():
    assert get_data_lab_project_id() == PROJECT_UUID


@pytest.mark.unit
def test_sdl_project_url():
    expected_project_url = f'{SERVER_URL}/data-lab/{PROJECT_UUID}'
    assert get_data_lab_project_url() == expected_project_url


def test_warning(t):
    with pytest.raises(t):
        warnings.warn(f"{t} warning should be thrown as an error by pytest in .py", t)


@pytest.mark.unit
def test_warning_as_error():
    for t in [UserWarning, SyntaxWarning, RuntimeWarning, FutureWarning, UnicodeWarning, BytesWarning,
              ResourceWarning, ImportWarning]:
        test_warning(t)
