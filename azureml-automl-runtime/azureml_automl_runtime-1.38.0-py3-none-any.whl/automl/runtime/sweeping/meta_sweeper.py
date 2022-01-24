# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Runs all enabled features sweepers."""
from typing import Any, cast, Dict, List, Optional, Tuple, Union
from functools import reduce
import logging

import numpy as np
import os
import pandas as pd
import pickle
import scipy
import tempfile

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ConflictingValueForArguments
from sklearn.base import BaseEstimator
from sklearn.pipeline import make_pipeline, Pipeline

from azureml.automl.core.shared import activity_logger, logging_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.runtime.shared import resource_limits
from azureml.automl.runtime.shared.types import CoreDataInputType, DataInputType, \
    CoreDataSingleColumnInputType, DataSingleColumnInputType
from azureml.automl.core.constants import TextNeuralNetworks, SweepingMode, TextDNNLanguages
from azureml.automl.core.configuration import FeatureConfig, SweeperConfig, ConfigKeys
from azureml.automl.core.configuration.sampler_config import SamplerConfig
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.runtime.estimation import Estimators
from ..column_purpose_detection import StatsAndColumnPurposeType
from ..featurization import Featurizers
from ..sampling import AbstractSampler, DataProvider, DiskBasedDataProvider, InMemoryDataProvider, Samplers
from ..scoring import Scorers, AbstractScorer
from ..sweeping.abstract_sweeper import AbstractSweeper
from ..sweeping.sweepers import Sweepers
from ..featurizer.transformer import WordEmbeddingsInfo

logger = logging.getLogger(__name__)


