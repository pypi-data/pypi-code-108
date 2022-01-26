import boto3
import os
import pandas as pd
import time

from datupapi.configure.config import Config


class DeepAR(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path
        self.forecast_types=[self.forecast_types[0],self.forecast_types[1],self.forecast_types[3],self.forecast_types[5],self.forecast_types[6]]


    def create_dataset_deepar(self, dataset_name, dataset_domain='RETAIL', dataset_type='TARGET_TIME_SERIES', related_dataset_dims=None, use_location=False):
        """
        Return a JSON response for AWS Forecast's create_dataset API calling

        :param dataset_name: Dataset's name to uniquely identify.
        :param dataset_domain: Dataset's industry-domain, such as RETAIL, INVENTORY_PLANNING and METRICS. Default RETAIL
        :param dataset_type: Dataset's dataset contents, such as TARGET_TIME_SERIES, RELATED_TIME_SERIES or ITEM_METADATA. Default TARGET_TIME_SERIES
        :param related_dataset_dims: Related dataset list of colums or dimensions. Only applies to RELATED_TIME_SERIES. Default None.
        :param use_location: True or false to use location column in the dataset. Default False.
        :return response: API's response

        >>> response = create_dataset_deepar(dataset_name='my_dataset', dataset_domain='RETAIL', dataset_type='TARGET_TIME_SERIES', use_location=False)
        >>> response = 'arn:aws:forecast:us-east-1:account-id:dataset/my_dataset'
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        try:
            if use_location is False:
                attributes_required = [
                    {
                        'AttributeName': 'timestamp',
                        'AttributeType': 'timestamp'
                    },
                    {
                        'AttributeName': 'item_id',
                        'AttributeType': 'string'
                    },
                    {
                        'AttributeName': 'demand',
                        'AttributeType': 'float'
                    }
                ]
                if dataset_type == 'TARGET_TIME_SERIES':
                    response = client.create_dataset(
                        DatasetName=dataset_name,
                        Domain=dataset_domain,
                        DatasetType=dataset_type,
                        DataFrequency=self.dataset_frequency,
                        Schema={
                            'Attributes': attributes_required
                        }
                    )
                else:
                    attributes_related = [{'AttributeName': col, 'AttributeType': 'float'} for col in related_dataset_dims[2:]]
                    response = client.create_dataset(
                        DatasetName=dataset_name,
                        Domain=dataset_domain,
                        DatasetType=dataset_type,
                        DataFrequency=self.dataset_frequency,
                        Schema={
                            'Attributes': attributes_required[:-1] + attributes_related
                        }
                    )
            else:
                attributes_required = [
                    {
                        'AttributeName': 'timestamp',
                        'AttributeType': 'timestamp'
                    },
                    {
                        'AttributeName': 'item_id',
                        'AttributeType': 'string'
                    },
                    {
                        'AttributeName': 'demand',
                        'AttributeType': 'float'
                    },
                    {
                        'AttributeName': 'location',
                        'AttributeType': 'string'
                    }
                ]
                if dataset_type == 'TARGET_TIME_SERIES':
                    response = client.create_dataset(
                        DatasetName=dataset_name,
                        Domain=dataset_domain,
                        DatasetType=dataset_type,
                        DataFrequency=self.dataset_frequency,
                        Schema={
                            'Attributes': attributes_required
                        }
                    )
                else:
                    attributes_related = [{'AttributeName': col, 'AttributeType': 'float'} for col in related_dataset_dims[3:]]
                    response = client.create_dataset(
                        DatasetName=dataset_name,
                        Domain=dataset_domain,
                        DatasetType=dataset_type,
                        DataFrequency=self.dataset_frequency,
                        Schema={
                            'Attributes': attributes_required[:2] + attributes_required[3:4] + attributes_related
                        }
                    )
        except client.exceptions.ResourceAlreadyExistsException as err:
            self.logger.exception(f'The dataset already exists. Please check dataset name: {err}')
            return False
        return response['DatasetArn']


    def create_dataset_group_deepar(self, dataset_group_name, dataset_group_domain='RETAIL', dataset_arns=None):
        """
        Return a JSON response for AWS Forecast's create_dataset_group API calling

        :param dataset_group_name: Dataset group's name to uniquely identify.
        :param dataset_group_domain: Dataset group's industry-domain, such as RETAIL, INVENTORY_PLANNING and METRICS. Default RETAIL
        :param dataset_arns: List of ARNs that identifies the datasets to include to the dataset group.
        :return response: API's response

        >>> response = create_dataset_group_deepar(dataset_group_name='my_dataset_group', dataset_group_domain='RETAIL', dataset_arns=['arn:aws:forecast:us-east-1:account-id:dataset/my_dataset'])
        >>> response = 'arn:aws:forecast:us-east-1:account-id:dataset-group/my_dataset_group'
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        try:
            response = client.create_dataset_group(
                DatasetGroupName=dataset_group_name,
                Domain=dataset_group_domain,
                DatasetArns=dataset_arns
            )
        except client.exceptions.ResourceAlreadyExistsException as err:
            self.logger.exception(f'The dataset already exists. Please check dataset name: {err}')
            return False
        except client.exceptions.ResourceNotFoundException as err:
            self.logger.exception(f'The dataset is not found. Please check dataset name: {err}')
            return False
        return response['DatasetGroupArn']


    def create_dataset_import_deepar(self, import_job, dataset_arn, import_type='TARGET_TIME_SERIES', import_path=None, timestamp_format='yyyy-MM-dd'):
        """
        Return a JSON response for AWS Forecast's create_dataset_import API calling

        :param import_job: Import job's name to uniquely identify.
        :param dataset_arn: ARNs that identifies the dataset to include to import.
        :param import_type: Dataset type to import. Either TARGET_TIME_SERIES or RELATED_TIME_SERIES.
        :param import_path: S3 bucket's path to import the dataset from. Do not include bucket's name.
        :param timestamp_format: Date or timestamp column format, such as yyyy-MM-dd or yyyy-MM-dd HH-mm-ss. Default yyyy-MM-dd
        :return response: API's response

        >>> response = create_dataset_import_deepar(import_job='my_import_job', dataset_arn='arn:aws:forecast:us-east-1:account-id:dataset/my_dataset', import_path='path/to/data.csv')
        >>> response = 'arn:aws:forecast:us-east-1:account-id:dataset-import-job/my_dataset/my_import_job'
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        try:
            if import_type=='TARGET_TIME_SERIES':
                response = client.create_dataset_import_job(
                    DatasetImportJobName=import_job,
                    DatasetArn=dataset_arn,
                    DataSource={
                        'S3Config': {
                            'Path': os.path.join('s3://', self.datalake, import_path),
                            'RoleArn': self.forecast_role
                        }
                    },
                    TimestampFormat=timestamp_format,
                    TimeZone='America/Bogota',
                    UseGeolocationForTimeZone=False
                )
            else:
                response = client.create_dataset_import_job(
                    DatasetImportJobName=import_job,
                    DatasetArn=dataset_arn,
                    DataSource={
                        'S3Config': {
                            'Path': os.path.join('s3://', self.datalake, import_path),
                            'RoleArn': self.forecast_role
                        }
                    },
                    TimestampFormat=timestamp_format,
                )
        except client.exceptions.ResourceAlreadyExistsException as err:
            self.logger.exception(f'The import job already exists. Please check job name: {err}')
            return False
        except client.exceptions.ResourceNotFoundException as err:
            self.logger.exception(f'The import job is not found. Please check job name: {err}')
            return False
        return response['DatasetImportJobArn']


    def create_predictor_automl(self,predictor_name, dataset_group_arn, use_location=False):
        """
                Return a JSON response for AWS Forecast's create_predictor API calling

                :param predictor_name: Predictor's name to uniquely identify.
                :param dataset_group_arn: ARNs that identifies the dataset group related to the target dataset.
                :param use_location: True or false to use location column in the dataset. Default False.
                :return response: API's response

                >>> response = create_predictor_deepar(predictor_name='my_predictor', dataset_group_arn='arn:aws:forecast:us-east-1:account-id:dataset-group/my_dataset_group', use_location=False)
                >>> response = 'arn:aws:forecast:us-east-1:147018152776:predictor/olimpica_predictor'
                """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        # Check dataset frequency
        try:
            if use_location:
                response = client.create_predictor(
                    PredictorName=predictor_name,
                    ForecastHorizon=self.forecast_horizon,
                    ForecastTypes=self.forecast_types,
                    PerformAutoML=True,
                    EvaluationParameters={
                        'NumberOfBacktestWindows': self.backtests,
                        'BackTestWindowOffset': self.backtest_horizon
                    },
                    InputDataConfig={
                        'DatasetGroupArn': dataset_group_arn,
                        'SupplementaryFeatures': [
                            {
                                'Name': 'holiday',
                                'Value': 'CO'
                            },
                        ]
                    },
                    FeaturizationConfig={
                        'ForecastFrequency': self.dataset_frequency,
                        'ForecastDimensions': [
                            'location',
                        ],
                        'Featurizations': [
                            {
                                'AttributeName': 'demand',
                                'FeaturizationPipeline': [
                                    {
                                        'FeaturizationMethodName': 'filling',
                                        'FeaturizationMethodParameters': {
                                            "aggregation": "sum",
                                            "backfill": "zero",
                                            "frontfill": "none",
                                            "middlefill": "zero"
                                        }
                                    },
                                ]
                            },
                        ]
                    }
                )
            else:
                response = client.create_predictor(
                    PredictorName=predictor_name,
                    ForecastHorizon=self.forecast_horizon,
                    ForecastTypes=self.forecast_types,
                    PerformAutoML=True,
                    EvaluationParameters={
                        'NumberOfBacktestWindows': self.backtests,
                        'BackTestWindowOffset': self.backtest_horizon
                    },
                    InputDataConfig={
                        'DatasetGroupArn': dataset_group_arn,
                        'SupplementaryFeatures': [
                            {
                                'Name': 'holiday',
                                'Value': 'CO'
                            },
                        ]
                    },
                    FeaturizationConfig={
                        'ForecastFrequency': self.dataset_frequency,
                        'Featurizations': [
                            {
                                'AttributeName': 'demand',
                                'FeaturizationPipeline': [
                                    {
                                        'FeaturizationMethodName': 'filling',
                                        'FeaturizationMethodParameters': {
                                            "aggregation": "sum",
                                            "backfill": "zero",
                                            "frontfill": "none",
                                            "middlefill": "zero"
                                        }
                                    },
                                ]
                            },
                        ]
                    }
                )
        except client.exceptions.ResourceAlreadyExistsException as err:
            self.logger.exception(f'The predictor already exists. Please predictor name: {err}')
            return False
        except client.exceptions.ResourceNotFoundException as err:
            self.logger.exception(f'The predictor is not found. Please predictor name: {err}')
            return False
        except client.exceptions.ResourceInUseException as err:
            self.logger.exception(f'Dataset creation in progress. Please wait some minutes: {err}')
            return False
        return response['PredictorArn']


    def create_predictor_deepar(self, predictor_name, dataset_group_arn, use_location=False):
        """
        Return a JSON response for AWS Forecast's create_predictor API calling

        :param predictor_name: Predictor's name to uniquely identify.
        :param dataset_group_arn: ARNs that identifies the dataset group related to the target dataset.
        :param use_location: True or false to use location column in the dataset. Default False.
        :return response: API's response

        >>> response = create_predictor_deepar(predictor_name='my_predictor', dataset_group_arn='arn:aws:forecast:us-east-1:account-id:dataset-group/my_dataset_group', use_location=False)
        >>> response = 'arn:aws:forecast:us-east-1:147018152776:predictor/olimpica_predictor'
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        # Check dataset frequency
        if self.dataset_frequency == 'D':
            context_length_min = 7
            context_length_max = 365
        elif self.dataset_frequency == 'W':
            context_length_min = 2
            context_length_max = 52
        elif self.dataset_frequency == 'M':
            context_length_min = 1
            context_length_max = 12
        elif self.dataset_frequency == 'Y':
            context_length_min = 1
            context_length_max = 3
        else:
            self.logger.debug('No valid option. Please check config file.')
        try:
            if use_location:
                response = client.create_predictor(
                    PredictorName=predictor_name,
                    AlgorithmArn='arn:aws:forecast:::algorithm/Deep_AR_Plus',
                    ForecastHorizon=self.forecast_horizon,
                    ForecastTypes=self.forecast_types,
                    PerformAutoML=False,
                    PerformHPO=True,
                    TrainingParameters={
                        "context_length": str(self.input_window),
                        "epochs": str(self.epochs),
                        "learning_rate": "0.03623715680834933",
                        "learning_rate_decay": "0.5",
                        "likelihood": "student-t",
                        "max_learning_rate_decays": "0",
                        "num_averaged_models": "1",
                        "num_cells": str(self.neurons),
                        "num_layers": str(self.hidden_layers),
                        "prediction_length": str(self.forecast_horizon)
                    },
                    EvaluationParameters={
                        'NumberOfBacktestWindows': self.backtests,
                        'BackTestWindowOffset': self.backtest_horizon
                    },
                    HPOConfig={
                        'ParameterRanges': {
                            'ContinuousParameterRanges': [
                                {
                                    'Name': 'learning_rate',
                                    'MaxValue': 0.1,
                                    'MinValue': 0.0001,
                                    'ScalingType': 'Logarithmic'
                                },
                            ],
                            'IntegerParameterRanges': [
                                {
                                    'Name': 'context_length',
                                    'MaxValue': context_length_max,
                                    'MinValue': context_length_min,
                                    'ScalingType': 'Auto'
                                },
                            ]
                        }
                    },
                    InputDataConfig={
                        'DatasetGroupArn': dataset_group_arn,
                        'SupplementaryFeatures': [
                            {
                                'Name': 'holiday',
                                'Value': 'CO'
                            },
                        ]
                    },
                    FeaturizationConfig={
                        'ForecastFrequency': self.dataset_frequency,
                        'ForecastDimensions': [
                            'location',
                        ],
                        'Featurizations': [
                            {
                                'AttributeName': 'demand',
                                'FeaturizationPipeline': [
                                    {
                                        'FeaturizationMethodName': 'filling',
                                        'FeaturizationMethodParameters': {
                                            "aggregation": "sum",
                                            "backfill": "zero",
                                            "frontfill": "none",
                                            "middlefill": "zero"
                                        }
                                    },
                                ]
                            },
                        ]
                    }
                )
            else:
                response = client.create_predictor(
                    PredictorName=predictor_name,
                    AlgorithmArn='arn:aws:forecast:::algorithm/Deep_AR_Plus',
                    ForecastHorizon=self.forecast_horizon,
                    ForecastTypes=self.forecast_types,
                    PerformAutoML=False,
                    PerformHPO=True,
                    TrainingParameters={
                        "context_length": str(self.input_window),
                        "epochs": str(self.epochs),
                        "learning_rate": "0.03623715680834933",
                        "learning_rate_decay": "0.5",
                        "likelihood": "student-t",
                        "max_learning_rate_decays": "0",
                        "num_averaged_models": "1",
                        "num_cells": str(self.neurons),
                        "num_layers": str(self.hidden_layers),
                        "prediction_length": str(self.forecast_horizon)
                    },
                    EvaluationParameters={
                        'NumberOfBacktestWindows': self.backtests,
                        'BackTestWindowOffset': self.backtest_horizon
                    },
                    HPOConfig={
                        'ParameterRanges': {
                            'ContinuousParameterRanges': [
                                {
                                    'Name': 'learning_rate',
                                    'MaxValue': 0.1,
                                    'MinValue': 0.0001,
                                    'ScalingType': 'Logarithmic'
                                },
                            ],
                            'IntegerParameterRanges': [
                                {
                                    'Name': 'context_length',
                                    'MaxValue': context_length_max,
                                    'MinValue': context_length_min,
                                    'ScalingType': 'Auto'
                                },
                            ]
                        }
                    },
                    InputDataConfig={
                        'DatasetGroupArn': dataset_group_arn,
                        'SupplementaryFeatures': [
                            {
                                'Name': 'holiday',
                                'Value': 'CO'
                            },
                        ]
                    },
                    FeaturizationConfig={
                        'ForecastFrequency': self.dataset_frequency,
                        'Featurizations': [
                            {
                                'AttributeName': 'demand',
                                'FeaturizationPipeline': [
                                    {
                                        'FeaturizationMethodName': 'filling',
                                        'FeaturizationMethodParameters': {
                                            "aggregation": "sum",
                                            "backfill": "zero",
                                            "frontfill": "none",
                                            "middlefill": "zero"
                                        }
                                    },
                                ]
                            },
                        ]
                    }
                )
        except client.exceptions.ResourceAlreadyExistsException as err:
            self.logger.exception(f'The predictor already exists. Please predictor name: {err}')
            return False
        except client.exceptions.ResourceNotFoundException as err:
            self.logger.exception(f'The predictor is not found. Please predictor name: {err}')
            return False
        except client.exceptions.ResourceInUseException as err:
            self.logger.exception(f'Dataset creation in progress. Please wait some minutes: {err}')
            return False
        return response['PredictorArn']


    def create_backtest_export_deepar(self, export_job, predictor_arn, export_path):
        """
        Return a JSON response for AWS Forecast's create_predictor_backtest_export_job API calling

        :param export_job: Export job's name to uniquely identify.
        :param predictor_arn: ARNs that identifies the predictor that produced backtesting.
        :param export_path: S3 bucket's path to export the backtests. Do not include bucket's name.
        :return response: API's response

        >>> response = create_backtest_export_deepar(export_job='my_export', predictor_arn='arn:aws:forecast:us-east-1:account-id:predictor/my_predictor', export_path='path/to/export')
        >>> response = 'arn:aws:forecast:us-east-1:147018152776:predictor-backtest-export-job/my_backtest_export'
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        try:
            response = client.create_predictor_backtest_export_job(
                PredictorBacktestExportJobName=export_job,
                PredictorArn=predictor_arn,
                Destination={
                    'S3Config': {
                        'Path': os.path.join('s3://', self.datalake, export_path),
                        'RoleArn': self.forecast_role
                    }
                }
            )
        except client.exceptions.ResourceAlreadyExistsException as err:
            self.logger.exception(f'The backtest export already exists. Please backtest export name: {err}')
            return False
        except client.exceptions.ResourceNotFoundException as err:
            self.logger.exception(f'The backtest export is not found. Please backtest export name: {err}')
            return False
        except client.exceptions.ResourceInUseException as err:
            self.logger.exception(f'Predictor creation in progress. Please wait some minutes: {err}')
            return False
        return response['PredictorBacktestExportJobArn']


    def list_dataset_import_deepar(self):
        """
        Return a JSON response for AWS Forecast's list_dataset_import_jobs API calling

        :return response: API's response

        >>> response = list_dataset_import_deepar()
        >>> response = {'DatasetImportJobArn': 'arn:aws:forecast:us-east-1:147018152776:dataset-import-job/my_import_job'}
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        response = client.list_dataset_import_jobs(
            MaxResults = 100,
            Filters = [
                {
                    "Condition": "IS_NOT",
                    "Key": "Status",
                    "Value": "ACTIVE"
                }
            ]
        )
        return response['DatasetImportJobs']


    def list_predictors_deepar(self):
        """
        Return a JSON response for AWS Forecast's list_predictors API calling

        :return response: API's response

        >>> response = list_predictors_deepar()
        >>> response = {'PredictorArn': 'arn:aws:forecast:us-east-1:147018152776:predictor/my_predictor'}
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        response = client.list_predictors(
            MaxResults = 100,
            Filters = [
                {
                    "Condition": "IS_NOT",
                    "Key": "Status",
                    "Value": "ACTIVE"
                }
            ]
        )
        return response['Predictors']


    def delete_dataset_group_deepar(self, arn_datasetgroup):
        """
        Delete the specified dataset group resource

        :param arn_datasetgroup: ARNs that identifies the dataset group.
        :return None:

        >>> delete_dataset_group_deepar(arn_datasetgroup='arn:aws:forecast:us-east-1:147018152776:dataset-group/my_datasetgroup')
        >>> None
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        response = client.delete_dataset_group(DatasetGroupArn=arn_datasetgroup)
        time.sleep(60)
        return None


    def delete_predictor_deepar(self, arn_predictor):
        """
        Delete the specified predictor resource

        :param arn_predictor: ARNs that identifies the predictor.
        :return None:

        >>> delete_predictor_deepar(arn_predictor='arn:aws:forecast:us-east-1:147018152776:predictor/my_predictor')
        >>> None
        """
        client = boto3.client('forecast',
                              region_name=self.region,
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key
                              )
        response = client.delete_predictor(PredictorArn=arn_predictor)
        time.sleep(300)
        return None


    def check_status(self, arn_target, check_type):
        """
        Return a True or False flag to determine whether the status in progress

        :param arn_target: ARN to check with the API calling to resources in progress
        :param check_type: Type of status check, either import or predictor
        :return False: Determine the status check is done

        >>> check_status(arn_target='arn:aws:forecast:us-east-1:147018152776:predictor/my_predcitor', check_type='predictor')
        >>> False
        """
        in_progress = True
        if check_type == 'import':
            while in_progress:
                in_progress = any(arn['DatasetImportJobArn'] == arn_target for arn in self.list_dataset_import_deepar())
                time.sleep(300)
        elif check_type == 'predictor':
            while in_progress:
                in_progress = any(arn['PredictorArn'] == arn_target for arn in self.list_predictors_deepar())
                time.sleep(300)
        else:
            self.logger.debug(f'Invalid check type option. Choose from import or predictor')
        return in_progress

