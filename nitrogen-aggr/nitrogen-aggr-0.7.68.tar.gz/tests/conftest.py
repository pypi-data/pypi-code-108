"""
conftest.py
~~~~~~~~~~~~~~~

https://docs.pytest.org/en/latest/parametrize.html#pytest-generate-tests
"""
import pytest
import pandas as pd
from tests.spark_context_fixture import spark_context, spark_session
from dependencies import aws, config

pytestmark = pytest.mark.usefixtures("spark_session")
CONFIG_PROJECT_TEST_FILE_NAME = 'project_test.yaml'


def get_test_etl_job_parameters():
    '''

    :return:
    '''
    project_configs =  config.load_framework_config()[CONFIG_PROJECT_TEST_FILE_NAME]
    return project_configs['test_etl_job']['jobs']


def pytest_generate_tests(metafunc):
    '''

    :param metafunc:
    :return:
    '''
    if "etl_job_test_modules" in metafunc.fixturenames:
        metafunc.parametrize("etl_job_test_module", get_test_etl_job_parameters())