class MetaSweeper:
    """Runs all enabled features sweepers."""

    DEFAULT_SWEEPER_TIMEOUT_SEC = 3600  # 1 hour

    def __init__(self,
                 task: str,
                 timeout_sec: int = DEFAULT_SWEEPER_TIMEOUT_SEC,
                 featurization_config: Optional[FeaturizationConfig] = None,
                 is_cross_validation: bool = False,
                 enable_dnn: bool = False,
                 force_text_dnn: bool = False,
                 feature_sweeping_config: Dict[str, Any] = {}) -> None:
        """Load configuration and create sweeper configurations.

        :param task: Task type- Classification, Regression or Forecasting.
        :param timeout_sec: Timeout in seconds for feature sweeping.
        :param is_cross_validation: Whether to do the cross validation.
        :param feature_sweeping_config: Feature sweeping config.
        :param enable_dnn: Flag to enable sweeping over text DNNs such as BERT, BiLSTM.
        :param force_text_dnn: Flag to force add text DNNs such as BERT, BiLSTM after sweeping.
        """
        self._task = task
        self._cfg = feature_sweeping_config  # type: Dict[str,Any]

        self._enabled = self._cfg.get(ConfigKeys.SWEEPING_ENABLED, False)
        self._sweepers = []  # type: List[AbstractSweeper]
        self._enabled_sweeper_configs = []  # type: List[SweeperConfig]
        self._is_cross_validation = is_cross_validation
        self._enable_dnn = enable_dnn and not self._is_cross_validation  # DNNs do not support cross-validation
        self._featurization_config = featurization_config
        self._class_balancing = self._cfg.get(ConfigKeys.ENABLE_CLASS_BALANCING, False)
        self._enabled_balancer_configs = []  # type: List[SweeperConfig]
        self._force_text_dnn = force_text_dnn

        # Select default language for text dnns or use langauge specified in featurization config
        if self._featurization_config is None or self._featurization_config.dataset_language is None:
            self._dataset_language = TextDNNLanguages.default
        else:
            self._dataset_language = self._featurization_config.dataset_language

        # Set sweeping configs with user specified params like enable_dnn and featurization_config
        self._set_feature_sweeping_configs()
        self._set_class_balancing_sweeper_configs()

        self._timeout_sec = timeout_sec
        self._temp_files_to_cleanup = []  # type: List[str]
        self._page_sampled_data_to_disk = self._cfg.get(ConfigKeys.PAGE_SAMPLED_DATA_TO_DISK, True)
        self._run_sweeping_in_isolation = self._cfg.get(ConfigKeys.RUN_SWEEPING_IN_ISOLATION, True)

    def _set_feature_sweeping_configs(self):
        """ Create and set feature sweeper configs objects and join with user settings to decide what sweepers
            are enabled, and in some cases what parameters they have such as
            enable_dnn or force_text_dnn."""

        # Text dnn logic based on enable_dnn, force_text_dnn, and dataset_language.
        if self._enabled:
            sweeper_configs = [{}] if self._cfg is None \
                else self._cfg.get(ConfigKeys.ENABLED_SWEEPERS, [])  # type: List[Dict[str, Any]]
            self._sweeper_name_list = []  # type: List[str]
            for sweeper_config in sweeper_configs:
                sweeper_config_obj = SweeperConfig.from_dict(sweeper_config)
                if not sweeper_config_obj._enabled:  # Only care about sweepers that are not individually disabled.
                    continue

                sweeper_name = sweeper_config_obj._name
                if sweeper_name in TextNeuralNetworks.ALL:
                    if not self._enable_dnn:  # The experiment is for a text DNN, but DNNs are not enabled.
                        continue
                    elif self._force_text_dnn:  # Force sweeping to choose the text DNN by overriding the experiment.
                        sweeper_config_obj._experiment_result_override = True

                    if sweeper_name == TextNeuralNetworks.BERT:
                        # Change the BERT model according to the given language
                        for featurizer in sweeper_config_obj._experiment["featurizers"]:
                            if featurizer["id"] == "pretrained_text_dnn":
                                featurizer["kwargs"]["dataset_language"] = self._dataset_language

                self._enabled_sweeper_configs.append(sweeper_config_obj)
                self._sweeper_name_list.append(sweeper_name)

            # Non-unique sweeper._name's can break how we loop over sweepers in _sweep_internal()
            duplicate_sweepers = set([x for x in self._sweeper_name_list if self._sweeper_name_list.count(x) > 1])
            if duplicate_sweepers:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ConflictingValueForArguments, target="_sweeper_name_list",
                        arguments='_sweeper_name_list ({})'.format(", ".join(duplicate_sweepers))
                    )
                )

    def _set_class_balancing_sweeper_configs(self):
        """ Create and set class balancing sweeper config objects"""

        # Class balancing logic
        if self._class_balancing:
            balancer_configs = [{}] if self._cfg is None \
                else self._cfg.get(ConfigKeys.ENABLED_BALANCERS, [])  # type: List[Dict[str, Any]]
            self._balancer_name_list = []  # type: List[str]
            for balancer_config in balancer_configs:
                balancer_config_obj = SweeperConfig.from_dict(balancer_config)
                if not balancer_config_obj._enabled:  # Only care about sweepers that are not individually disabled.
                    continue
                balancer_name = balancer_config_obj._name
                if balancer_name not in self._balancer_name_list:  # dedupe balancer
                    self._enabled_balancer_configs.append(balancer_config_obj)
                    self._balancer_name_list.append(balancer_name)

    # TODO: Balancing sweeping and the normal sweeping return completely different data structures. Refactor!
    def sweep(self,
              working_dir: str,
              X: DataInputType,
              y: DataSingleColumnInputType,
              stats_and_column_purposes: Optional[List[StatsAndColumnPurposeType]] = None,
              sweeping_mode: str = SweepingMode.Feature) -> List[Any]:
        """Feature sweeping and / or class balancing sweeping"""

        # Formalize type assumptions already made in both sweeping scenarios.
        Contract.assert_type(X, "sweeping input", expected_types=(np.ndarray, pd.DataFrame, scipy.sparse.spmatrix))
        Contract.assert_type(y, "sweeping targets", expected_types=(np.ndarray, pd.Series, pd.Categorical))

        if sweeping_mode == SweepingMode.Feature:
            # Feature sweeping goes a step further and expects X as a DataFrame. Other types will break us.
            Contract.assert_type(X, "sweeping input", expected_types=pd.DataFrame)
            # Feature sweeping also needs a non-empty stats and column purposes list.
            Contract.assert_non_empty(stats_and_column_purposes, "stats_and_column_purposes")
            return self._sweep_feature(working_dir,
                                       cast(pd.DataFrame, X),
                                       y,
                                       cast(List[StatsAndColumnPurposeType], stats_and_column_purposes))

        if sweeping_mode == SweepingMode.Balancing:
            return self._sweep_balancing(working_dir, X, y)

        return []

    def _sweep_balancing(self,
                         working_dir: str,
                         X: CoreDataInputType,
                         y: CoreDataSingleColumnInputType) -> List[Any]:
        """Sweep through all class balancers in the configuration."""

        if self._class_balancing is False:
            logger.info("Class balancing sweeping disabled")

        is_valid, msg = self._validate(X, y)
        if not is_valid:
            logger.info(msg)
            return []

        sweepers = self._build_sweepers(working_dir, X, y,
                                        enabled_sweeper_configs=self._enabled_balancer_configs,
                                        sweeping_mode=SweepingMode.Balancing)

        kwargs = {"sweepers": sweepers}  # type: Dict[str, Any]

        exit_status = None
        result = None  # type: Optional[List[Any]]
        try:
            if self._run_sweeping_in_isolation is False:
                return MetaSweeper._sweep_balancing_internal(**kwargs)

            constraints = resource_limits.DEFAULT_RESOURCE_LIMITS
            constraints[resource_limits.TIME_CONSTRAINT] = self._timeout_sec
            limiter = resource_limits.SafeEnforceLimits(enable_limiting=True, **constraints)
            result, exit_status, _ = limiter.execute(working_dir,
                                                     MetaSweeper._sweep_balancing_internal,
                                                     sweepers)

        except Exception:
            logger.warning("Balancing sweeping sub-process failed")

        return cast(List[Any], result)

    def _sweep_feature(self,
                       working_dir: str,
                       X: pd.DataFrame,
                       y: CoreDataSingleColumnInputType,
                       stats_and_column_purposes: List[StatsAndColumnPurposeType]) \
            -> List[Tuple[str, Pipeline]]:
        """Sweep through all the sweepers in the configurations."""

        if self._enabled is False:
            logger.debug("Feature sweeping disabled.")
            return []

        is_valid, msg = self._validate(X, y)
        if not is_valid:
            logger.info(msg)
            return []

        column_groups = {}  # type: Dict[str, List[str]]
        if stats_and_column_purposes is not None:
            for _, column_purpose, column in stats_and_column_purposes:
                column_groups.setdefault(column_purpose.lower(), []).append(column)

        sweepers = self._build_sweepers(working_dir, X, y,
                                        enabled_sweeper_configs=self._enabled_sweeper_configs,
                                        sweeping_mode=SweepingMode.Feature,
                                        column_groups=column_groups)

        file_handle, checkpoint_file = tempfile.mkstemp(suffix=".ck", prefix="feature_sweep_", dir=working_dir)
        self._temp_files_to_cleanup.append(checkpoint_file)
        # after creating the file, mkstemp holds a lock on it, preventing us from removing it after we're done
        # so we'll close that handle right after creation
        os.close(file_handle)

        exit_status = None
        result = None  # type: Optional[List[Tuple[Any, Pipeline]]]
        try:
            # TODO: Can we use enable_limiting=False for this case?
            if self._run_sweeping_in_isolation is False:
                return MetaSweeper._sweep_internal(sweepers,
                                                   self._enabled_sweeper_configs,
                                                   checkpoint_file,
                                                   column_groups)

            constraints = resource_limits.DEFAULT_RESOURCE_LIMITS
            constraints[resource_limits.TIME_CONSTRAINT] = self._timeout_sec
            limiter = resource_limits.SafeEnforceLimits(enable_limiting=True, **constraints)
            result, exit_status, _ = limiter.execute(working_dir,
                                                     MetaSweeper._sweep_internal,
                                                     sweepers,
                                                     self._enabled_sweeper_configs,
                                                     checkpoint_file,
                                                     column_groups)

            # the subprocess can silently fail, in which case fallback to recovering from checkpoint file
            if result is None:
                # This will always be a BaseException. Cast is required since combining Union and Tuple doesn't work
                exit_status = cast(BaseException, exit_status)
                logger.warning("Feature sweeping silently failed. ExitStatus: {}".format(exit_status))
                logging_utilities.log_traceback(exit_status, logger, is_critical=False)
                result = self._recover_sweeping_from_checkpointfile(checkpoint_file)
        except Exception as ex:
            logger.warning("Feature sweeping sub-process failed.")
            logging_utilities.log_traceback(ex, logger, is_critical=False)
            result = self._recover_sweeping_from_checkpointfile(checkpoint_file)
        finally:
            self._remove_temporary_files()

        return cast(List[Tuple[str, Any]], result)

    def _recover_sweeping_from_checkpointfile(self, checkpoint_file: str) -> List[Tuple[Any, Pipeline]]:
        # let's try to open the checkpoint file and recover as much as possible from there.
        result = []
        logger.info("Recovering sweeping metadata from checkpoint file")
        try:
            with open(checkpoint_file, 'rb') as ck_file:
                for row in ck_file:
                    sweeper_idx, columns = pickle.loads(row)
                    sweeper_config = self._enabled_sweeper_configs[int(sweeper_idx)]

                    result.append((columns,  # Handle group of columns case.
                                   self._build_featurizers(sweeper_config._experiment)))
            recovered_sweeps_count = len(result)
            if recovered_sweeps_count > 0:
                logger.debug(
                    "Recovered {} sweeping metadata items from checkpoint file.".format(recovered_sweeps_count))
        except Exception:
            pass

        return result

    @staticmethod
    def _sweep_balancing_internal(sweepers: List[AbstractSweeper]) -> List[Any]:
        return_strategies = []  # type: List[Any]

        logger.info("Begin Balancing Sweeping...")

        for sweeper_idx, sweeper in enumerate(sweepers):

            if sweeper.sweep():
                logger.debug("Sweep returned true for: {sweeper}".format(sweeper=sweeper))
                return_strategies.append(sweeper._name)
            else:
                logger.debug(
                    "Sweep returned false for: {sweeper} ".format(sweeper=sweeper))

        logger.info("Finished sweeping with all balancing sweepers.")
        return return_strategies

    @staticmethod
    def _sweep_internal(sweepers: List[AbstractSweeper],
                        enabled_sweeper_configs: List[SweeperConfig],
                        checkpoint_file: str,
                        column_groups: Dict[str, List[str]]) -> List[Tuple[str, Pipeline]]:
        return_transforms = []  # type: List[Tuple[Any, Any]]

        logger.info("Begin Feature Sweeping...")

        with open(checkpoint_file, mode='wb', buffering=1) as ck_file:
            for sweeper_idx, sweeper in enumerate(sweepers):
                # Get sweeper config by name in case of misalignment between sweeper_configs and sweepers
                sweeper_config = next((x for x in enabled_sweeper_configs if x._name == sweeper._name), None)
                if sweeper_config is None:
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            ArgumentBlankOrEmpty, target="sweeper_config",
                            argument_name="sweeper_config ({})".format(sweeper._name)
                        )
                    )

                cols, group = MetaSweeper._determine_columns_of_interest(sweeper_config, column_groups)
                if not group:
                    for col_id, column in enumerate(cols):
                        if sweeper.sweep(column):
                            logger.debug("Sweep returned true for: {sweeper} on column index: {col}".format(
                                sweeper=sweeper, col=col_id))

                            # persist our progress so far in case this child process dies out of a sudden
                            ck_file.write(pickle.dumps((sweeper_idx, column)))
                            return_transforms.append((column, sweeper._experiment))
                        else:
                            logger.debug(
                                "Sweep returned false for: {sweeper} "
                                "on col id: {col}".format(sweeper=sweeper, col=col_id))
                else:
                    featurize_separately = False
                    if group == 'score':
                        featurize_separately = True
                    col_string = reduce(lambda a, b: str(a) + "," + str(b), cols)
                    if sweeper.sweep(featurize_separately=featurize_separately):
                        logger.debug("Sweep returned true for: {sweeper} on column index: {col}".format(
                            sweeper=sweeper, col=col_string))
                        ck_file.write(pickle.dumps((sweeper_idx, col_string)))
                        if featurize_separately:
                            return_transforms.extend(([col], sweeper._experiment) for col in cols)
                        else:
                            return_transforms.append((cols, sweeper._experiment))
                    else:
                        logger.debug(
                            "Sweep returned false for: {sweeper} "
                            "for col ids: {col}".format(sweeper=sweeper, col=col_string))

        logger.info("Finished sweeping with all feature sweepers.")
        return return_transforms

    def _build_sweepers(self, working_dir: str, X: CoreDataInputType, y: CoreDataSingleColumnInputType,
                        enabled_sweeper_configs: Optional[List[SweeperConfig]] = None,
                        sweeping_mode: str = SweepingMode.Feature,
                        column_groups: Optional[Dict[str, List[str]]] = None) -> List[AbstractSweeper]:
        """
        Build and return relevant sweepers for the experiment. This is used for both feature sweeping and class
        balancing. The sweepers are built based on the corresponding sweeper configuration objects, which are read
        in upstream from JOS or a default config, if communication fails.

        :param working_dir: The working directory.
        :param X: The input data on which we will run the sweeping experiment.
        :param y: The input labels with which we will run the sweeping experiments.
        :param enabled_sweeper_configs: A list of configuration objects that we will use to build the
        associated Sweepers. If this list is empty or unspecified, this function returns early as there
        are no sweepers to be built.
        :param sweeping_mode: Whether we are doing feature or class balancing sweeping.
        :param column_groups: A dictionary of types and the associated column names for each type.
        :return: List of relevant sweepers for the experiment.
        """
        if not enabled_sweeper_configs:
            return []

        logger.debug("Sweeper configuration: {c}".format(c=enabled_sweeper_configs))
        sweepers = []
        for enabled_sweeper_config in enabled_sweeper_configs:
            # Build sampler
            sampler = self._build_sampler(
                SamplerConfig.from_dict(enabled_sweeper_config._sampler), task=self._task)
            # Build estimator
            estimator = Estimators.get(enabled_sweeper_config._estimator)  # type: Optional[BaseEstimator]
            # Build scorer
            scorer = Scorers.get(
                enabled_sweeper_config._scorer,
                experiment_result_override=enabled_sweeper_config._experiment_result_override,
                task=self._task)  # type: Optional[AbstractScorer]

            # Determine columns of interest
            columns_of_interest = []  # type: List[str]
            group = False  # type: Union[bool, str]
            if sweeping_mode == SweepingMode.Feature:
                Contract.assert_non_empty(column_groups, "column_groups")  # Mandatory for feature sweeping.
                columns_of_interest, group = \
                    MetaSweeper._determine_columns_of_interest(enabled_sweeper_config,
                                                               cast(Dict[str, List[str]], column_groups))
                if not len(columns_of_interest):  # No relevant columns for specified type, so skip.
                    continue

            # Build data provider
            data_provider = self._build_data_provider(X=X, y=y,
                                                      sampler=sampler,
                                                      working_dir=working_dir,
                                                      include_columns=columns_of_interest,
                                                      group=group)

            # Build baseline and experiment featurizers only for feature sweeping mode
            if sweeping_mode == SweepingMode.Feature:
                baseline_featurizer = self._build_featurizers(
                    enabled_sweeper_config._baseline,
                )  # type: Optional[Pipeline]
                experiment_featurizer = self._build_featurizers(
                    enabled_sweeper_config._experiment,
                )  # type: Optional[Pipeline]

                if baseline_featurizer is None or experiment_featurizer is None:
                    logger.debug("Excluding blocked transformer from sweeper")
                    continue

                include_baseline_features = True
                if enabled_sweeper_config._experiment:
                    include_baseline_features = enabled_sweeper_config._experiment. \
                        get(ConfigKeys.INCLUDE_BASELINE_FEATURES, True)

                scale_epsilon = True
                if hasattr(enabled_sweeper_config, "_scale_epsilon"):  # For compatibility.
                    scale_epsilon = enabled_sweeper_config._scale_epsilon

                kwargs = {"name": enabled_sweeper_config._name, "data_provider": data_provider, "estimator": estimator,
                          "scorer": scorer,
                          "baseline": baseline_featurizer, "experiment": experiment_featurizer,
                          "epsilon": enabled_sweeper_config._epsilon, "scale_epsilon": scale_epsilon,
                          "task": self._task,
                          "include_baseline_features_in_experiment": include_baseline_features}  # type: Dict[str, Any]
            else:
                kwargs = {"name": enabled_sweeper_config._name, "data_provider": data_provider, "estimator": estimator,
                          "scorer": scorer,
                          "epsilon": enabled_sweeper_config._epsilon, "task": self._task}

            sweeper = Sweepers.get(enabled_sweeper_config._type, **kwargs)  # type: Optional[AbstractSweeper]
            if sweeper:
                sweepers.append(sweeper)

        return sweepers

    def _remove_temporary_files(self) -> None:
        for file_name in self._temp_files_to_cleanup:
            try:
                os.remove(file_name)
            except IOError:
                pass

    @classmethod
    def _validate(cls, X: CoreDataInputType, y: CoreDataSingleColumnInputType) -> Tuple[bool, str]:
        if X is None or y is None:
            return False, "X or y cannot be None"

        if scipy.sparse.issparse(X):
            if X.shape[0] != len(y):
                return False, "Number of rows in X must be equal to the number of rows in y."
        elif len(X) != len(y):
            return False, "Number of rows in X must be equal to the number of rows in y."

        if len(np.unique(y)) == 1:
            return False, "Number of classes in y must be more than 1."

        return True, ''

    @classmethod
    def _build_sampler(cls, sampler_config: SamplerConfig, task: str) -> AbstractSampler:
        """
        Build sampler from the given sampler configuration.

        :param sampler_config: Sampler configuration.
        :param task: Task type.
        :return: Created sampler.
        """
        sampler_id = sampler_config.id
        sampler_args = sampler_config.sampler_args
        sampler_kwargs = sampler_config.sampler_kwargs
        sampler_kwargs["task"] = task

        sampler = Samplers.get(sampler_id, *sampler_args, **sampler_kwargs)
        return cast(AbstractSampler, sampler)

    def _build_featurizers(self, feature_config: Dict[str, Any]) -> Pipeline:
        feature_steps = feature_config.get(ConfigKeys.FEATURIZERS)
        if not isinstance(feature_steps, list):
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="feature_config",
                    argument_name="feature_config ({})".format(ConfigKeys.FEATURIZERS)
                )
            )
        steps = []

        for c in feature_steps:
            f_config = FeatureConfig.from_dict(c)
            featurizer = Featurizers.get(f_config, self._featurization_config)
            if featurizer is None:
                logger.debug("Excluding featurizer step with transformer: {0}.".format(f_config.id))
                return
            steps.append(featurizer)

        return make_pipeline(*steps)

    def _build_data_provider(self, X: CoreDataInputType, y: CoreDataSingleColumnInputType,
                             sampler: AbstractSampler,
                             working_dir: str,
                             include_columns: Optional[List[str]] = None,
                             group: Optional[Union[bool, str]] = None) -> DataProvider:
        if not include_columns:  # No particular columns specified, so sample dataset across all columns.
            data = sampler.sample(X, y)
        elif not group:  # Columns are individually tested, so we take individual samples.
            data = {col: sampler.sample(X, y, col) for col in include_columns}  # type: ignore
        else:
            # We featurize the columns together (group == 'featurize') or separately (group == 'score')
            # but score them together. With shared scoring, we want a single sample across the columns of interest.
            data = sampler.sample(X, y, include_columns)

        data_provider = None  # type: Optional[DataProvider]
        if self._page_sampled_data_to_disk:
            file_handle, dataset_file = tempfile.mkstemp(suffix=".ds", prefix="sampled_dataset_", dir=working_dir)
            self._temp_files_to_cleanup.append(dataset_file)

            with os.fdopen(file_handle, "wb") as f:
                pickle.dump(data, f)

            data_provider = DiskBasedDataProvider(dataset_file)
        else:
            data_provider = InMemoryDataProvider(data)

        return data_provider

    @staticmethod
    def _determine_columns_of_interest(sweeper_config: SweeperConfig,
                                       column_groups: Dict[str, List[str]]) -> Tuple[List[str], Union[bool, str]]:
        """
        Using provided sweeper config which contains the column purposes that this experiment will test
        and a mapping of purposes to input column names, return a list of the input columns of interest for
        this sweeping experiment. Currently only needed for feature sweeping, since class balance sweeping samples
        across all columns for the entire dataset.

        :param sweeper_config: The SweeperConfig object defining this experiment.
        :param column_groups: A dictionary of types and the associated column names for each type.
        :return: Tuple of (columns of interest, specifier for how to group the columns during the experiment).
        """
        columns_of_interest = []  # type: List[str]
        group = False  # type: Union[bool, str]
        for purpose in sweeper_config._column_purposes:
            group = purpose.get("group", False)
            for t in purpose.get("types", []):
                columns_of_interest.extend(column_groups.get(t.lower(), []))
        return columns_of_interest, group
