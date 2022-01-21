# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
import base64
import json
import os
import random
import requests
import time
import uuid

from datetime import datetime, timedelta
from retry import retry

from ibm_ai_openscale_cli import logging_temp_file, name as cli_name
from ibm_ai_openscale_cli.api_environment import ApiEnvironment
from ibm_ai_openscale_cli.enums import MLEngineType, Environment
from ibm_ai_openscale_cli.models.model import Model
from ibm_ai_openscale_cli.openscale.openscale_reset import OpenScaleReset
from ibm_ai_openscale_cli.utility_classes.constants import DRIFT_ARCHIVE_ENV_MAPPING, WML_CHALLENGER_ENVIRONMENT_MAPPING, WML_SPARK_VERSION_SUPPORT_MAPPING
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from ibm_ai_openscale_cli.utility_classes.utils import remove_port_from_url, update_url, get_url_elements

from ibm_watson_openscale.base_classes.watson_open_scale_v2 import COSTrainingDataReferenceLocation, COSTrainingDataReferenceConnection, SparkStruct, TrainingDataReference, FileTrainingDataReferenceOptions, Target, WMLCredentialsCloud, WMLCredentialsCP4D, Asset, AssetDeploymentRequest, AssetPropertiesRequest, Records, PatchDocument, Measurements, DatabaseConfigurationRequest, LocationSchemaName, PrimaryStorageCredentialsLong
from ibm_watson_openscale.supporting_classes.enums import DatabaseType, InputDataType, ProblemType, ServiceTypes, DataSetTypes, TargetTypes, AssetTypes, DeploymentTypes
from ibm_watson_openscale.supporting_classes.payload_record import PayloadRecord

logger = FastpathLogger(__name__)
parent_dir = os.path.dirname(__file__)

OPERATIONAL_PRE_PRODUCTION_SPACE_ID = "pre_production"
OPERATIONAL_PRODUCTION_SPACE_ID = "production"
SERVICE_PROVIDER_NAME = "WOS ExpressPath WML {} binding"

