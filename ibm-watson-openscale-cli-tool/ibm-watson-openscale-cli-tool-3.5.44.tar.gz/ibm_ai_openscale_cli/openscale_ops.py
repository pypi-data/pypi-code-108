# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
import time
from ibm_ai_openscale_cli.enums import ResetType, MLEngineType
from ibm_ai_openscale_cli.openscale.openscale_client import OpenScaleClient
from ibm_ai_openscale_cli.ops import Ops
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger

logger = FastpathLogger(__name__)


class OpenScaleOps(Ops):

    def __init__(self, args):
        super().__init__(args)
        self._model_names = self.get_models_list()
        self.run_once = True

    def _validate_model_name(self):
        valid_names_list = self.get_models_list()
        if self._args.model not in valid_names_list:
            error_msg = 'Invalid model name specified. Only the following models are supported for {}: {}'.format(self._args.ml_engine_type.value, valid_names_list)
            logger.log_error(error_msg)
            raise Exception(error_msg)

    def _validate_custom_model(self):
        if self._args.custom_model and not self._args.custom_model_directory:
            error_msg = 'Custom model must specify --custom-model-directory'
            logger.log_error(error_msg)
            raise Exception(error_msg)
        if self._args.custom_model_directory and not self._args.custom_model:
            error_msg = 'Custom model must specify --custom-model model name'
            logger.log_error(error_msg)
            raise Exception(error_msg)

    def _model_validations(self):
        if self._args.custom_model or self._args.custom_model_directory:
            self._validate_custom_model()
            self._model_names = [self._args.custom_model]
            self._args.model = self._args.custom_model
        elif self._args.model != 'all':
            self._validate_model_name()
            self._model_names = [self._args.model]
            if self._args.mrm:
                self._model_names.insert(0, '{}PreProd'.format(self._args.model))
                self._model_names.insert(0, '{}Challenger'.format(self._args.model))

    def _instantiate_openscale_client(self):
        start = time.time()
        openscale_credentials = self._credentials.get_openscale_credentials()
        elapsed = time.time() - start
        self.timer('get openscale credentials',elapsed)
        start = time.time()
        database_credentials = self._credentials.get_database_credentials()
        elapsed = time.time() - start
        self.timer('get database credentials',elapsed)
        start = time.time()
        ml_engine_credentials = self._credentials.get_ml_engine_credentials()
        elapsed = time.time() - start
        self.timer('get ml engine credentials',elapsed)
        openscale_client = OpenScaleClient(self._args, openscale_credentials, database_credentials, ml_engine_credentials)
        logger.log_info('Watson OpenScale data mart id: {}'.format(openscale_credentials['data_mart_id']))
        return openscale_client

    def _validate_datamart_reset(self, openscale_client):
        if self._args.protect_datamart: # Do not reset any existing datamart before setup
            data_mart_count = openscale_client.get_data_mart_count()
            if data_mart_count != 0:
                error_msg = "Unable to proceed with the setup as an existing datamart setup was found."
                logger.log_error(error_msg)
                raise Exception(error_msg)

    def _reset_datamart(self, openscale_client):
        if not self._args.extend:
            openscale_client.reset(ResetType.DATAMART)
            openscale_client.create_datamart()

    def _bind_ml_instance(self, openscale_client, ml_engine_prod=None, ml_engine_preprod=None):
        if not self._args.extend:
            ml_engine_credentials = self._credentials.get_ml_engine_credentials()
            openscale_client.bind_mlinstance(ml_engine_credentials, ml_engine_prod, ml_engine_preprod)

    def use_existing_binding_if_extending_datamart(self, openscale_client, asset_details_dict):
        if self._args.extend and self.run_once:
            self.run_once = False
            openscale_client.use_existing_binding(asset_details_dict)

    def execute(self):

        # validations
        self._model_validations()

        # credentials
        openscale_client = self._instantiate_openscale_client()

        self._validate_datamart_reset(openscale_client)

        # Instantiate ml engine
        """
        if not self._args.is_icp:
            if not self._args.is_icp and self._args.v4:
                if self._args.ml_engine_type is MLEngineType.WML:
                    self._cos_credentials, self._cos_instance = self.get_cos_instance()
                    openscale_client.set_cos_credentials(self._cos_credentials)
        """
        ml_engine_prod = self.get_ml_engine_instance(openscale_client)

        ml_engine_preprod = None
        if self._args.mrm:
            ml_engine_preprod = self.get_ml_engine_instance(openscale_client, self._args.mrm)

        # reset datamart
        self._reset_datamart(openscale_client)
        if self._args.mrm:
            self._bind_ml_instance(openscale_client, ml_engine_prod, ml_engine_preprod)
        else:
            self._bind_ml_instance(openscale_client, ml_engine_prod)

        modeldata = None
        first = True
        for modelname in self._model_names:
            openscale_client.is_mrm_challenger = False
            openscale_client.is_mrm_preprod = False
            openscale_client.is_mrm_prod = False
            if self._args.mrm:
                if 'challenger' in modelname.lower():
                    ml_engine = ml_engine_preprod
                    openscale_client.is_mrm_challenger = True
                elif 'preprod' in modelname.lower():
                    ml_engine = ml_engine_preprod
                    openscale_client.is_mrm_preprod = True
                else:
                    ml_engine = ml_engine_prod
                    openscale_client.is_mrm_prod = True
            else:
                ml_engine = ml_engine_prod
            logger.log_info_h1('Model: {}, Engine: {}'.format(modelname, self._args.ml_engine_type.value))
            for model_instance_num in range(self._args.model_first_instance, self._args.model_first_instance + self._args.model_instances):
                if self._args.model_instances > 1:
                    logger.log_info('Model instance {}'.format(model_instance_num))
                if not first and self._args.pause_between_models > 0:
                    logger.log_info('Pause for {:.3f} seconds before starting this model'.format(self._args.pause_between_models))
                    time.sleep(self._args.pause_between_models)
                first = False

                # get the iam headers that will be used for all REST API calls for this model
                openscale_client.set_iam_headers()

                # model instance
                modeldata = self.get_modeldata_instance(modelname, model_instance_num)
                openscale_client.set_model(modeldata)
                """
                if not self._args.is_icp and self._args.v4:  # Cloud WML V4, COS is needed
                    if self._args.ml_engine_type is MLEngineType.WML:
                        openscale_client.perform_cos_operations(self._cos_instance)
                """

                if self._args.values_per_score > 1 and (openscale_client.is_unstructured_text() or openscale_client.is_unstructured_image()):
                    self._args.num_scores = self._args.values_per_score * self._args.num_scores
                    self._args.values_per_score = 1
                    logger.log_info('FYI: This model only supports 1 value per score request. Continuing with each value in its own score request')


                asset_details_dict = None
                # ml engine instance
                if self._args.ml_engine_type is MLEngineType.WML:
                    ml_engine.set_model(modeldata)
                    if not self._args.deployment_name:
                        asset_details_dict = ml_engine.create_model_and_deploy()
                    else:
                        asset_details_dict = ml_engine.get_existing_deployment(self._args.deployment_name)
                else:
                    asset_details_dict = openscale_client.get_asset_details(self._args.deployment_name)

                self.use_existing_binding_if_extending_datamart(openscale_client, asset_details_dict)

                # ai openscale operations
                if self._args.history_only:
                    openscale_client.use_existing_subscription(asset_details_dict)
                else:
                    openscale_client.subscribe_to_model_deployment(asset_details_dict)
                    openscale_client.generate_sample_scoring(ml_engine, numscores=1, values_per_score=1, to_init_payload_logging=True)
                    openscale_client.configure_subscription_monitors()

                if self._args.subscription_details != 'none':
                    openscale_client.save_subscription_details()
                if openscale_client.generate_sample_metrics():
                    openscale_client.load_historical_payloads()
                    openscale_client.load_historical_fairness()
                    openscale_client.load_historical_quality()
                    openscale_client.confirm_payload_logging()
                    openscale_client.load_historical_debiased_payloads()
                    openscale_client.load_historical_drift()
                    openscale_client.load_historical_performance()
                    openscale_client.load_historical_explanations()
                
                openscale_client.generate_sample_scoring(ml_engine, numscores=self._args.num_scores, values_per_score=self._args.values_per_score)
                openscale_client.trigger_monitors()
                openscale_client.generate_explain_requests()

        if self._args.summary:
            try:
                from tabulate import tabulate
            except ModuleNotFoundError as e:
                logger.log_info('Module "tabulate" not found, attempting to install ...')
                from ibm_ai_openscale_cli.utility_classes.utils import pip_install
                pip_install('tabulate')
            length_errors = len(openscale_client.metric_check_errors)
            if length_errors > 1:
                summary_title = tabulate([tabulate([['Summary:']])])
                table_headers = openscale_client.metric_check_errors[0]
                table_rows = openscale_client.metric_check_errors[1:length_errors]
                summary_table = tabulate(table_rows, headers=table_headers)
                logger.log_info('\n' * 3)
                logger.log_info(summary_title)
                logger.log_info('')
                logger.log_info(summary_table)
                logger.log_info('')

            if len(list(openscale_client.timers)) > 0 or len(list(self.timers)) > 0:
                summary_title = tabulate([tabulate([['Timers:']])])
                table_headers = ['tag', 'count', 'seconds', 'average']
                table_rows = []
                total_count = 0
                total_seconds = 0
                for tag in list(openscale_client.timers):
                    total_count += openscale_client.timers[tag]['count']
                    total_seconds += openscale_client.timers[tag]['seconds']
                    average = openscale_client.timers[tag]['seconds'] / openscale_client.timers[tag]['count']
                    table_rows.append([tag, openscale_client.timers[tag]['count'], openscale_client.timers[tag]['seconds'], average])
                for tag in list(self.timers):
                    total_count += self.timers[tag]['count']
                    total_seconds += self.timers[tag]['seconds']
                    average = self.timers[tag]['seconds'] / self.timers[tag]['count']
                    table_rows.append([tag, self.timers[tag]['count'], self.timers[tag]['seconds'], average])
                table_rows.sort(key=lambda item: item[0])
                table_rows.append(['TOTAL', total_count, total_seconds])
                summary_table = tabulate(table_rows, headers=table_headers)
                logger.log_info('\n' * 3)
                logger.log_info(summary_title)
                logger.log_info('')
                logger.log_info(summary_table)
                logger.log_info('')

