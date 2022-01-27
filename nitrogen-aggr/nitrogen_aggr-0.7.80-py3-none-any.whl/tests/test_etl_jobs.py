"""
test_etl_jobs.py
~~~~~~~~~~~~~~~
This module contains unit tests for the transformation steps of the ETL
job defined in etl_job_base.py. It makes use of a local version of PySpark
that is bundled with the PySpark package.
"""

import pytest
import pandas as pd
from tests.spark_context_fixture import spark_context, spark_session
from dependencies import aws, config
from constants.constants_configs import ProjectTest, Config as Constant_Config
import os

CONFIG_PROJECT_TEST_FILE_NAME = 'project_test.yaml'

# this to create fixture for spark_sessions
pytestmark = pytest.mark.usefixtures("spark_session")


def get_test_etl_job_parameters():
    '''

    The unittest configuration and jobs are placed in configs/project/project_test.yaml file
    This function get the list of unittest jobs from the config file (test_etl_job.jobs) and
    provide it as a fixture to the test_etl_jobs function. Pytest generates one unittest per
    job.
    :return:
    '''
    project_configs = config.load_framework_config()[Constant_Config.PROJECT_TEST]
    return project_configs[ProjectTest.TEST_ETL_JOB][ProjectTest.TEST_ETL_JOB_JOBS]


@pytest.mark.parametrize('etl_job_test_module', get_test_etl_job_parameters())
def test_etl_jobs(spark_session, etl_job_test_module):
    """
    :param spark_session:
    :param etl_job_test_module:
    :return:
    """

    # get configuration values (stored in configs/project/project_test.yaml)
    project_config = config.load_framework_config()
    project_test_configs = project_config[Constant_Config.PROJECT_TEST]
    storage_bucket = project_test_configs[ProjectTest.AWS_TEST_DIRECTORY][ProjectTest.AWS_TEST_DIRECTORY_BUCKET]
    storage_key = project_test_configs[ProjectTest.AWS_TEST_DIRECTORY][ProjectTest.AWS_TEST_DIRECTORY_BASE_KEY]
    # storage_aws_path = f"s3a://{storage_bucket}/{storage_key}"
    data_path = os.environ['DATA_PATH'] # Example: ~/cadmium/cadmium/tests/pickle/
    storage_aws_path= data_path

    # get the test module_name, class name, function and version(datetime)
    # from the etl_job_test_module fixture
    module_name = etl_job_test_module[0]
    class_name = etl_job_test_module[1]
    func_name = etl_job_test_module[2]
    version = etl_job_test_module[3]  # datetime
    etl_name = module_name.split(".")[-1]

    file_name_args = "{}test_data-{}-{}-args_{}.json".format(
        storage_key, etl_name, func_name, version)
    file_path_input = "{}test_data-{}-{}-input_{}.pickle".format(
        storage_aws_path, etl_name, func_name, version)
    file_path_output = "{}test_data-{}-{}-output_{}.pickle".format(
        storage_aws_path, etl_name, func_name, version)

    cadmium_aws = aws.cadmium_aws()
    args_dict = cadmium_aws.read_json_from_bucket(storage_bucket, file_name_args)
    # the input data for testing
    input_df = spark_session.createDataFrame(pd.read_pickle(file_path_input))
    # the expected data for testing
    expected_output = pd.read_pickle(file_path_output)

    module = __import__(module_name)  # import module
    my_class = getattr(getattr(module, "etl_job_base"), class_name)
    instance = my_class()  # init class
    instance.set_spark_session(spark_session)  # set class config
    instance.set_config(args_dict['config'])  # set class config

    instance.set_log()
    args_2_plus = args_dict['args_2_plus']
    func = getattr(instance, func_name)

    # this generates the current output for the test input data
    output_df = func(input_df, *args_2_plus).toPandas()

    # assert test using pandas assert
    pd.testing.assert_frame_equal(output_df, expected_output)
