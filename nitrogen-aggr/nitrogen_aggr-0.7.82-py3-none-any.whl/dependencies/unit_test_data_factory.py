"""
unit testing handler
~~~~~~~
This module contains a function to take sample test_data from input and output of functions

The location to store test data is in AWS.
"""

import json
from dependencies.aws import cadmium_aws
from constants.constants_configs import ProjectTest, Config as Constant_Config
from datetime import datetime


def unit_test_data_factory(func):
    '''
    A decorator to generate sample data for functions.
    Assumptions about the function:
        1st argument is self
        2nd argument is a dataframe  (usually represents a large data)
        3rd and onwards are other config parameters (no large data)

    The decorator gets a fraction of input data (fraction is set in project_test config file) and calculates
    the expected output for that fraction. It stores that data into an AWS bucket (bucket and key are in configuration
    file)
    bucket and key are stored in project_test.yaml:
    aws_test_directory:
          bucket: "<BUCKET>"
          base_key: "<KEY>"
    There are three files that are stored in bucket/base_key folder:
    files are named:
        - test_data-<CLASS_NAME>-<METHOD_NAME>-args_<DATETIME>.json
            This file includes the config, vault and arguments (ARGS[2:])
        - test_data-<CLASS_NAME>-<METHOD_NAME>-input_<DATETIME>.pickle
            This file includes the sample of input dataframe (ARGS[1])
        - test_data-<CLASS_NAME>-<METHOD_NAME>-output_<DATETIME>.pickle
            This file includes the output for the sampled input

    The decorator then runs the function as normal.

    How to use it:
        1- upon completing or editing a  function and when you are confident that the function is operational and
        bug free, add the decorator label (`@unit_test_data_factory`) to top of the function,
        2- add `self.unittest_sampling_enabled = True` to the main function (before calling the transform)
        3- run the ETL job (function) for a dataset (could be a large dataset). After the job finishes, check for the newly generated sample files in
        aws. (check the logs for  file names).
        4- Remove the decorator label or set `self.unittest_sampling_enabled = False`.
        5- add to unittest conf:    add module_name, class name, function and version(datetime) to `configs/project/project_test.yaml`


    :param func:
    :return:
    '''
    def unittest_inner_function(*args, **kwargs):
        r = func(*args, **kwargs)
        # first argument is the self object
        self = args[0]

        if hasattr(self, "unittest_sampling_enabled"):
            unittest_sampling_enabled = self.unittest_sampling_enabled
        else:
            unittest_sampling_enabled = False

        # unit_test_data_factory configs
        project_test_configs = self.config[Constant_Config.FRAMEWORK][Constant_Config.PROJECT_TEST]
        current_datetime = datetime.now().strftime('%Y%m%d%H%M')
        if unittest_sampling_enabled:

            storage_bucket = project_test_configs[ProjectTest.AWS_TEST_DIRECTORY][ProjectTest.AWS_TEST_DIRECTORY_BUCKET]
            storage_key = project_test_configs[ProjectTest.AWS_TEST_DIRECTORY][ProjectTest.AWS_TEST_DIRECTORY_BASE_KEY]
            storage_aws_path = f"s3a://{storage_bucket}/{storage_key}"

            file_name_args = "{}test_data-{}-{}-args_{}.json".format(
                storage_key, self.__class__.__name__, func.__name__, current_datetime)
            file_path_input = "{}test_data-{}-{}-input_{}.pickle".format(
                storage_aws_path, self.__class__.__name__, func.__name__, current_datetime)
            file_path_output = "{}test_data-{}-{}-output_{}.pickle".format(
                storage_aws_path, self.__class__.__name__, func.__name__, current_datetime)


            # write other configuration arguments like
            args_dict = {
                "config": self.config,
                "vault": self.Vault,
                "args_2_plus": args[2:]
            }
            aws_conn = cadmium_aws()
            aws_conn.write_json_to_bucket(
                json.dumps(args_dict),
                storage_bucket,
                file_name_args
            )
            # args_dict_df = pd.DataFrame.from_dict(args_dict)
            # args_dict_df.to_pickle(file_name_args)

            # sample the input data
            input_spark_df = args[1].sample(
                True,
                project_test_configs[ProjectTest.TEST_DATA_FACTORY][ProjectTest.TEST_DATA_FACTORY_FRACTION],  seed=0
            ).limit(project_test_configs[ProjectTest.TEST_DATA_FACTORY][ProjectTest.TEST_DATA_FACTORY_LIMIT])

            args_2 = (self, input_spark_df) + args[2:]
            # use pandas in order to create one file
            input_spark_df.toPandas().to_pickle(
                file_path_input

            )
            # expected output for sample input
            expected_r = func(*args_2, **kwargs)

            # store expected output
            expected_r.toPandas().to_pickle(
                file_path_output
            )
            self.log.info(f"sample test data created at {file_name_args}, {file_path_input},  {file_path_output}")

        return r
    return unittest_inner_function

