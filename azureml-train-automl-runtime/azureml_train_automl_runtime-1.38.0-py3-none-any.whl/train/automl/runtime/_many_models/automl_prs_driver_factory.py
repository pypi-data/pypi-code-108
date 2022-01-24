# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, cast, Dict, Optional
from logging import Logger

from azureml._restclient.experiment_client import ExperimentClient
from azureml._restclient.models.create_run_dto import CreateRunDto
from azureml._restclient.models.run_type_v2 import RunTypeV2

from azureml.core import Run
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.train.automl.runtime._many_models.train_helper import Arguments
from azureml.train.automl.runtime._many_models.automl_prs_driver_base import AutoMLPRSDriverBase
from azureml.train.automl.runtime._many_models.many_models_automl_train_driver import ManyModelsAutoMLTrainDriver
from azureml.train.automl.runtime._many_models.many_models_inference_driver import ManyModelsInferenceDriver
from azureml.train.automl.runtime._hts.hts_automl_train_driver import HTSAutoMLTrainDriver
from azureml.train.automl.runtime._hts.hts_data_aggregation_driver import HTSDataAggregationDriver
from azureml.train.automl.runtime._hts.hts_forecast_parallel_driver import HTSForecastParallelDriver


class AutoMLPRSDriverFactory:
    HTS_AUTOML_TRAIN = "HTSAutoMLTrain"
    HTS_DATA_AGGREGATION = "HTSDataAggregation"
    HTS_FORECAST_PARALLEL = "ForecastParallel"
    MANY_MODELS_AUTOML_TRAIN = "ManyModelsAutoMLTrain"
    MANY_MODELS_INFERENCE = "ManyModelsInference"

    AUTOML_HTS_TRAIN_TRAIT = "AutoMLHTSTrain"
    AUTOML_HTS_INFERENCE_TRAIT = "AutoMLHTSInference"
    AUTOML_MANY_MODELS_TRAIN_TRAIT = "AutoMLManyModelsTrain"
    AUTOML_MANY_MODELS_INFERENCE_TRAIT = "AutoMLManyModelsInference"

    @staticmethod
    def add_run_trait(
            scenario_trait: str,
            current_step_run: Run
    ) -> None:
        """
        Add trait based on the scenario to the run for telemetry purposes.

        :param scenario_trait: The MM/HTS training or inference run.
        :param current_step_run: The current PRS run.
        """
        create_run_dto = CreateRunDto(current_step_run.id, run_type_v2=RunTypeV2(traits=[scenario_trait]))

        experiment = current_step_run.experiment
        experiment_client = ExperimentClient(
            experiment.workspace.service_context,
            experiment.name,
            experiment_id=experiment.id
        )
        experiment_client.create_run(current_step_run.id, create_run_dto=create_run_dto)

    @staticmethod
    def get_automl_prs_driver(
            scenario: str,
            current_step_run: Run,
            logger: Logger,
            args: Arguments,
            automl_settings: Optional[Dict[str, Any]] = None,
    ) -> AutoMLPRSDriverBase:
        """
        Get AutoML PRS driver code based on scenario.

        :param scenario: The PRS run scenario.
        :param current_step_run: The current PRS run.
        :param logger: The logger.
        :param args: The args used in the PRS run.
        :param automl_settings: The automl settings dict.
        :return: An AutoMLPRSDriverBase that used in PRS step.
        """
        driver = None  # type: Optional[AutoMLPRSDriverBase]
        if scenario == AutoMLPRSDriverFactory.MANY_MODELS_AUTOML_TRAIN:
            driver = ManyModelsAutoMLTrainDriver(
                current_step_run, cast(Dict[str, Any], automl_settings), args
            )
            AutoMLPRSDriverFactory.add_run_trait(AutoMLPRSDriverFactory.AUTOML_MANY_MODELS_TRAIN_TRAIT,
                                                 current_step_run)
        elif scenario == AutoMLPRSDriverFactory.MANY_MODELS_INFERENCE:
            driver = ManyModelsInferenceDriver(
                current_step_run, args
            )
            AutoMLPRSDriverFactory.add_run_trait(AutoMLPRSDriverFactory.AUTOML_MANY_MODELS_INFERENCE_TRAIT,
                                                 current_step_run)
        elif scenario == AutoMLPRSDriverFactory.HTS_DATA_AGGREGATION:
            driver = HTSDataAggregationDriver(
                current_step_run, args, cast(Dict[str, Any], automl_settings)
            )
        elif scenario == AutoMLPRSDriverFactory.HTS_FORECAST_PARALLEL:
            driver = HTSForecastParallelDriver(
                current_step_run, args
            )
            AutoMLPRSDriverFactory.add_run_trait(AutoMLPRSDriverFactory.AUTOML_HTS_INFERENCE_TRAIT,
                                                 current_step_run)
        elif scenario == AutoMLPRSDriverFactory.HTS_AUTOML_TRAIN:
            driver = HTSAutoMLTrainDriver(
                current_step_run, cast(Dict[str, Any], automl_settings), args
            )
            AutoMLPRSDriverFactory.add_run_trait(AutoMLPRSDriverFactory.AUTOML_HTS_TRAIN_TRAIT,
                                                 current_step_run)

        Contract.assert_type(
            driver, "AutoMLPRSDriver",
            expected_types=(
                ManyModelsAutoMLTrainDriver, ManyModelsInferenceDriver, HTSDataAggregationDriver,
                HTSForecastParallelDriver, HTSAutoMLTrainDriver
            ),
            reference_code=ReferenceCodes._MANY_MODELS_WRONG_DRIVER_TYPE
        )
        driver = cast(AutoMLPRSDriverBase, driver)

        return driver
