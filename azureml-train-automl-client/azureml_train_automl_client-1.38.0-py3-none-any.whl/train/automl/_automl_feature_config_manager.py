# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for getting AutoML features' configuration from JOS"""
import logging
from typing import Any, Dict, List, Optional, cast

from azureml._restclient.jasmine_client import JasmineClient
from azureml._restclient.models.feature_config_request import FeatureConfigRequest
from azureml._restclient.models.feature_config_response import FeatureConfigResponse
from azureml._restclient.models.feature_profile_input import FeatureProfileInput
from azureml._restclient.models.feature_profile_output import FeatureProfileOutput

from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.configuration.sweeper_config import SweeperConfig
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from ._automl_datamodel_utilities import CaclulatedExperimentInfo

from ._automl_datamodel_utilities import FEATURE_SWEEPING_ID, \
    STREAMING_ID, _get_feature_sweeping_config_request, _get_streaming_config_request
from .utilities import _is_gpu

logger = logging.getLogger(__name__)


class AutoMLFeatureConfigManager:
    """Config manager for automl features."""

    def __init__(self, jasmine_client: JasmineClient):
        """
        Config manager for AutoML features. eg. Feature sweeping

        :param jasmine_client: Jasmine REST client.
        :param logger: Logger.
        """
        self.jasmine_client = jasmine_client
        self.feature_profile_input_version = "1.0.0"

        # Cached feature config responses
        self._cached_feature_config_responses = {}  # type: Dict[str, FeatureConfigResponse]

    def fetch_all_feature_profiles_for_run(
            self,
            parent_run_id: str,
            automl_settings: AzureAutoMLSettings,
            caclulated_experiment_info: Optional[CaclulatedExperimentInfo]
    ) -> None:
        """
        Fetch and cache all appropriate feature profiles for a run.

        :param parent_run_id: Parent run id.
        :param automl_settings: AutoML settings.
        :param data_characteristics: Data characteristics of training data.
        """
        logger.info("Preparing to fetch all feature profiles for the run.")

        try:
            feature_config_requests = []  # type: List[FeatureConfigRequest]

            # Prepare feature sweeping request.
            if automl_settings.enable_feature_sweeping:
                logger.info("Preparing feature sweeping feature profile request.")
                feature_sweeping_request = _get_feature_sweeping_config_request(
                    task_type=automl_settings.task_type,
                    is_gpu=_is_gpu()
                )
                feature_config_requests.append(feature_sweeping_request)

            if caclulated_experiment_info:
                logger.info("Preparing streaming feature profile request.")
                streaming_request = _get_streaming_config_request(caclulated_experiment_info)
                feature_config_requests.append(streaming_request)

            if len(feature_config_requests) == 0:
                logger.info("There are no feature profile requests to make for this run.")
                return

            feature_profiles = self.get_feature_profiles(parent_run_id, feature_config_requests)

        except Exception as e:
            logger.warning("Error encountered while requesting feature profiles from server.")
            logging_utilities.log_traceback(
                e,
                logger,
                override_error_msg="Error encountered while requesting feature profiles from server.",
                is_critical=False)
            return

        # Cache retrieved feature profiles.
        self._cached_feature_config_responses.update(feature_profiles)

    def get_feature_profiles(self,
                             parent_run_id: str,
                             feature_config_requests: List[FeatureConfigRequest]) -> \
            Dict[str, FeatureConfigResponse]:
        """
        Get feature profile information for specified list of features.

        :param run_id: Parent run id.
        :param feature_config_requests: List of FeatureConfigRequest object.
        :rtype: Dict[str, FeatureConfigResponse] where key is feature_id.
        """
        input_map = {}  # type: Dict[str, FeatureConfigRequest]
        for feature in feature_config_requests:
            input_map[feature.feature_id] = feature
        feature_profile_input = FeatureProfileInput(version=self.feature_profile_input_version,
                                                    feature_config_input_map=input_map)
        response_dto = self.jasmine_client.get_feature_profiles(
            parent_run_id, feature_profile_input)  # type: FeatureProfileOutput
        return cast(Dict[str, FeatureConfigResponse], response_dto.feature_config_output_map)

    def get_feature_sweeping_config(self,
                                    enable_feature_sweeping: bool,
                                    parent_run_id: str,
                                    task_type: str) -> Dict[str, Any]:
        """
        Get feature sweeping config from JOS.

        :param enable_feature_sweeping: Enable feature sweeping.
        :param parent_run_id: AutoML parent run Id.
        :param task_type: Task type- Classification, Regression, Forecasting.
        :returns: Feature sweeping config for the specified task type, empty if not available/found.
        """
        if enable_feature_sweeping is False:
            return {}

        try:
            # Pull feature sweeping response from cache if available.
            feature_conf_response = \
                self._cached_feature_config_responses.get(
                    FEATURE_SWEEPING_ID)  # type: Optional[FeatureConfigResponse]

            # If no cached response, make request to server.
            if not feature_conf_response or feature_conf_response is None:
                is_gpu = _is_gpu()
                feature_config_request = _get_feature_sweeping_config_request(task_type=task_type,
                                                                              is_gpu=is_gpu)
                response = self.get_feature_profiles(parent_run_id,
                                                     [feature_config_request])  # type: FeatureProfileOutput
                feature_conf_response = response[feature_config_request.feature_id]

            feature_sweeping_config = feature_conf_response.feature_config_map['config'] \
                if feature_conf_response is not None and feature_conf_response.is_enabled else {}
            return cast(Dict[str, Any], feature_sweeping_config)
        except Exception:
            # Putting below message as info to avoid notebook failure due to warning.
            message = "Unable to fetch feature sweeping config from service, defaulting to blob store config."
            logger.info("{message}".format(message=message))
            # Below code can be used to test the feature_sweeping_config changes locally or on remote machine without
            # need of JOS.
            config = self._get_default_feature_sweeping_config()
            return cast(Dict[str, Any], config[task_type])

    def _get_default_feature_sweeping_config(self) -> Dict[str, Any]:
        """Read config and setup the list of enabled sweepers."""
        try:
            return SweeperConfig().get_config()
        except (IOError, FileNotFoundError) as e:
            logger.warning("Error trying to read configuration file")
            logging_utilities.log_traceback(e, logger, is_critical=False)
            return {}

    def is_streaming_enabled(self):
        """Return whether streaming is enabled for the run."""
        streaming_config = self._cached_feature_config_responses.get(STREAMING_ID)
        if streaming_config is None:
            return False
        return streaming_config.is_enabled
