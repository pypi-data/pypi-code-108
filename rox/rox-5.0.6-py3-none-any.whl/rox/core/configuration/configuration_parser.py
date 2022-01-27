from datetime import datetime
import json
import traceback

from rox.core.configuration.configuration import Configuration
from rox.core.configuration.configuration_fetched_invoker import FetcherError
from rox.core.configuration.models.experiment_model import ExperimentModel
from rox.core.configuration.models.target_group_model import TargetGroupModel
from rox.core.logging.logging import Logging
from rox.core.network.configuration_result import ConfigurationSource


class ConfigurationParser:
    def __init__(self, signature_verifier, error_reporter, configuration_fetched_invoker):
        self.signature_verifier = signature_verifier
        self.error_reporter = error_reporter
        self.configuration_fetched_invoker = configuration_fetched_invoker

    def parse(self, fetch_result, sdk_settings):
        try:
            return self.parse_internal(fetch_result, sdk_settings)
        except Exception as ex:
            Logging.get_logger().error('Failed to parse configurations', ex)
            self.configuration_fetched_invoker.invoke_error(FetcherError.UNKNOWN)

        return None

    def parse_internal(self, fetch_result, sdk_settings):
        json_obj = fetch_result.json_data

        if fetch_result.source != ConfigurationSource.ROXY and not self.signature_verifier.verify(json_obj['data'], json_obj['signature_v0']):
            self.configuration_fetched_invoker.invoke_error(FetcherError.SIGNATURE_VERIFICATION_ERROR)
            self.error_reporter.report('Failed to validate signature',
                                       Exception('Data : %s Signature : %s' % (json_obj['data'], json_obj['signature_v0'])),
                                       traceback.extract_stack())
            return None

        signature_date = datetime.strptime(json_obj['signed_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
        internal_data_string = json_obj['data']
        internal_data_object = json.loads(internal_data_string)
        if fetch_result.source != ConfigurationSource.ROXY and internal_data_object['application'] != sdk_settings.api_key:
            self.configuration_fetched_invoker.invoke_error(FetcherError.MISMATCH_APP_KEY)
            self.error_reporter.report('Failed to parse JSON configuration - ',
                                       ValueError('Internal Data: %s SdkSettings: %s' % (internal_data_object["application"], sdk_settings.api_key)),
                                       traceback.extract_stack())
            return None

        experiments = self.parse_experiments(internal_data_object)
        target_groups = self.parse_target_groups(internal_data_object)

        return Configuration(experiments, target_groups, signature_date)

    def parse_experiments(self, data):
        return [self.parse_experiment(e) for e in data['experiments']]

    def parse_experiment(self, data):
        condition = data['deploymentConfiguration']['condition']
        is_archived = data['archived']
        name = data['name']
        id = data['_id']
        labels = set(data.get('labels', []))
        flags = [f['name'] for f in data['featureFlags']]
        stickinessProperty = data['stickinessProperty']
        return ExperimentModel(id, name, condition, is_archived, flags, labels, stickinessProperty)

    def parse_target_groups(self, data):
        return [self.parse_target_group(e) for e in data['targetGroups']]

    def parse_target_group(self, data):
        return TargetGroupModel(data['_id'], data['condition'])