class OpenScaleClient(OpenScaleReset):

    def __init__(self, args, credentials, database_credentials, ml_engine_credentials):
        super().__init__(args, credentials, database_credentials, ml_engine_credentials)
        self.is_mrm_challenger = False
        self.is_mrm_preprod = False
        self.is_mrm_prod = False
        self.mrm_preprod_subscription_id = None
        self.mrm_challenger_instance_id = None
        self.mrm_preprod_instance_id = None
        self.mrm_prod_instance_id = None
        self._binding_id = None
        self._binding_id_mrm_preprod = None
        self.metric_check_errors = [["model-name", "metric", "status"]]
        self.set_iam_headers()

    def set_model(self, model):
        self._model = model
        self._subscription_id = None
        self._asset_details_dict = None
        self._fairness_run_once = True
        self._explainability_run_once = True
        self._use_bkpi = False
        self._configure_explain = True

    def set_cos_credentials(self, _cos_credentials):
        self._cos_credentials = _cos_credentials

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_get_or_create_bucket(self, _cos_instance):
        bucket = _cos_instance.get_wos_bucket()
        if not bucket:
            bucket = _cos_instance.create_wos_bucket()
        return bucket.name

    def perform_cos_operations(self, _cos_instance):
        self._cos_instance = _cos_instance
        logger.log_info("Checking for OpenScale ExpresPath bucket ...")
        bucket_name = self._reliable_get_or_create_bucket(_cos_instance)
        self._cos_train_data_bucket_name = bucket_name
        # delete existing training data and re-upload
        self._cos_train_data_file_name = '{}_{}_{}'.format(self._model.name, self._args.env_dict['name'], Model.TRAINING_DATA_CSV_FILENAME)

        logger.log_info("Deleting existing training data file if already present ...")
        _cos_instance.delete_item(
            bucket_name=bucket_name,
            item_name=self._cos_train_data_file_name
        )
        logger.log_info("Uploading training data file: {}".format(bucket_name))
        _cos_instance.multi_part_upload(
            bucket_name=bucket_name,
            item_name=self._cos_train_data_file_name,
            file_path_w_name=self._model.training_data_csv_file
        )

    def get_deployment_id(self):
        return self._asset_details_dict['source_entry_metadata_guid']

    def get_asset_id(self):
        return self._asset_details_dict['source_uid']

    def get_binding_id(self):
        if self.is_mrm_challenger or self.is_mrm_preprod:
            return self._binding_id_mrm_preprod
        return self._binding_id

    def get_subscription_id(self):
        return self._subscription_id

    def is_unstructured_text(self):
        return self._model.is_unstructured_text

    def is_unstructured_image(self):
        return self._model.is_unstructured_image

    def get_datamart_details(self):
        return self._client.data_marts.get(data_mart_id=self._credentials['data_mart_id'])
    
    def get_data_mart_count(self):
        """
        Returns the number of data marts present in the OpenScale instance.
        """
        data_marts_count = None
        list_data_mart_response = self._client.data_marts.list().result
        data_marts_count = len(list_data_mart_response.data_marts)
        return data_marts_count

    def set_iam_headers(self):
        token = self._args.iam_token if self._args.iam_token else self._client.authenticator.token_manager.get_token()
        self.iam_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token)
        }

    def create_datamart(self):
        '''
        Create datamart schema and datamart
        '''
        logger.log_info('Creating datamart {} ...'.format(self._datamart_name))

        if self._database is None:
            logger.log_info('PostgreSQL instance: internal')
        else:
            self._reliable_create_schema()
        self._reliable_create_datamart()
        logger.log_info('Datamart {} created successfully'.format(self._datamart_name))

    @retry(tries=3, delay=5, backoff=2)
    def _reliable_create_schema(self):
        self._database.create_new_schema(self._datamart_name, self._keep_schema)

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_create_datamart(self):
        start = time.time()
        if self._database is None:
            self._client.data_marts.add(name=self._datamart_name, internal_database=True, background_mode=False)
        else:
            db_config_request = None
            if self._database_credentials['db_type'] == 'postgresql':
                if 'instance_administration_api' in self._database_credentials and 'connection' in self._database_credentials:
                    db_config_request = DatabaseConfigurationRequest(
                        database_type=DatabaseType.POSTGRESQL,
                        instance_id=self._database_credentials['instance_administration_api']['instance_id'],
                        credentials=PrimaryStorageCredentialsLong(
                            hostname=self._database_credentials['connection']['postgres']['hosts'][0]['hostname'],
                            username=self._database_credentials['connection']['postgres']['authentication']['username'],
                            password=self._database_credentials['connection']['postgres']['authentication']['password'],  # pragma: allowlist secret
                            db=self._database_credentials['connection']['postgres']['database'],
                            port=self._database_credentials['connection']['postgres']['hosts'][0]['port'],
                            ssl=True,
                            sslmode=self._database_credentials['connection']['postgres']['query_options']['sslmode'],
                            certificate_base64=self._database_credentials['connection']['postgres']['certificate']['certificate_base64']
                        ),
                        location=LocationSchemaName(schema_name=self._datamart_name)
                    )
                else:
                    raise Exception("Non ICD Postgres not supported at this time")
            elif self._database_credentials['db_type'] == 'db2':
                use_ssl_flag = True if "ssl" in self._database_credentials and self._database_credentials["ssl"] is True else False
                if 'certificate_base64' in self._database_credentials and self._database_credentials['certificate_base64'] is not None and self._database_credentials['ssl']:
                    db2_crendentials = PrimaryStorageCredentialsLong(
                        hostname=self._database_credentials['hostname'],
                        username=self._database_credentials['username'],
                        password=self._database_credentials['password'],
                        db=self._database_credentials['db'],
                        port=self._database_credentials['port'],
                        ssl=True,
                        certificate_base64=self._database_credentials['certificate_base64']
                    )
                else:
                    db2_crendentials = PrimaryStorageCredentialsLong(
                            hostname=self._database_credentials['hostname'],
                            username=self._database_credentials['username'],
                            password=self._database_credentials['password'],
                            db=self._database_credentials['db'],
                            port=self._database_credentials['port'],
                            ssl=use_ssl_flag
                    )

                db_config_request = DatabaseConfigurationRequest(
                    database_type=DatabaseType.DB2,
                    credentials=db2_crendentials,
                    location=LocationSchemaName(schema_name=self._datamart_name)
                )
            else:
                raise Exception('Unsupported database type: "{}"'.format(self._database_credentials['db_type']))
            try:
                if not self._args.is_icp:
                    self._client.data_marts.add(
                        service_instance_crn=self._credentials['crn'],
                        background_mode=False,
                        name=self._datamart_name,
                        description="Data Mart created by OpenScale ExpressPath",
                        database_configuration=db_config_request
                    )
                else:
                    self._client.data_marts.add(
                        background_mode=False,
                        name=self._datamart_name,
                        description="Data Mart created by OpenScale ExpressPath",
                        database_configuration=db_config_request
                    )
            except Exception as e:
                raise Exception("Failed while creating datamart with the specified database instance: {}".format(str(e)))

        elapsed = time.time() - start
        self.timer('data_mart.setup', elapsed)

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_bind_mlinstance(self, credentials, ml_engine=None, is_mrm_preprod=False):
        # if self._args.ml_engine_type is MLEngineType.WML:
        #     if self._args.is_icp:
        #         if 'apikey' in credentials:
        #             ml_instance = WMLCredentialsCloud(credentials)
        #             binding_name = 'IBM Cloud {}'.format(binding_name)
        #         else:
        #             if self._args.wml or self._args.wml_json:
        #                 ml_instance = WMLCredentialsCP4D(credentials)
        #                 binding_name = 'Remote ICP {}'.format(binding_name)
        #             else:
        #                 credentials = {}
        #                 ml_instance = WMLCredentialsCP4D()
        #                 binding_name = 'ICP {}'.format(binding_name)
        #     else:
        #         ml_instance = WMLCredentialsCloud(credentials)
        # elif self._args.ml_engine_type is MLEngineType.AZUREMLSTUDIO:
        #     ml_instance = AzureCredentials(credentials)
        # elif self._args.ml_engine_type is MLEngineType.AZUREMLSERVICE:
        #     ml_instance = AzureCredentials(credentials)
        # elif self._args.ml_engine_type is MLEngineType.SPSS:
        #     ml_instance = SPSSCredentials(credentials)
        # elif self._args.ml_engine_type is MLEngineType.CUSTOM:
        #     ml_instance = CustomCredentials(credentials)
        # elif self._args.ml_engine_type is MLEngineType.SAGEMAKER:
        #     ml_instance = SageMakerCredentials(credentials)


        start = time.time()
        if not self._args.is_icp:
            bindings_url = "{}/openscale/{}/v2/service_providers".format(self._credentials['url'], self._credentials['data_mart_id'])

            logger.log_info("Not using ML Instance information in the add service provider call ...")
            if is_mrm_preprod:
                operational_space_id = OPERATIONAL_PRE_PRODUCTION_SPACE_ID
            else:
                operational_space_id = OPERATIONAL_PRODUCTION_SPACE_ID
            payload = {
                "name": SERVICE_PROVIDER_NAME.format(operational_space_id),
                "description": "WML Instance designated as {}".format(operational_space_id),
                "service_type": "watson_machine_learning",
                "credentials": {},
                "operational_space_id": operational_space_id,
                "deployment_space_id": ml_engine.space_id
            }

            binding_details = requests.post(bindings_url, json=payload, headers=self.iam_headers, verify=self._verify).json()
            if is_mrm_preprod:
                self._binding_id_mrm_preprod = binding_details["metadata"]["id"]
            else:
                self._binding_id = binding_details["metadata"]["id"]

            binding_details = requests.get(bindings_url, headers=self.iam_headers, verify=self._verify).json()

            if 'entity' in binding_details:
                if 'status' in binding_details['entity']:
                    if 'state' in binding_details['entity']['status']:
                        for i in range(12):
                            # binding_details = self._client.service_providers.get(self._binding_id).get_result()
                            binding_details = requests.get(bindings_url, headers=self.iam_headers, verify=self._verify).json()
                            service_providers = binding_details['service_providers']
                            for sp in service_providers:
                                if sp['metadata']['id'] == self._binding_id:
                                    state = sp["entity"]["status"]["state"]
                                    _msg = "Service provider status = {}".format(state)
                                    if state == "active":
                                        logger.log_info(_msg)
                                        break
                                    if state == "error":
                                        logger.log_info(_msg)
                                        raise Exception("Service provider add failed.")
                                    else:
                                        _msg = _msg + ', rechecking in 5 seconds ...'
                                        logger.log_info(_msg)
                                        time.sleep(5)
                            if state == "active":
                                _msg = "Service provider status = {}".format(state)
                                break

            logger.log_info('Waiting 15 seconds for the binding to be complete ...')
            time.sleep(15)

            elapsed = time.time() - start
            logger.log_info('Binding {} created successfully'.format(self.get_binding_id()))
        else:
            wml_service_provider_creds = WMLCredentialsCP4D.from_dict({})
            if is_mrm_preprod:
                operational_space_id = OPERATIONAL_PRE_PRODUCTION_SPACE_ID
            else:
                operational_space_id = OPERATIONAL_PRODUCTION_SPACE_ID
            service_provider_result = self._client.service_providers.add(
                name=SERVICE_PROVIDER_NAME.format(operational_space_id),
                description="Service Provider added by OpenScale Express Path",
                service_type=ServiceTypes.WATSON_MACHINE_LEARNING,
                credentials=wml_service_provider_creds,
                operational_space_id=operational_space_id,
                deployment_space_id=ml_engine.space_id,
                background_mode=False
            ).result
            this_binding_id = service_provider_result.metadata.id
            if is_mrm_preprod:
                self._binding_id_mrm_preprod = this_binding_id
            else:
                self._binding_id = this_binding_id
            elapsed = time.time() - start
            logger.log_info('Binding {} {} created successfully'.format(operational_space_id, this_binding_id))

        self.timer('data_mart.bindings.add', elapsed)

    def bind_mlinstance(self, credentials, ml_engine_prod=None, ml_engine_preprod=None):
        logger.log_info('Binding {} instance to {} ...'.format(self._args.ml_engine_type.name.lower(), self._args.service_name))
        self._reliable_bind_mlinstance(credentials, ml_engine_prod, is_mrm_preprod=False)
        if self._args.mrm:
            self._reliable_bind_mlinstance(credentials, ml_engine_preprod, is_mrm_preprod=True)

    def use_existing_binding(self, asset_details_dict):
        if self._args.v4:
            service_providers = self._client.service_providers.list().result.service_providers
            for service_provider in service_providers:
                provider_name = service_provider.entity.name
                provider_id = service_provider.metadata.id
                if provider_name == SERVICE_PROVIDER_NAME.format(OPERATIONAL_PRODUCTION_SPACE_ID):
                    self._binding_id = provider_id
                elif provider_name == SERVICE_PROVIDER_NAME.format(OPERATIONAL_PRE_PRODUCTION_SPACE_ID):
                    self._binding_id_mrm_preprod = provider_id
        else:
            self._binding_id = asset_details_dict["binding_uid"]
        logger.log_info("Use existing binding {}".format(self.get_binding_id()))

    @retry(tries=5, delay=4, backoff=2)
    def use_existing_subscription(self, asset_details_dict):
        self._asset_details_dict = asset_details_dict
        asset_uid = asset_details_dict['source_uid']
        deployment_uid = asset_details_dict['source_entry_metadata_guid']
        logger.log_info('Get existing subscription for model {} deployment {}...'.format(asset_uid, deployment_uid))
        start = time.time()
        all_subscriptions = self._client.subscriptions.list().result.subscriptions
        elapsed = time.time() - start
        self.timer('data_mart.subscriptions.get_details(ALL)', elapsed)
        subscription_id = None
        for sub_response in all_subscriptions:
            sub = sub_response.to_dict()
            if 'entity' in sub and 'asset' in sub['entity'] and 'asset_id' in sub['entity']['asset']:
                if sub['entity']['asset']['asset_id'] == asset_uid and 'deployment' in sub['entity']:
                        if 'deployment_id' in sub['entity']['deployment'] and sub['entity']['deployment']['deployment_id'] == deployment_uid:
                            if 'metadata' in sub and 'id' in sub['metadata']:
                                self._subscription_id = sub['metadata']['id']
        if not self._subscription_id:
            error_msg = 'ERROR: Could not find an existing subscription for model {} deployment {}'.format(asset_uid, deployment_uid)
            logger.log_error(error_msg)
            raise Exception(error_msg)
        self._payload_dataset_id = self._client.data_sets.list(
                                        type=DataSetTypes.PAYLOAD_LOGGING,
                                        target_target_id=self._subscription_id,
                                        target_target_type=TargetTypes.SUBSCRIPTION
                                    ).result.data_sets[0].metadata.id
        elapsed = time.time() - start
        self._model.expected_payload_row_count = self._reliable_count_payload_rows('use existing subscription')
        logger.log_info('Subscription {} found successfully'.format(self.get_subscription_id()))
        self._reliable_count_datamart_rows('use existing subscription')

    @retry(tries=1, delay=4, backoff=2)
    def subscribe_to_model_deployment(self, asset_details_dict):
        '''
        Create subscription for the given model
        '''
        logger.log_info('Subscribing ML deployment to {} ...'.format(self._args.service_name))
        self._reliable_count_datamart_rows('create subscription start')
        asset_metadata = self._model.configuration_data['asset_metadata']
        # asset_params = {
        #     'source_uid': asset_details_dict['source_uid'],
        #     'binding_uid': self.get_binding_id()
        # }
        # if 'problem_type' in asset_metadata:
        #     asset_params['problem_type'] = self._get_problem_type_object(asset_metadata['problem_type'])
        # if 'input_data_type' in asset_metadata:
        #     asset_params['input_data_type'] = self._get_input_data_type_object(asset_metadata['input_data_type'])
        # if self._model.training_data_reference:
        #     asset_params['training_data_reference'] = self._model.training_data_reference['cos_storage_reference']
        # if 'label_column' in asset_metadata:
        #     asset_params['label_column'] = asset_metadata['label_column']
        # if 'prediction_column' in asset_metadata:
        #     asset_params['prediction_field'] = asset_metadata['prediction_column']
        # if 'class_probability_columns' in asset_metadata:
        #     asset_params['class_probability_columns'] = asset_metadata['class_probability_columns']
        # if 'probability_column' in asset_metadata:
        #     asset_params['probability_column'] = asset_metadata['probability_column']
        # if 'feature_columns' in asset_metadata:
        #     asset_params['feature_fields'] = asset_metadata['feature_columns']
        # if 'categorical_columns' in asset_metadata:
        #     asset_params['categorical_fields'] = asset_metadata['categorical_columns']
        # ml_asset = None
        # if self._args.ml_engine_type is MLEngineType.WML:
        #     ml_asset = WatsonMachineLearningAsset(**asset_params)
        # elif self._args.ml_engine_type is MLEngineType.AZUREMLSTUDIO:
        #     ml_asset = AzureMachineLearningStudioAsset(**asset_params)
        # elif self._args.ml_engine_type is MLEngineType.AZUREMLSERVICE:
        #     ml_asset = AzureMachineLearningServiceAsset(**asset_params)
        # elif self._args.ml_engine_type is MLEngineType.SPSS:
        #     ml_asset = SPSSMachineLearningAsset(**asset_params)
        # elif self._args.ml_engine_type is MLEngineType.CUSTOM:
        #     ml_asset = CustomMachineLearningAsset(**asset_params)
        # elif self._args.ml_engine_type is MLEngineType.SAGEMAKER:
        #     ml_asset = SageMakerMachineLearningAsset(**asset_params)

        start = time.time()
        deployment_uid = asset_details_dict['source_entry_metadata_guid']
        asset_details_dict['binding_id'] = self.get_binding_id()

        # Calling the Discovery service to get the schema for subscription creation
        deployment_space_id = asset_details_dict["model_url"].split("space_id=")[1].split("&")[0]
        discovery_response = self._client.service_providers.get_deployment_asset(self._credentials['data_mart_id'], self.get_binding_id(), deployment_uid, deployment_space_id=deployment_space_id)

        created_at = discovery_response["entity"]["asset"]["created_at"]
        spark_input_data_schema = SparkStruct.from_dict(discovery_response["entity"]["asset_properties"]["input_data_schema"])
        spark_training_data_schema = SparkStruct.from_dict(discovery_response["entity"]["asset_properties"]["training_data_schema"])
        asset_properties_request = AssetPropertiesRequest(
            label_column=asset_metadata['label_column'],
            probability_fields=['probability'],
            prediction_field=asset_metadata['prediction_column'],
            feature_fields=asset_metadata['feature_columns'],
            categorical_fields=asset_metadata['categorical_columns'],
            input_data_schema=spark_input_data_schema,
            training_data_schema=spark_training_data_schema
        )

        subscription_details = self._client.subscriptions.add(
            data_mart_id=self._credentials["data_mart_id"],
            service_provider_id=self.get_binding_id(),
            asset=Asset(
                name=asset_details_dict["model_name"],
                asset_id=asset_details_dict["source_uid"],
                url=asset_details_dict["model_url"],
                asset_type=AssetTypes.MODEL,
                input_data_type=self._get_input_data_type_object(asset_metadata["input_data_type"]),
                problem_type=self._get_problem_type_object(asset_metadata["problem_type"]),
                created_at=created_at
            ),
            deployment=AssetDeploymentRequest(
                deployment_id=deployment_uid,
                name=asset_details_dict["deployment_name"],
                deployment_type=DeploymentTypes.ONLINE,
                url=asset_details_dict["deployment_url"],
            ),
            asset_properties=asset_properties_request,
            background_mode=False
        ).result
        self._subscription_id = subscription_details.metadata.id
        
        details_json = subscription_details.to_dict()
        status = details_json["entity"]["status"]["state"]
        if status != "active":
            logger.log_error("Error in subscription: {}".format(json.dumps(details_json)))
            raise Exception("Adding subscription failed with status {}!".format(status))

        logger.log_info("Subscription_id: {}".format(self._subscription_id))
        self._client.data_sets.show()
        self._payload_dataset_id = self._client.data_sets.list(
                                        type=DataSetTypes.PAYLOAD_LOGGING,
                                        target_target_id=self._subscription_id,
                                        target_target_type=TargetTypes.SUBSCRIPTION
                                    ).result.data_sets[0].metadata.id
        elapsed = time.time() - start
        self._asset_details_dict = asset_details_dict
        self._model.expected_payload_row_count = self._reliable_count_payload_rows('subscription created')
        logger.log_info('Subscription completed successfully (guid: {})'.format(self.get_subscription_id()))
        self.timer('data_mart.subscriptions.add', elapsed)
        self._reliable_count_datamart_rows('create subscription completed')

    def _get_input_data_type_object(self, data):
        if data == 'STRUCTURED':
            return InputDataType.STRUCTURED
        elif data == 'UNSTRUCTURED_IMAGE':
            return InputDataType.UNSTRUCTURED_IMAGE
        elif data == 'UNSTRUCTURED_TEXT':
            return InputDataType.UNSTRUCTURED_TEXT
        return None

    def _get_problem_type_object(self, data):
        if data == 'BINARY_CLASSIFICATION':
            return ProblemType.BINARY_CLASSIFICATION
        elif data == 'MULTICLASS_CLASSIFICATION':
            return ProblemType.MULTICLASS_CLASSIFICATION
        elif data == 'REGRESSION':
            return ProblemType.REGRESSION
        return None

    # not actually called, because payload logging and performance monitoring are both already enabled by default
    @retry(tries=5, delay=8, backoff=2)
    def configure_subscription(self):
        '''
        Configure payload logging and performance monitoring
        '''
        logger.log_info('Enabling payload logging ...')
        start = time.time()
        self._subscription.payload_logging.enable()
        elapsed = time.time() - start
        self.timer('subscription.payload_logging.enable', elapsed)
        logger.log_info('Payload logging enabled successfully')

        logger.log_info('Enabling performance monitoring ...')
        start = time.time()
        self._subscription.performance_monitoring.enable()
        elapsed = time.time() - start
        self.timer('subscription.performance_monitoring.enable', elapsed)
        logger.log_info('Performance monitoring enabled successfully')

    def configure_subscription_monitors(self):
        def _get_config_params(param_key_name):
            param_name = param_key_name.split('_')[0]
            params = None
            if param_key_name in self._model.configuration_data:
                params = self._model.configuration_data[param_key_name]
                logger.log_info('Configuring {} ...'.format(param_name))
            else:
                logger.log_info('Configuration for {} not provided for this model - skipping'.format(param_name))
            return params

        self.configure_explainability()
        self.configure_fairness(_get_config_params('fairness_configuration'))
        self.configure_quality(_get_config_params('quality_configuration'))
        self.configure_drift(_get_config_params('drift_configuration'))
        # if self._args.bkpi:
        #     self.configure_bkpi(_get_config_params('businesskpi_configuration'))
        if self._args.mrm:
            self.configure_mrm(_get_config_params('mrm_configuration'))

    @retry(tries=5, delay=8, backoff=2)
    def configure_fairness(self, params):
        if params:
            start = time.time()
            if self._fairness_run_once:  # in case of retry
                self._fairness_run_once = False
            parameters = {
                "features": params["features"],
                "favourable_class": params["favourable_classes"],
                "unfavourable_class": params["unfavourable_classes"],
                "min_records": params["min_records"],
                "training_data_distributions": self._model.training_data_statistics["fairness_configuration"]["parameters"]["training_data_distributions"]
            }
            target = Target(
                target_type=TargetTypes.SUBSCRIPTION,
                target_id=self._subscription_id
            )
            thresholds = []
            for feature in params["features"]:
                thresholds.append(
                    {
                        "metric_id": "fairness_value",
                        "specific_values": [
                            {
                                "applies_to": [
                                    {
                                        "type": "tag",
                                        "value": feature["feature"],
                                        "key": "feature"
                                    }
                                ],
                                "value": int(feature["threshold"] * 100)
                            }
                        ],
                        "type": "lower_limit",
                        "value": int(feature["threshold"] * 100)
                    }
                )
            fairness_monitor_details = self._client.monitor_instances.create(
                data_mart_id=self._credentials['data_mart_id'],
                background_mode=False,
                monitor_definition_id=self._client.monitor_definitions.MONITORS.FAIRNESS.ID,
                target=target,
                parameters=parameters,
                thresholds=thresholds
            ).result
            self._fairness_monitor_instance_id = fairness_monitor_details.metadata.id
            elapsed = time.time() - start
            self.timer("subscription.fairness_monitoring.enable", elapsed)
            logger.log_info('Fairness configured successfully')

    @retry(tries=5, delay=8, backoff=2)
    def configure_quality(self, params):
        if params:
            start = time.time()
            target = Target(
                target_type=TargetTypes.SUBSCRIPTION,
                target_id=self._subscription_id
            )
            parameters = {"min_feedback_data_size": params["min_records"]}
            thresholds = [
                {
                    "metric_id": "area_under_roc",
                    "type": "lower_limit",
                    "value": params["threshold"]
                }
            ]
            quality_monitor_details = self._client.monitor_instances.create(
                data_mart_id=self._credentials["data_mart_id"],
                background_mode=False,
                monitor_definition_id=self._client.monitor_definitions.MONITORS.QUALITY.ID,
                target=target,
                parameters=parameters,
                thresholds=thresholds
            ).result
            self._quality_monitor_instance_id = quality_monitor_details.metadata.id
            elapsed = time.time() - start
            self.timer('subscription.quality_monitoring.enable', elapsed)
            logger.log_info('Quality configured successfully')

    @retry(tries=5, delay=8, backoff=2)
    def configure_explainability(self):
        explain_required_columns_absent = 'class_probability_columns' not in self._model.configuration_data['asset_metadata'] and 'probability_column' not in self._model.configuration_data['asset_metadata']
        is_xgboost_model = 'xgboost' in self._model.name.lower()
        if not is_xgboost_model and explain_required_columns_absent:
            logger.log_info('Explainability not available for this model')
            self._configure_explain = False
            return
        logger.log_info('Configuring explainability ...')
        # params = {}
        # if self._explainability_run_once: # in case of retry
        #     if not self._model.training_data_reference:
        #         if self._model.training_data_statistics:
        #             params['training_data_statistics'] = self._model.training_data_statistics
        #         else:
        #             params['training_data'] = self._model.training_data
        #     self._explainability_run_once = False
        start = time.time()
        target = Target(
            target_type=TargetTypes.SUBSCRIPTION,
            target_id=self._subscription_id
        )
        # print('training_data_statistics = {}'.format(self._model.training_data_statistics))
        parameters = {
            'enabled': True,
            'training_statistics': self._model.training_data_statistics['explainability_configuration']
        }
        explainability_details = self._client.monitor_instances.create(
            data_mart_id=self._credentials['data_mart_id'],
            background_mode=False,
            monitor_definition_id=self._client.monitor_definitions.MONITORS.EXPLAINABILITY.ID,
            target=target,
            parameters=parameters
        ).result
        self._explainability_monitor_id = explainability_details.metadata.id
        elapsed = time.time() - start
        self.timer('subscription.explainability.enable', elapsed)
        logger.log_info('Explainability configured successfully')

    @retry(tries=5, delay=8, backoff=2)
    def configure_drift(self, params):
        if params:
            start = time.time()

            # Configuring Drift
            data_mart_id = self.get_datamart_id()
            subscription_id = self.get_subscription_id()
            target = Target(
                target_type=TargetTypes.SUBSCRIPTION,
                target_id=subscription_id
            )
            
            # Uploading the DDM
            logger.log_info("Uploading the Drift Detection Model.")
            
            # Getting appropriate scikit-learn version trained archive as per environment
            scikit_folder = DRIFT_ARCHIVE_ENV_MAPPING[self._args.environment]

            if self.is_mrm_challenger:
                filename = "drift_archives/{}/{}/{}".format(WML_CHALLENGER_ENVIRONMENT_MAPPING[self._args.environment], scikit_folder, Model.DRIFT_MODEL_FILENAME)
            else:
                filename = "drift_archives/{}_model/{}/{}".format(WML_SPARK_VERSION_SUPPORT_MAPPING[self._args.environment], scikit_folder, Model.DRIFT_MODEL_FILENAME)
            
            model_path = self._model._get_file_path(filename)
            
            upload_response = self._client.monitor_instances.upload_drift_model(model_path=model_path, data_mart_id=data_mart_id, subscription_id=subscription_id, enable_data_drift=True, enable_model_drift=True)
            
            logger.log_info("Drift Detection Model uploaded successfully for drift configuration.")

            parameters = {
                "min_samples": 20,
                "train_drift_model": False,
                "enable_model_drift": True,
                "enable_data_drift": True
            }
                
            drift_monitor_details = self._client.monitor_instances.create(
                data_mart_id=data_mart_id,
                background_mode=False,
                monitor_definition_id=self._client.monitor_definitions.MONITORS.DRIFT.ID,
                target=target,
                parameters=parameters
            ).result
            self._drift_monitor_instance_id = drift_monitor_details.metadata.id
            elapsed = time.time() - start
            self.timer("subscription.drift_monitoring.enable", elapsed)
            logger.log_info("Drift configured successfully")
    
    @classmethod
    def get_fairness_heartbeat(cls, service_url: str) -> dict:
        """
        Returns the response of the fairness V1 heartbeat call.
        :service_url: The Openscale Gateway URL.

        :returns: The fairness V1 heartbeat response.
        """

        url = "{}/v1/fairness_monitoring/heartbeat".format(service_url)

        payload = {}
        headers = {
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers, data=payload)

        if response.ok is False:
            error_msg = "ERROR: Failed to get the fairness heartbeat, url: {}, rc: {}, response: {}".format(url, response.status_code, response.text)
            logger.log_error(error_msg)
            raise Exception(error_msg)

        return response.json()

    @retry(tries=5, delay=8, backoff=2)
    def configure_mrm(self, params):
        # save preprod subscription id so it can be used later by prod subscription mrm configuration
        if self.is_mrm_preprod:
            self.mrm_preprod_subscription_id = self.get_subscription_id()
        start = time.time()
        target = Target(target_type="subscription", target_id=self.get_subscription_id())
        parameters = {}
        response = self._client.monitor_instances.create(monitor_definition_id="mrm", target=target, data_mart_id=self._credentials['data_mart_id'], background_mode=False, parameters=parameters)

        elapsed = time.time() - start
        if self.is_mrm_challenger:
            self.mrm_challenger_instance_id = response.result.metadata.id
        elif self.is_mrm_preprod:
            self.mrm_preprod_instance_id = response.result.metadata.id
        else:
            self.mrm_prod_instance_id = response.result.metadata.id
        self.timer('subscription.mrm.enable', elapsed)

        # for the preprod model, mark it as approved for production
        if self.is_mrm_preprod and self.mrm_preprod_instance_id:
            payload = {'state': 'approved'}
            mrm_url = '{}/openscale/{}/v2/subscriptions/{}/risk_evaluation_status'.format(self._credentials['url'], self._credentials['data_mart_id'], self.get_subscription_id())
            start = time.time()
            response = requests.put(mrm_url, json=payload, headers=self.iam_headers, verify=self._verify)
            elapsed = time.time() - start
            if response.status_code != 200:
                error_msg = 'ERROR: Failed to approve pre-prod model, rc: {} url: {} payload: {} response: {}'.format(response.status_code, mrm_url, payload, response.text)
                logger.log_error(error_msg)
                raise Exception(error_msg)
            self.timer('subscription.mrm approve preprod', elapsed)

        # for the prod model, link it back to the preprod model
        if self.is_mrm_prod and self.mrm_preprod_subscription_id:
            payload = [{ "op": "add", "path": "/pre_production_reference_id", "value": self.mrm_preprod_subscription_id }]
            mrm_url = '{}/openscale/{}/v2/subscriptions/{}'.format(self._credentials['url'], self._credentials['data_mart_id'], self.get_subscription_id())
            start = time.time()
            response = requests.patch(mrm_url, json=payload, headers=self.iam_headers, verify=self._verify)
            elapsed = time.time() - start
            if response.status_code != 200:
                error_msg = 'ERROR: Failed to patch subscription with pre-prod reference, rc: {} url: {} payload: {} response: {}'.format(response.status_code, mrm_url, payload, response.text)
                logger.log_error(error_msg)
                raise Exception(error_msg)
            self.timer('subscription.mrm patch prod', elapsed)

        logger.log_info('MRM configured successfully')

    def generate_sample_metrics(self):
        if self._args.history < 1 or (self._args.mrm and self.is_mrm_challenger or self.is_mrm_preprod):
            return False
        self._reliable_count_datamart_rows('generate sample metrics start')
        return True

    def save_subscription_details(self):
        _subs_details = self._client.subscriptions.get(subscription_id=self._subscription_id).result.entity
        subscription_details_json = json.dumps(_subs_details, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        temp_file = logging_temp_file.name.replace('{}.log'.format(cli_name), '{}-{}.json'.format(cli_name, 'subscription-details'))
        logger.log_info('Saving datamart subscription details to: {}'.format(temp_file))
        with open(temp_file, "w+") as f:
            f.write(subscription_details_json)

    def load_historical_payloads(self):
        self._no_historical_payloads = False
        self._history_load_start_time = datetime.utcnow()
        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_payload_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    self._no_historical_payloads = True # use later to skip generating drift history
                    logger.log_info('No historical payload records provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical payload records to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            self._reliable_post_payloads(records)
            if (day + 1) == self._args.history:
                logger.log_info('Historical payloads loaded successfully')
                self._model.expected_payload_row_count += self._model.historical_payload_row_count

    def load_historical_performance(self):
        target = Target(
            target_type=TargetTypes.SUBSCRIPTION,
            target_id=self.get_subscription_id()
        )
        performance_monitor_instance_details = self._client.monitor_instances.create(
            data_mart_id=self._credentials["data_mart_id"],
            background_mode=False,
            monitor_definition_id=self._client.monitor_definitions.MONITORS.PERFORMANCE.ID,
            target=target
        ).result
        performance_monitor_instance_id = performance_monitor_instance_details.metadata.id
        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_performance_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical performance metrics provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical performance metrics to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            self._client.monitor_instances.measurements.add(
                monitor_instance_id=performance_monitor_instance_id,
                monitor_measurement_request=records
            ).result
            if (day + 1) == self._args.history:
                logger.log_info('Historical performance metrics loaded successfully')
    
    def _get_data_set_id(self, target_id: str, target_type: str, data_set_type: str):
        """
        Returns the data set ID with the given parameters.
        """
        data_set_id = None
        # Getting all data sets with given target
        all_data_sets = self._client.data_sets.list(target_target_id=target_id, target_target_type=target_type).result.data_sets

        for data_set in all_data_sets:
            if data_set.entity.type == data_set_type:
                data_set_id = data_set.metadata.id
                break
        
        return data_set_id

    def load_historical_explanations(self):
        records = self._model.get_explain_history()
        if len(records) == 0:
            logger.log_info('No historical explanations provided - skipping')
        else:
            logger.log_info('Loading historical explanations to {} ...'.format(self._args.service_name))

            # Performing a LIST explanations so that the explain data set ID is created (#19994)
            subscription_id = self.get_subscription_id()
            self._client.monitor_instances.explanation.list(subscription_id=subscription_id)

            # Getting the explain data set ID
            self.explain_data_set_id = self._get_data_set_id(self._credentials["data_mart_id"], "data_mart", "explanations")
            reqs = []
            for record in records:
                value = record["entity"]["values"]
                value["subscription_id"] = subscription_id
                value["binding_id"] = self.get_binding_id()
                value["deployment_id"] = self.get_deployment_id()
                value["asset_name"] = self._asset_details_dict["model_name"]
                explanation = json.loads(base64.b64decode(value.get("explanation")).decode("utf-8"))
                explanation["entity"]["asset"]["id"] = self.get_asset_id()
                explanation["entity"]["asset"]["deployment"]["id"] = self.get_deployment_id()
                explanation["entity"]["asset"]["name"] = self._asset_details_dict["model_name"]
                value["explanation"] = self._encode(json.dumps(explanation))
                reqs.append(value)
            
            # Storing the records
            stored_rec_info = self._client.data_sets.store_records(data_set_id=self.explain_data_set_id, request_body=reqs, background_mode=False)
            if stored_rec_info.result.state == "active":
                logger.log_info("History explanations loaded successully!")
        self._reliable_count_datamart_rows('generate sample metrics completed')
    
    def _encode(self, data):
        return str(base64.b64encode(data.encode("utf-8")))[2:-1]

    def load_historical_fairness(self):

        # Adding the fairness metrics
        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_fairness_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical fairness metrics provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical fairness metrics to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            
            self._reliable_store_fairness_monitor_metrics(records)
            if (day + 1) == self._args.history:
                logger.log_info('Historical fairness metrics loaded successfully')
        
        # Adding the debiased fairness metrics
        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_debias_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical debiased fairness metrics provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical debiased fairness metrics to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            self._reliable_store_fairness_monitor_metrics(records)
            if (day + 1) == self._args.history:
                logger.log_info('Historical debiased fairness metrics loaded successfully')

        # Adding the manual labelling records and `is_individually_biased` annotation
        records_client = Records(watson_open_scale=self._client)
        self.manual_labelling_data_set_id = self._get_data_set_id(self.get_subscription_id(), "subscription", "manual_labeling")
        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records, original_records = self._model.get_manual_labeling_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical manual labeling data provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical manual labeling data to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            # Adding records in ML table
            self._client.data_sets.store_records(data_set_id=self.manual_labelling_data_set_id, request_body=records, background_mode=True)

            # Adding `is_individually_biased` annotation
            logger.log_info("   Adding 'is_individually_biased' annotation for day {} records.".format(day + 1))
            patch_documents = []
            for ib_record in original_records:
                patch_document = PatchDocument(
                    op="replace",
                    path="/records/{}/annotations/{}".format(ib_record["scoring_id"], "is_individually_biased"),
                    value=True
                )
                patch_documents.append(patch_document)
            if len(patch_documents) > 0:
                response = records_client.patch(data_set_id=self._payload_dataset_id, patch_document=patch_documents)
            if (day + 1) == self._args.history:
                logger.log_info('Historical manual labeling data loaded successfully')
    
    @retry(tries=5, delay=4, backoff=2)
    def _reliable_store_fairness_monitor_metrics(self, records):
        '''
        Retry the loading metrics so that if a specific day fails, just retry that day, rather than retry the whole sequence
        '''
        if not records:
            logger.log_debug('No fairness_monitor history provided to load - skipping')
            return
        start = time.time()
        measurements_client = Measurements(watson_open_scale=self._client)
        measurements_client.add(monitor_instance_id=self._fairness_monitor_instance_id, monitor_measurement_request=records)
        elapsed = time.time() - start
        self.timer('post data_mart fairness_monitor metrics', elapsed)

    def load_historical_quality(self):
        if not self._model.feedback_history:
            logger.log_info('No historical feedback data provided for this model - skipping')
        else:
            logger.log_info('Loading historical feedback data ...')
            self._reliable_upload_feedback(self._model.feedback_history)
            logger.log_info('Historical feedback data loaded successfully')

        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_quality_monitor_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical quality monitor metrics provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical quality monitor metrics to {} ...'.format(self._args.service_name))
            logger.log_info(' - Loading day {}'.format(day + 1))
            self._reliable_store_quality_monitor_metrics(records)
            if (day + 1) == self._args.history:
                logger.log_info('Historical quality monitor metrics loaded successfully')

    def confirm_payload_logging(self):
        self.wait_for_payload_logging(initial_pause=8+int(self._model.historical_payload_row_count/250), context='payload history')
        self._reliable_count_datamart_rows('confirm payload logging')

    def load_historical_debiased_payloads(self):
        for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
            records = self._model.get_debiased_payload_history(day)
            if day == self._args.history_first_day:
                if len(records) == 0:
                    logger.log_info('No historical debiased payloads provided - skipping')
                    break
                else:
                    logger.log_info('Loading historical debiased payloads to {} ...'.format(self._args.service_name))
            logger.log_info(" - Loading day {}".format(day + 1))
            logger.log_info("   Adding 'is_group_biased_record' annotation for day {} records.".format(day + 1))
            self._reliable_post_debiased_payloads(records)
            if (day + 1) == self._args.history:
                logger.log_info('Historical debiased payloads loaded successfully')

    def load_historical_drift(self):
        if 'drift_configuration' in self._model.configuration_data and self._args.history > 0:
            if self._args.generate_drift_history:
                if self._no_historical_payloads:
                    logger.log_info('No historical payloads provided - skipping drift history generation')
                else:
                    logger.log_info('Generating {} days of historical drift metrics to {} ...'.format(self._args.history, self._args.service_name))
                    end_time = self._history_load_start_time - timedelta(hours=self._args.history_first_day*24)
                    start_time = end_time - timedelta(hours=24*self._args.history)
                    windows = 8 * self._args.history # 3 hour drift windows, so 8 per day
                    self._reliable_generate_drift_metrics(start_time, end_time, windows)
                    logger.log_info('Historical drift metrics generated successfully')
            else:
                for day in range(self._args.history_first_day, self._args.history_first_day + self._args.history):
                    records = self._model.get_drift_metrics_history(day)
                    if day == self._args.history_first_day:
                        if len(records) == 0:
                            logger.log_info('No historical drift metrics provided - skipping')
                            break
                        else:
                            logger.log_info('Loading historical drift metrics to {} ...'.format(self._args.service_name))
                    logger.log_info(' - Loading day {}'.format(day + 1))
                    self._post_drift_metrics(records, day)
                    if (day + 1) == self._args.history:
                        logger.log_info('Historical drift metrics loaded successfully')


    @retry(tries=5, delay=8, backoff=2)
    def _reliable_upload_feedback(self, feedback_data):
        start = time.time()
        if self._model.is_unstructured_text:
            self._subscription.feedback_logging.store(feedback_data)
        else:
            self._feedback_dataset_id = self._client.data_sets.list(
                type=DataSetTypes.FEEDBACK,
                target_target_id=self._subscription_id,
                target_target_type=TargetTypes.SUBSCRIPTION
            ).result.data_sets[0].metadata.id
            self._client.data_sets.show()

            response = self._client.data_sets.store_records(
                self._feedback_dataset_id,
                request_body=feedback_data,
                background_mode=False
            ).result.to_dict()
        elapsed = time.time() - start
        self.timer('subscription.feedback_logging.store', elapsed)

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_single_score(self, engine_client, deployment_url, score_input, score_num, values_per_score, totalelapsed, firststart, lastend, tokenizer=None):
        record = None
        start = time.time()
        if self._args.v4:
            deployment_id = self._asset_details_dict['source_entry_metadata_guid']
            if 'fields' in score_input:
                record = engine_client.score(deployment_id, values=score_input['values'], fields=score_input['fields'])
            elif 'fields' not in score_input:
                record = engine_client.score(deployment_id, values=score_input['values'])
        else:
            record = engine_client.deployments.score(deployment_url, score_input)
        end = time.time()
        elapsed = end - start
        totalelapsed += elapsed
        lastend = end
        duration = lastend - firststart
        logger.log_timer('WML deployment.score {} values(s) in {:.3f} seconds, total requests: {}, duration: {:.3f} seconds, elapsed: {:.3f} seconds'.format(values_per_score, elapsed, score_num+1, duration, totalelapsed))
        self.timer('WML deployment.score {} value(s)'.format(values_per_score), elapsed)
        if self._args.generate_payload_history:
            logger.log_info('{},'.format ({"scoring_id": uuid.uuid4().hex, "response_time": int(1000*elapsed)}))
        if self._args.v4:
            record = record['predictions'][0]
        return totalelapsed, duration, lastend, record

    def generate_sample_scoring(self, engine_client, numscores, values_per_score, to_init_payload_logging=False):
        # no feedback or sample scoring for MRM pre-production models
        if not to_init_payload_logging and self._args.mrm and not self.is_mrm_prod:
            return

        # first, generate sample feedback if requested, then move on to scoring
        if not to_init_payload_logging and not self._args.no_new_feedback:
            if not self._model.feedback_data:
                logger.log_info('New feedback data not provided for this model - skipping')
            else:
                logger.log_info('Adding new feedback data ...')
                self._reliable_upload_feedback(self._model.feedback_data)
                logger.log_info('New feedback data added successfully')

        if numscores < 1:
            return
        if to_init_payload_logging:
            logger.log_info('Initialize payload logging by sending one sample scoring request')

        message = 'Generating {} scoring request(s) ...'.format(numscores)
        if values_per_score > 1:
            message = message.replace('...', 'with {} values per request ...'.format(values_per_score))
        logger.log_info(message)
        records_list = []
        subscription_details = self._client.subscriptions.get(subscription_id=self._subscription_id)
        if self._args.ml_engine_type is MLEngineType.WML:
            if self._args.v4:
                native_client = engine_client.get_native_client()
                deployment_details = native_client.deployments.get_details(self._asset_details_dict['source_entry_metadata_guid'])
                deployment_url = native_client.deployments.get_scoring_href(deployment_details)
            else:
                engine_client = self._client.data_mart.bindings.get_native_engine_client(binding_uid=self.get_binding_id())
                deployment_details = engine_client.deployments.get_details(self._asset_details_dict['source_entry_metadata_guid'])
                deployment_url = engine_client.deployments.get_scoring_url(deployment_details)

            is_local_icp_wml = False
            is_remote_icp_wml = False
            is_cloud_wml = False
            if self._args.is_icp and self._args.v4:
                api_env = ApiEnvironment()
                if self._args.wml:# or self._args.wml_json:
                    if 'apikey' in self._ml_engine_credentials:
                        is_cloud_wml = True
                    else:
                        is_remote_icp_wml = True
                else:
                    is_local_icp_wml = True
                if api_env.is_running_on_icp:
                    if is_local_icp_wml:
                        elements = get_url_elements(api_env.icp_gateway_url)
                        deployment_url = update_url(deployment_url, new_hostname=elements.hostname, new_scheme=elements.scheme)
                        deployment_url = remove_port_from_url(deployment_url)
                else:
                    icp4d_port = get_url_elements(self._credentials['url']).port
                    port = get_url_elements(deployment_url).port
                    if not port or port != icp4d_port:
                        deployment_url = update_url(deployment_url, new_hostname=None, new_port=icp4d_port, new_scheme=None)

            pause = self._args.pause_between_scores
            if pause > 0.0:
                logger.log_info('{:.3f} second pause between each scoring request'.format(pause))
            totalelapsed = 0.0
            firststart = time.time()
            lastend = firststart
            self._model.expected_payload_row_count += numscores * values_per_score
            for score_num in range(numscores):
                if pause > 0.0 and score_num > 0:
                    logger.log_info("Pausing for {} second(s) in-between scores.".format(pause))
                    time.sleep(pause)
                fields, values = self._model.get_score_input(values_per_score)
                tokenizer = None
                if self._model.is_unstructured_image:
                    score_input = values
                else:
                    if self._model.is_unstructured_text:
                        tokenizer = self._model.tokenizer
                    score_input = {'fields': fields, 'values': values}
                logger.log_info("Scoring {} record(s).".format(values_per_score))
                (totalelapsed, duration, lastend, record) = self._reliable_single_score(engine_client, deployment_url, score_input, score_num, values_per_score, totalelapsed, firststart, lastend, tokenizer=tokenizer)
                # manual payload logging if remote-cloud-wml or remote-icp-wml is used on icp
                if is_cloud_wml or is_remote_icp_wml:
                    logger.log_info("Performing logging of Payload Records ...")
                    pl_record = PayloadRecord(request=score_input, response=record, response_time=int(duration))
                    records_list.append(pl_record)
            logger.log_timer('Total score requests: {}, total scores: {}, duration: {:.3f} seconds'.format(numscores, numscores*values_per_score, duration))
            logger.log_timer('Throughput: {:.3f} score requests per second, {:.3f} scores per second, average score request time: {:.3f} seconds'.format(numscores/duration, numscores*values_per_score/duration, totalelapsed/numscores))

        elif self._args.ml_engine_type is MLEngineType.AZUREMLSTUDIO:
            engine_client.setup_scoring_metadata(subscription_details)
            self._model.expected_payload_row_count += numscores
            for _ in range(numscores):
                fields, values = self._model.get_score_input(1)
                values = values[0]
                value_dict = {}
                for (index, field) in enumerate(fields):
                    value_dict[field] = values[index]
                start = time.time()
                record = engine_client.score({'Inputs': {'input1': [value_dict]}, 'GlobalParameters': {}})
                elapsed = time.time() - start
                self.timer('AzureML score', elapsed)
                records_list.append(record)

        elif self._args.ml_engine_type is MLEngineType.AZUREMLSERVICE:
            engine_client.setup_scoring_metadata(subscription_details)
            self._model.expected_payload_row_count += numscores
            for _ in range(numscores):
                fields, values = self._model.get_score_input(1)
                values = values[0]
                value_dict = {}
                for (index, field) in enumerate(fields):
                    value_dict[field] = values[index]
                start = time.time()
                record = engine_client.score({"input": [value_dict]})
                elapsed = time.time() - start
                self.timer('AzureML score', elapsed)
                records_list.append(record)

        elif self._args.ml_engine_type is MLEngineType.SPSS:
            engine_client.setup_scoring_metadata(subscription_details)
            subscription_details = self._subscription.get_details()
            model_name_id = subscription_details['entity']['asset']['name']
            input_table_id = subscription_details['entity']['asset_properties']['input_data_schema']['id']
            self._model.expected_payload_row_count += numscores
            for _ in range(numscores):
                spss_data = {'requestInputTable':[{'id': input_table_id, 'requestInputRow':[{'input':[]}]}],'id':model_name_id}
                fields, values = self._model.get_score_input(1)
                values = values[0]
                value_dict = {}
                for (index, field) in enumerate(fields):
                    entry_dict = {'name':str(field),'value':str(values[index])}
                    spss_data['requestInputTable'][0]['requestInputRow'][0]['input'].append(entry_dict)
                start = time.time()
                record = engine_client.score(spss_data)
                elapsed = time.time() - start
                self.timer('SPSS score', elapsed)
                records_list.append(record)
        elif self._args.ml_engine_type is MLEngineType.CUSTOM:
            engine_client.setup_scoring_metadata(subscription_details)
            self._model.expected_payload_row_count += numscores
            for _ in range(numscores):
                fields, values = self._model.get_score_input(1)
                score_input = {'fields': fields, 'values': values }
                start = time.time()
                record = engine_client.score(score_input)
                elapsed = time.time() - start
                self.timer('Custom score', elapsed)
                records_list.append(record)
        elif self._args.ml_engine_type is MLEngineType.SAGEMAKER:
            records_list = []
            engine_client.setup_scoring_metadata(subscription_details)
            self._model.expected_payload_row_count += numscores
            for _ in range(numscores):
                fields, values = self._model.get_score_input(1)
                values = values[0]
                start = time.time()
                record = engine_client.score(fields, values)
                elapsed = time.time() - start
                self.timer('Sagemaker score', elapsed)
                records_list.append(record)
        if records_list:
            start = time.time()
            self._client.data_sets.store_records(data_set_id=self._payload_dataset_id, request_body=records_list)
            elapsed = time.time() - start
            self.timer('subscription.payload_logging.store', elapsed)

        logger.log_info('Scoring request(s) generated successfully')
        if to_init_payload_logging:
            context = 'init payload logging'
        else:
            context = 'live scoring'
        self.wait_for_payload_logging(context=context, to_init_payload_logging=to_init_payload_logging)
        self._reliable_count_datamart_rows('generated sample scores and confirmed payload logging')

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_count_payload_rows(self, context=None):
        start = time.time()
        actual_payload_rows = self._client.data_sets.get_records_count(data_set_id = self._payload_dataset_id)
        elapsed = time.time() - start
        if context:
            context = ', {}'.format(context)
        else:
            context = ''
        logger.log_timer('subscription count payload rows in {:.3f} seconds, rows={}, expected={}{}'.format(elapsed, actual_payload_rows, self._model.expected_payload_row_count, context))
        return actual_payload_rows

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_count_datamart_rows(self, context=None):
        if self._database is None: # internal db
            logger.log_debug('DEBUG: cannot count datamart rows for internal db')
            if self._args.database_counts:
                logger.log_info('Cannot count datamart rows for internal db - skipping')
            return
        start = time.time()
        datamart_rows = self._database.count_datamart_rows(self._datamart_name, context=context)
        elapsed = time.time() - start
        if context:
            context = ', {}'.format(context)
        else:
            context = ''
        logger.log_timer('count datamart rows in {:.3f} seconds{}'.format(elapsed, context))
        logger.log_debug(str(datamart_rows))
        if self._args.database_counts:
            try:
                from tabulate import tabulate
            except:
                from ibm_ai_openscale_cli.utility_classes.utils import pip_install
                pip_install('tabulate')
            headers = ['table', 'row count']
            logger.log_info('\n{}\n'.format(tabulate(datamart_rows, headers=headers, tablefmt='orgtbl')))

    def wait_for_payload_logging(self, initial_pause=8, context=None, to_init_payload_logging=False):
        logger.log_info('Confirming that all payloads have been stored to the datamart database ...')
        logger.log_info('(start with {} second wait to give payload logging time to complete)'.format(initial_pause))
        time.sleep(initial_pause)
        for pause in [16, 32, 64, 64]:
            actual_payload_rows = self._reliable_count_payload_rows(context)
            if self._model.expected_payload_row_count == actual_payload_rows:
                logger.log_info('Confirmed that the expected {} rows are in the payload table for this model'.format(actual_payload_rows))
                return
            elif self._model.expected_payload_row_count < actual_payload_rows:
                logger.log_warning('Expecting {} rows in the payload table for this model, but {} rows already in table'.format(self._model.expected_payload_row_count, actual_payload_rows))
                break
            else:
                delaymsg = ', pause {} seconds and check again ...'.format(pause)
                logger.log_error('Expecting {} rows in the payload table for this model, {} rows currently in table{}'.format(self._model.expected_payload_row_count, actual_payload_rows, delaymsg))
                time.sleep(pause)
        if to_init_payload_logging and actual_payload_rows < 1:
            error_msg = 'OpenScale did not receive the scoring payload, so setup cannot continue. Please try again.'
            logger.log_error(error_msg)
            raise Exception(error_msg)
        message = 'WARNING: unable to confirm that the expected number of payloads are stored into the datamart database'
        logger.log_warning(message)
        self.metric_check_errors.append([self._model.name, 'payload-logging', 'failed (count-mismatch)'])


    def trigger_monitors(self):
        background_mode = self._args.async_checks
        if self._args.no_checks:
            logger.log_info('Skip monitor checks')
            return
        
        if self._args.mrm:
            self.trigger_mrm_check(background_mode)
            self._reliable_count_datamart_rows('mrm monitor triggered')
        else:
            self._reliable_count_datamart_rows('correlation monitor triggered')
            self._reliable_trigger_fairness_check(background_mode)
            self._reliable_count_datamart_rows('fairness monitor triggered')
            self._reliable_trigger_quality_check(background_mode)
            self._reliable_count_datamart_rows('quality monitor triggered')
            self._reliable_trigger_drift_check(background_mode)
            self._reliable_count_datamart_rows('drift monitor triggered')
        
        return

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_trigger_fairness_check(self, background_mode):
        if 'fairness_configuration' not in self._model.configuration_data:
            logger.log_info('Skip fairness check since fairness not configured for model')
        else:
            try:
                deployment_uid = self._asset_details_dict['source_entry_metadata_guid']
                logger.log_info('Triggering immediate fairness check ...')
                start = time.time()
                result = self._client.monitor_instances.run(monitor_instance_id=self._fairness_monitor_instance_id, background_mode=background_mode).result
                elapsed = time.time() - start
                self.timer('subscription.fairness_monitoring.run', elapsed)
                logger.log_info('Fairness check triggered')
                if not background_mode:
                    if not result or (isinstance(result, str) and 'error' in result.lower()) or result.entity.status.state.lower() != 'finished':
                        self.metric_check_errors.append([self._model.name, 'fairness-check', 'failed'])
            except Exception as e:
                message = 'WARNING: Problems occurred while running fairness check: {}'.format(str(e))
                logger.log_warning(message)
                self.metric_check_errors.append([self._model.name, 'fairness-check', 'failed'])

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_trigger_quality_check(self, background_mode):
        if 'quality_configuration' not in self._model.configuration_data:
            logger.log_info('Skip quality check since quality monitoring not configured for model')
        elif (not self._model.feedback_data or self._args.no_new_feedback) and (not self._model.feedback_history or self._args.history < 1):
            logger.log_info('Skip quality check for model since there is no feedback data yet')
        else:
            try:
                logger.log_info('Triggering immediate quality check ...')
                start = time.time()
                result = self._client.monitor_instances.run(monitor_instance_id=self._quality_monitor_instance_id, background_mode=background_mode).result
                elapsed = time.time() - start
                self.timer('subscription.quality_monitoring.run', elapsed)
                logger.log_info('Quality check triggered')
                if not background_mode:
                    if not result or (isinstance(result, str) and 'error' in result.lower()) or result.entity.status.state.lower() != 'finished':
                        self.metric_check_errors.append([self._model.name, 'quality-check', 'failed'])
            except Exception as e:
                message = 'WARNING: Problems occurred while running quality check: {}'.format(str(e))
                logger.log_warning(message)
                self.metric_check_errors.append([self._model.name, 'quality-check', 'failed'])

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_trigger_drift_check(self, background_mode):
        if 'drift_configuration' not in self._model.configuration_data:
            logger.log_info('Skip drift check since drift monitoring not configured for model')
        else:
            try:
                logger.log_info('Triggering immediate drift check ...')
                start = time.time()
                result = self._client.monitor_instances.run(monitor_instance_id=self._drift_monitor_instance_id, background_mode=background_mode).result
                elapsed = time.time() - start
                self.timer('subscription.drift_monitoring.run', elapsed)
                logger.log_info('Drift check triggered')
                if not result or (isinstance(result, str) and 'error' in result.lower()):
                    self.metric_check_errors.append([self._model.name, 'drift-check', 'failed'])
            except Exception as e:
                message = 'WARNING: Problems occurred while running drift check: {}'.format(str(e))
                logger.log_warning(message)
                self.metric_check_errors.append([self._model.name, 'drift-check', 'failed'])

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_trigger_mrm_prod_check(self, mrm_instance_id, background_mode):
        mrm_url = '{}/openscale/{}/v2/monitor_instances/{}/runs'.format(self._credentials['url'], self._credentials['data_mart_id'], mrm_instance_id)
        payload = {
            "parameters": {
                "publish_fact": "true",
                "on_demand_trigger": True
            },
            "triggered_by": "user"
        }

        # trigger the MRM check
        start = time.time()
        response = requests.post(url=mrm_url, json=payload, headers=self.iam_headers, verify=self._verify)
        elapsed = time.time() - start
        self.timer('trigger mrm prod check', elapsed)

        # check to see if the call was successful
        if response.status_code != 201 and response.status_code != 202:
            error_msg = 'ERROR: Failed to trigger MRM check, url: {}, rc: {}, response: {}'.format(mrm_url, response.status_code, response.text)
            logger.log_error(error_msg)
            raise Exception(error_msg)
        mrm_run_id = None
        json_data = response.json()
        if "metadata" in json_data and "id" in json_data["metadata"]:
            mrm_run_id = json_data["metadata"]["id"]
        else:
            error_msg = 'ERROR: Failed to trigger MRM check, url: {}, rc: {}, response: {}'.format(mrm_url, response.status_code, response.text)
            logger.log_error(error_msg)
            raise Exception(error_msg)
        return mrm_run_id

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_trigger_mrm_preprod_check(self, mrm_instance_id, background_mode):
        if self.is_mrm_challenger:
            filename = 'test_data_challenger.csv'
        else:
            filename = 'test_data_preprod.csv'
        mrm_url = '{}/openscale/{}/v2/monitoring_services/mrm/monitor_instances/{}/risk_evaluations?test_data_set_name={}'.format(self._credentials['url'], self._credentials['data_mart_id'], mrm_instance_id, filename)
        payload = self._model.mrm_evaluation_data

        # trigger the MRM check
        iam_headers = { 'Authorization': self.iam_headers['Authorization'], 'Content-Type': 'text/csv'} # binary-coded csv payload
        start = time.time()
        response = requests.post(url=mrm_url, data=payload, headers=iam_headers, verify=self._verify)
        elapsed = time.time() - start
        self.timer('trigger mrm preprod check', elapsed)

        # check to see if the call was successful
        if response.status_code != 201 and response.status_code != 202:
            error_msg = 'ERROR: Failed to trigger MRM check, url: {}, rc: {}, response: {}'.format(mrm_url, response.status_code, response.text)
            logger.log_error(error_msg)
            raise Exception(error_msg)

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_get_mrm_check_status(self, mrm_instance_id, mrm_run_id=None):
        # different URLs to check MRM run status between prod and pre-prod (PreProd or Challenger)
        if self.is_mrm_prod:
            results_url = '{}/openscale/{}/v2/monitor_instances/{}/runs/{}'.format(self._credentials['url'], self._credentials['data_mart_id'], mrm_instance_id, mrm_run_id)
        else:
            results_url = '{}/openscale/{}/v2/monitoring_services/mrm/monitor_instances/{}/risk_evaluations'.format(self._credentials['url'], self._credentials['data_mart_id'], mrm_instance_id)
        start = time.time()
        response = requests.get(url=results_url, headers=self.iam_headers, verify=self._verify)
        elapsed = time.time() - start
        if response.status_code != 200:
            error_msg = 'ERROR: Failed to get MRM check status, rc: {} {}'.format(response.status_code, response.text)
            raise Exception(error_msg)
        state = response.json()['entity']['status']['state']
        logger.log_debug('MRM check status: {}'.format(state))
        if state == 'error':
            error_msg = 'ERROR: MRM check failed: {}'.format(response.text)
            raise Exception(error_msg)
        self.timer('get mrm monitoring.run', elapsed)
        return response

    def trigger_mrm_check(self, background_mode):
        if 'mrm_configuration' not in self._model.configuration_data:
            logger.log_info('Skip mrm check since MRM not configured for model')
            return

        logger.log_info('Triggering immediate mrm check ...')
        if self.is_mrm_prod:
            mrm_instance_id = self.mrm_prod_instance_id
            mrm_run_id = self._reliable_trigger_mrm_prod_check(mrm_instance_id, background_mode)
        else:
            if self.is_mrm_challenger:
                mrm_instance_id = self.mrm_challenger_instance_id
            elif self.is_mrm_preprod:
                mrm_instance_id = self.mrm_preprod_instance_id
            self._reliable_trigger_mrm_preprod_check(mrm_instance_id, background_mode)
            mrm_run_id = None

        if background_mode:
            logger.log_info('MRM check triggered')
            return
        logger.log_info('MRM check running ...')

        try:
            check_completed = False
            for i in range(18):
                response = self._reliable_get_mrm_check_status(mrm_instance_id, mrm_run_id)
                state = response.json()['entity']['status']['state'].lower()
                if state != 'running' and state != 'upload_in_progress':
                    check_completed = True
                    break
                logger.log_info('MRM check still running; wait 10 seconds and check again')
                time.sleep(10)
            if check_completed:
                logger.log_info('MRM check completed')
            else:
                logger.log_info('MRM check did not complete in 3 minutes, continuing')
        except Exception as e:
            message = 'WARNING: Problems occurred while running MRM check: {}'.format(str(e))
            logger.log_warning(message)
            self.metric_check_errors.append([self._model.name, 'mrm-check', 'failed'])

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_post_payloads(self, records):
        '''
        Retry the loading payloads so that if a specific day fails, just retry that day, rather than retry the whole sequence
        '''
        if not records:
            logger.log_debug('No payload history provided to load - skipping')
            return
        start = time.time()
        self._client.data_sets.store_records(data_set_id=self._payload_dataset_id, request_body=records)
        elapsed = time.time() - start
        self.timer('subscription.payload_logging.store', elapsed)

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_post_debiased_payloads(self, records):
        """
        Retry the loading so that if a specific day fails, just retry that day, rather than retry the whole sequence
        """
        if not records:
            logger.log_debug('No debiased payloads history provided to load - skipping')
            return
        
        records_client = Records(watson_open_scale=self._client)
        
        # Building the patch JSON
        patch_documents = []
        for record in records:
            scoring_id = record["scoring_id"]
            patch_document_pred = PatchDocument(
                op="replace",
                path="/records/{0}/values/debiased_prediction".format(scoring_id),
                value=record["debiased_prediction"]
            )
            patch_document_prob = PatchDocument(
                op="replace",
                path="/records/{0}/values/debiased_probability".format(scoring_id),
                value=record["debiased_probability"]
            )
            patch_documents.append(patch_document_pred)
            patch_documents.append(patch_document_prob)

            # Checking for `is_group_biased_record` annotation
            if record["is_group_biased_record"]:
                patch_document = PatchDocument(
                    op="replace",
                    path="/records/{}/annotations/{}".format(scoring_id, "is_group_biased_record"),
                    value=True
                )
                patch_documents.append(patch_document)
        start = time.time()
        response = records_client.patch(data_set_id=self._payload_dataset_id, patch_document=patch_documents)

        elapsed = time.time() - start
        self.timer('post data_mart debiased payloads history', elapsed)

        if response.status_code < 200 or response.status_code > 299:
            logger.log_warning('WARNING: while posting debiased payloads history: {}'.format(str(response.result.to_dict())))

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_store_quality_monitor_metrics(self, records):
        '''
        Retry the loading metrics so that if a specific day fails, just retry that day, rather than retry the whole sequence
        '''
        if not records:
            logger.log_debug('No quality_monitor history provided to load - skipping')
            return
        start = time.time()
        measurements_client = Measurements(watson_open_scale=self._client)
        measurements_client.add(monitor_instance_id=self._quality_monitor_instance_id, monitor_measurement_request=records)
        elapsed = time.time() - start
        self.timer('post data_mart quality_monitor metrics', elapsed)

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_generate_drift_metrics(self, start_time, end_time, windows=8): # eight 3-hour drift windows in 24 hours
        date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        start_time_param = start_time.strftime(date_format)
        end_time_param = end_time.strftime(date_format)

        drift_tasks_url = '{}/v1/data_marts/{}/service_bindings/{}/subscriptions/{}/drift_tasks'.format(self._credentials['url'], self._credentials['data_mart_id'], self.get_binding_id(), self.get_subscription_id())
        drift_tasks_url += '?start_time={}&end_time={}&compute_windows={}'.format(start_time_param, end_time_param, windows)
        # &execute_mode=synch

        start = time.time()
        requests.post(drift_tasks_url, json={}, headers=self.iam_headers, verify=self._verify)
        elapsed = time.time() - start
        self.timer('generate drift metrics', elapsed)

    def _post_drift_metrics(self, records, day):
        drift_measurement = records[0]['drift_measurement']
        drift_annotations = records[0]['drift_annotations']
        for i in range(0,len(drift_measurement)):
            window_start = self._model._get_score_time(day, hour=(i+1)*3).strftime('%Y-%m-%dT%H:%M:%SZ')  # first_payload_record_timestamp_in_window (oldest)
            window_end = self._model._get_score_time(day, hour=i*3).strftime('%Y-%m-%dT%H:%M:%SZ') # last_payload_record_timestamp_in_window (most recent)
            drift_measurement[i][0]['timestamp'] = window_end
            drift_measurement[i][0]['binding_id'] = self.get_binding_id()
            drift_measurement[i][0]['asset_id'] = self.get_asset_id()
            drift_measurement[i][0]['subscription_id'] = self.get_subscription_id()
            drift_measurement[i][0]['deployment_id'] = self.get_deployment_id()
            drift_measurement[i][0]['process'] = 'Drift run for subscription_{}'.format(self.get_subscription_id())
            drift_measurement[i][0]['sources'][0]['data']['start'] = window_start
            drift_measurement[i][0]['sources'][0]['data']['end'] = window_end
        for i in range(len(drift_measurement)):
            # Adding the Drift measurements
            post_measurement_response = self._client.monitor_instances.measurements.add(
                    monitor_instance_id=self._drift_monitor_instance_id,
                    monitor_measurement_request=drift_measurement[i]
                )
            measurement_id = post_measurement_response.result[0]["measurement_id"]
            
            # Adding drift annotations
            records_client = Records(watson_open_scale=self._client)

            # Building the patch JSON
            patch_documents = []
            related_annotations = drift_annotations[i]
            for annotation_payload in related_annotations:
                patch_document = PatchDocument(
                    op=annotation_payload["op"],
                    path=annotation_payload["path"].replace("<measurement_id>", measurement_id),
                    value=annotation_payload["value"]
                )
                patch_documents.append(patch_document)
            start = time.time()
            response = records_client.patch(data_set_id=self._payload_dataset_id, patch_document=patch_documents)

    def get_asset_details(self, name):
        logger.log_info('Retrieving assets ...')
        asset_details = self._client.data_mart.bindings.get_asset_details()
        asset_details_dict = {}
        for detail in asset_details:
            if name == detail['source_entry']['entity']['name']:
                if self._args.ml_engine_type is MLEngineType.SPSS:
                    asset_details_dict['id'] = detail['name']
                asset_details_dict['binding_uid'] = detail['binding_uid']
                asset_details_dict['source_uid'] = detail['source_uid']
                if self._args.ml_engine_type is not MLEngineType.WML: # For WML, the scoring URL is not in the asset
                    asset_details_dict['scoring_url'] = detail['source_entry']['entity']['scoring_endpoint']['url']
                asset_details_dict['source_entry_metadata_guid'] = detail['source_entry']['metadata']['guid']
                break
        if not 'source_uid' in asset_details_dict:
            error_msg = 'ERROR: Could not find a deployment with the name: {}'.format(name)
            logger.log_error(error_msg)
            raise Exception(error_msg)
        return asset_details_dict

    @retry(tries=5, delay=1, backoff=2)
    def _get_explanation_status(self, scoring_id, background_mode):
        cem = not self._args.explain_no_cem
        logger.log_info("Starting explain request for scoring id: {}".format(scoring_id))
        start = time.time()
        explain = self._client.monitor_instances.get_explanation_tasks(explanation_task_id=scoring_id).result.to_dict()
        status = explain['entity']['status']['state']
        if not background_mode:
            MAX_TIME = 120
            sleep_time = 15
            total_time = 0
            while status == 'in_progress':
                logger.log_info("Waiting for explanation generation to finish, current status: {}, re-check in {} seconds ...".format(status, sleep_time))
                time.sleep(sleep_time)
                total_time += sleep_time
                if total_time > MAX_TIME:
                    logger.log_warning("WARNING: Explanation generation did not finish in {}s, will continue in the background ...".format(MAX_TIME))
                    break
                explain = self._client.monitor_instances.get_explanation_tasks(explanation_task_id=scoring_id).result.to_dict()
                status = explain['entity']['status']['state']

        logger.log_info("Explanation generation ended with state {}.".format(status))
        end = time.time()
        return (start, end, explain)

    def _get_available_scores(self, max_explain_candidates):
        try:
            start = time.time()
            payload_table = self._client.data_sets.get_list_of_records(
                data_set_id=self._payload_dataset_id,
                limit=max_explain_candidates,
                offset=0
            ).result
            end = time.time()
            num_records = len(payload_table["records"])
            scoring_ids = [payload_table["records"][i]["entity"]["values"]["scoring_id"] for i in range(min(max_explain_candidates, num_records))]
            random.shuffle(scoring_ids)
            return start, end, scoring_ids
        except Exception as e:
            logger.log_warning('WARNING: Problems occurred while getting scoring ids for explanation: {}'.format(str(e)))
        return None, None, None

    @retry(tries=3, delay=4, backoff=2)
    def generate_explain_requests(self):
        # no explains for an MRM pre-production model
        if self._args.mrm and not self.is_mrm_prod:
            return
        num_explains = self._args.num_explains
        if num_explains < 1:
            return
        if not self._configure_explain:
            logger.log_info('Explainability not available for this model - skipping explain request(s)')
            return
        max_explain_candidates = self._args.max_explain_candidates
        if max_explain_candidates < 1:
            max_explain_candidates = num_explains
        pause = self._args.pause_between_explains
        try:
            logger.log_info('Finding up to {} available score(s) to explain...'.format(max_explain_candidates))
            (start, end, scoring_ids) = self._get_available_scores(max_explain_candidates)
            elapsed = end - start
            logger.log_info('Found {} available score(s) for explain'.format(len(scoring_ids)))
            self.timer('find {} available score(s) for explain'.format(len(scoring_ids)), elapsed)
            if num_explains > len(scoring_ids):
                num_explains = len(scoring_ids)
            if num_explains < 1:
                return

            if self._args.explain_start_sync:
                input('Press ENTER to start generating explain requests')

            explanation_types = ["lime", "contrastive"]
            if self._args.explain_no_cem:
                explain_mode = 'lime-only'
                explanation_types = ["lime"]
            else:
                explain_mode = 'lime and cem'

            logger.log_info('Generate {} explain request(s) ({}) ...'.format(num_explains, explain_mode))
            background_mode = self._args.async_explains
            for i in range(num_explains):
                explanation_task_id = self._client.monitor_instances.explanation_tasks(
                        scoring_ids=[scoring_ids[i]],
                        explanation_types=explanation_types
                    ).result.to_dict()["metadata"]["explanation_task_ids"][0]
                if pause > 0.0 and i > 0:
                    logger.log_info("Pausing in-between explanations for {} seconds ...".format(pause))
                    time.sleep(pause)
                (start, end, explain) = self._get_explanation_status(explanation_task_id, background_mode)
                elapsed = end - start
                if not background_mode:
                    if not explain or (isinstance(explain, str) and 'errors' in explain.lower()):
                        self.metric_check_errors.append([self._model.name, 'explanation', 'failed'])
                    elif explain:
                        explain_success = explain['entity']['status']['state'].lower() == 'finished'
                        if not explain_success:
                            self.metric_check_errors.append([self._model.name, 'explanation', 'failed'])
                explain_id = ""
                if explain:
                    explain_id = explain["metadata"]["explanation_task_id"]
                logger.log_timer("Request explain in {:.3f} seconds, scoring_id: {}, explain_id: {}".format(elapsed, scoring_ids[i], explain_id))
                self.timer('request explain', elapsed)
            logger.log_info('Generated {} explain request(s)'.format(num_explains))
        except Exception as e:
            if 'lime_state' in str(e):  # temporary fix until #13571 is fixed
                pass
            else:
                message = 'WARNING: Problems occurred while running explanation: {}'.format(str(e))
                logger.log_warning(message)
                self.metric_check_errors.append([self._model.name, 'explanation', 'failed'])
        self._reliable_count_datamart_rows('generated explains')
    
