# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains functionality for building pipelines using AutoML for advanced model building.
"""
from typing import Any, Dict, List, Optional, Tuple, Union
import json
import os
import shutil
import sys

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AllowedModelsNonExplainable
from azureml.automl.core.shared.constants import _NonExplainableModels
from azureml.automl.core.shared.exceptions import ConfigException
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.core import ComputeTarget, Dataset, Datastore, Experiment, Run, RunConfiguration
from azureml.core.environment import Environment
from azureml.data import FileDataset, TabularDataset
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.automl.core.console_writer import ConsoleWriter
from azureml.train.automl.constants import HTSConstants, HTSSupportedInputType, AutoMLPipelineScenario
from azureml.train.automl._hts import hts_client_utilities
from azureml.pipeline.core import PipelineData, PipelineParameter, PipelineRun, PipelineStep
from azureml.pipeline.core._python_script_step_base import _HTSStepConstants
from azureml.pipeline.steps import ParallelRunConfig, ParallelRunStep, PythonScriptStep
from azureml.train.automl.runtime._many_models.many_models_input_dataset import ManyModelsInputDataset
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru

from . import utilities
from ._assets import (
    partition_training_dataset_wrapper, partition_inference_dataset_wrapper, hierarchy_builder_wrapper,
    data_aggregation_and_validation_wrapper, automl_training_wrapper, automl_forecast_wrapper,
    proportions_calculation_wrapper, allocation_explanation_wrapper, allocation_wrapper)


@experimental
class _HTSPipelineBuilder(object):
    """
    Pipeline builder class.

    This class is used to build pipelines for AutoML training utilizing advanced modeling
    techniques including many models and hierarchical time series.
    """

    _ASSETS_LOCATION = "_assets"
    _PROJECT_FOLDER = "automl_pipeline_project"
    AVERAGE_HISTORICAL_PROPORTIONS = HTSConstants.AVERAGE_HISTORICAL_PROPORTIONS
    PROPORTIONS_OF_HISTORICAL_AVERAGE = HTSConstants.PROPORTIONS_OF_HISTORICAL_AVERAGE

    SCRIPT_TRAINING_DATASET_PARTITION = utilities.get_module_file_abs_path(partition_training_dataset_wrapper)
    SCRIPT_HIERARCHY_BUILDER = utilities.get_module_file_abs_path(hierarchy_builder_wrapper)
    SCRIPT_DATA_AGG = utilities.get_module_file_abs_path(data_aggregation_and_validation_wrapper)
    SCRIPT_AUTOML_TRAINING = utilities.get_module_file_abs_path(automl_training_wrapper)
    SCRIPT_PROPORTIONS_CALCULATION = utilities.get_module_file_abs_path(proportions_calculation_wrapper)
    SCRIPT_AUTOML_FORECAST_WRAPPER = utilities.get_module_file_abs_path(automl_forecast_wrapper)
    SCRIPT_INFERENCE_DATASET_PARTITION = utilities.get_module_file_abs_path(partition_inference_dataset_wrapper)
    SCRIPT_ALLOCATION_WRAPPER = utilities.get_module_file_abs_path(allocation_wrapper)
    SCRIPT_EXPLANATION_WRAPPER = utilities.get_module_file_abs_path(allocation_explanation_wrapper)

    STEP_NAME_ADDITIONAL_ARGUMENTS = {
        _HTSStepConstants.HTS_TRAINING_DATASET_PARTITION: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_HIERARCHY_BUILDER: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_DATA_AGGREGATION: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_AUTOML_TRAINING: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_PROPORTIONS: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_FORECAST: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_INFERENCE_DATASET_PARTITION: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_EXPLAIN_ALLOCATION: {HTSConstants.ENABLE_EVENT_LOGGER},
        _HTSStepConstants.HTS_ALLOCATION: {HTSConstants.ENABLE_EVENT_LOGGER},
    }

    _CONSOLE_WRITER = ConsoleWriter(sys.stdout)

    @staticmethod
    def get_hierarchy_train_steps(
        experiment: Experiment,
        train_data: Union[FileDataset, TabularDataset, DatasetConsumptionConfig],
        compute_target: ComputeTarget,
        node_count: int,
        train_env: Environment,
        process_count_per_node: int = 2,
        run_invocation_timeout: int = 3600,
        output_datastore: Optional[Datastore] = None,
        automl_settings: Optional[Dict[str, Any]] = None,
        enable_engineered_explanations: bool = False,
        arguments: Optional[List[Union[str, int]]] = None
    ) -> List[PipelineStep]:
        """
        Get the pipeline steps hierarchical for training.

        This method will build a list of steps to be used for training hierarchical time series.
        The training uses AutoML to create and register one model per group in the hierarchy.

        :param experiment: The experiment from which the PiplineSteps will be submitted.
        :param training_data: The data to be used for training.
        :param compute_target: The compute target name or compute target to be used by the pipeline's steps.
        :param node_count: The number of nodes to be used by the pipeline steps when work is
            distributable. This should be less than or equal to the max_nodes of the compute target
            if using amlcompute.
        :param process_count_per_node: The number of processes to use per node when the work is
            distributable. This should be less than or equal to the number of cores of the
            compute target.
        :param run_invocation_timeout: The maximum time to spend on distributable portions of the run.
            If a step times out the run will not proceed.
        :param train_env: The env used for train the HTS pipeline.
        :param output_datastore: The datastore to be used for output. If specified any pipeline
            output will be written to that location. If unspecified the default datastore will be used.
        :param automl_settings: The settings to be used to construct AutoMLConfig object.
        :param enable_engineered_explanations: If True, the engineered feature explanations will be generated.
        :param arguments: The additional arguments that will be passed to each step.
        :returns: A list of steps which will preprocess data to the desired training_level (as set in
            the automl_settings) and train and register automl models.
        """
        os.makedirs(_HTSPipelineBuilder._PROJECT_FOLDER, exist_ok=True)
        # Validate that we did will not block all models if explainability is desirable.
        allowed_models = automl_settings.get('allowed_models')
        if automl_settings.get('model_explainability', True) and allowed_models is not None:
            explainable_allowed_models = set(allowed_models) - set(_NonExplainableModels.FORECASTING)
            if not explainable_allowed_models:
                raise ConfigException._with_error(
                    AzureMLError.create(AllowedModelsNonExplainable,
                                        non_explainable_models=_NonExplainableModels.FORECASTING,
                                        reference_code=ReferenceCodes._HTS_NO_EXPLAINABLE_MODELS_ALLOWED,
                                        target='allowed_models'))
        workspace = experiment.workspace

        hts_client_utilities.validate_settings(automl_settings)
        _HTSPipelineBuilder._dump_settings(automl_settings)

        run_config = _HTSPipelineBuilder._get_run_config(train_env)

        mini_batch_size = PipelineParameter(name="batch_size_param", default_value=str(1))
        process_count_per_node = PipelineParameter(name="process_count_param", default_value=process_count_per_node)

        steps = []

        hierarchy_builder_output = PipelineData("hts_graph", datastore=output_datastore)

        hts_input = ManyModelsInputDataset.from_input_data(
            train_data, partition_column_names=hts_client_utilities.get_hierarchy(automl_settings),
            input_dataset_name=HTSConstants.HTS_INPUT, use_train_level=True)
        _HTSPipelineBuilder._copy_wrapper_files(hts_input, True)

        if hts_input.is_partition_step_needed:
            steps.append(
                _HTSPipelineBuilder._build_dataset_partition_step(
                    compute_target, run_config, hts_input, source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
                    is_training=True, arguments=arguments))

        steps.append(
            _HTSPipelineBuilder._build_hierarchy_builder_step(
                hts_input, compute_target, run_config, hierarchy_builder_output, arguments))

        # data aggregation only support file dataset and tabular dataset with partitions
        agg_metadata = PipelineData("data_aggregation_and_validation", datastore=output_datastore)
        hts_input.create_file_dataset(workspace, output_datastore, _HTSPipelineBuilder._CONSOLE_WRITER)
        steps.append(
            _HTSPipelineBuilder._build_data_agg_step(
                hts_input, compute_target, mini_batch_size, automl_settings, process_count_per_node,
                run_invocation_timeout, node_count, agg_metadata, hierarchy_builder_output,
                train_env, arguments))

        training_metadata = PipelineData("automl_training", datastore=output_datastore)
        automl_train_arguments = [
            HTSConstants.OUTPUT_PATH, training_metadata,
            HTSConstants.METADATA_INPUT, agg_metadata,
            HTSConstants.HTS_GRAPH, hierarchy_builder_output,
            HTSConstants.ENGINEERED_EXPLANATION, enable_engineered_explanations,
            HTSConstants.NODES_COUNT, node_count]
        automl_train_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            _HTSStepConstants.HTS_AUTOML_TRAINING, arguments
        ))
        automl_train_parallel_run_config = ParallelRunConfig(
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            entry_script=_HTSPipelineBuilder.SCRIPT_AUTOML_TRAINING.name,
            mini_batch_size=mini_batch_size,
            error_threshold=-1,
            output_action="append_row",
            append_row_file_name="outputs.txt",
            compute_target=compute_target,
            environment=train_env,
            process_count_per_node=process_count_per_node,
            run_invocation_timeout=run_invocation_timeout,
            node_count=node_count)

        automl_train_prs = ParallelRunStep(
            name=_HTSStepConstants.HTS_AUTOML_TRAINING,
            parallel_run_config=automl_train_parallel_run_config,
            arguments=automl_train_arguments,
            inputs=[hts_input.agg_file_dataset.as_named_input('aggregated_hierarchy_level_data')],
            output=training_metadata,
            side_inputs=[agg_metadata, hierarchy_builder_output],
            allow_reuse=False
        )
        steps.append(automl_train_prs)

        proportions_calculation = PipelineData("proportions_calculation", datastore=output_datastore)
        prop_calc_arguments = [
            HTSConstants.METADATA_INPUT, training_metadata,
            HTSConstants.HTS_GRAPH, hierarchy_builder_output]
        prop_calc_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            _HTSStepConstants.HTS_PROPORTIONS, arguments
        ))
        prop_calc_pss = PythonScriptStep(
            name=_HTSStepConstants.HTS_PROPORTIONS,
            script_name=_HTSPipelineBuilder.SCRIPT_PROPORTIONS_CALCULATION.name,
            compute_target=compute_target,
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            inputs=[training_metadata, hierarchy_builder_output],
            arguments=prop_calc_arguments,
            outputs=[proportions_calculation],
            runconfig=run_config,
            allow_reuse=False
        )

        steps.append(prop_calc_pss)

        if automl_settings.get('model_explainability', True):
            steps.append(_HTSPipelineBuilder._build_explain_allocation_step(
                training_metadata,
                hierarchy_builder_output,
                compute_target=compute_target,
                runconfig=run_config,
                output_datastore=output_datastore,
                training_datastore=output_datastore,
                enable_engineered_explanations=enable_engineered_explanations))

        return steps

    @staticmethod
    def get_hierarchy_inference_steps(
        experiment: Experiment,
        inference_data: Union[TabularDataset, FileDataset, DatasetConsumptionConfig],
        hierarchy_forecast_level: str,
        compute_target: Union[str, ComputeTarget],
        node_count: int,
        process_count_per_node: int = 2,
        run_invocation_timeout: int = 600,
        allocation_method: str = PROPORTIONS_OF_HISTORICAL_AVERAGE,
        train_experiment_name: Optional[str] = None,
        training_run_id: Optional[str] = None,
        output_datastore: Optional[Datastore] = None,
        inference_env: Optional[Environment] = None,
        arguments: Optional[List[Union[str, int]]] = None
    ) -> List[PipelineStep]:
        """
        Get the pipeline steps hierarchical for inferencing.

        This method should be used in conjunction with get_hierarchy_training_steps. This method
        will build an inference pipeline which can be used to coherently allocate forecasts
        from models trained through automl hierarchical time series training pipelines.

        :param experiment: The inference experiment.
        :param training_run_id: The pipeline run id which was used to train automl models. If this parameter is None.
            the latest successful training run will be used.
        :param train_experiment_name: The experiment name which the training_run lives.
        :param inference_data: The data to be used for inferencing.
        :param hierarchy_forecast_level: The default level to be used for inferencing. The pipeline
            will first aggregate data to the selected training level and then allocate forecasts to
            the desired forecast level. This can be modified on the pipeline through the
            PipelineParameter of the same name.
        :param allocation_method: The allocation method to be used for inferencing. This method will be
            used if the hierarchy_forecast_level is different from the training_level. This can be
            modified through the PipelineParameter of the same name.
        :param compute_target: The compute target name or compute target to be used by the pipeline's steps.
        :param node_count: The number of nodes to be used by the pipeline steps when work is
            distributable. This should be less than or equal to the max_nodes of the compute target
            if using amlcompute.
        :param process_count_per_node: The number of processes to use per node when the work is
            distributable. This should be less than or equal to the number of cores of the
            compute target.
        :param run_invocation_timeout: The maximum time to spend on distributable portions of the run.
            If a step times out the run will not proceed.
        :param output_datastore: The datastore to be used for output. If specified any pipeline
            output will be written to that location. If unspecified the default datastore will be used.
        :param inference_env: The inference environment.
        :param arguments: The additional arguments that will be passed to each step.
        :returns: A list of steps which will preprocess data to the desired training_level (as set in
            the automl_settings) and train and register automl models.
        """
        os.makedirs(_HTSPipelineBuilder._PROJECT_FOLDER, exist_ok=True)

        if train_experiment_name is None:
            training_experiment = experiment
            train_experiment_name = experiment.name
        else:
            training_experiment = Experiment(experiment.workspace, train_experiment_name)

        if training_run_id is None:
            training_run = hts_client_utilities.get_latest_successful_training_run(training_experiment)
            training_run_id = training_run.id
            _HTSPipelineBuilder._CONSOLE_WRITER.println(
                "The training run used for inference is {}.".format(training_run_id))
        else:
            training_run = PipelineRun(training_experiment, training_run_id)

        if inference_env is None:
            inference_env = utilities.get_default_inference_env(
                experiment, training_run_id, train_experiment_name, _HTSStepConstants.HTS_AUTOML_TRAINING
            )

        run_config = _HTSPipelineBuilder._get_run_config(inference_env)

        forecast_param = PipelineParameter(name="hierarchy_forecast_level", default_value=hierarchy_forecast_level)
        allocation_param = PipelineParameter(name="allocation_method", default_value=allocation_method)

        steps = []

        settings = json.loads(training_run.properties[HTSConstants.HTS_PROPERTIES_SETTINGS])
        _HTSPipelineBuilder._dump_settings(settings)
        partition_keys = hts_client_utilities.get_hierarchy_to_training_level(settings)
        hts_input = ManyModelsInputDataset.from_input_data(inference_data, partition_keys, HTSConstants.HTS_INPUT)

        _HTSPipelineBuilder._copy_wrapper_files(hts_input, False)
        if hts_input.is_partition_step_needed:
            steps.append(
                _HTSPipelineBuilder._build_dataset_partition_step(
                    compute_target, run_config, hts_input, source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
                    is_training=False, training_run_id=training_run_id))

        datastore, output_allocations = utilities.get_output_datastore_and_file(
            output_datastore, "allocated_forecasts", pipeline_output_name="forecasts")
        output_forecasts = PipelineData(
            name="raw_forecasts", datastore=datastore, pipeline_output_name="raw_forecasts")

        steps.append(
            _HTSPipelineBuilder._build_forecast_parallel_step(
                hts_input, inference_env, compute_target, node_count,
                process_count_per_node,
                run_invocation_timeout, training_run_id, output_forecasts, partition_keys))

        inf_allocation = PythonScriptStep(
            name=_HTSStepConstants.HTS_ALLOCATION,
            script_name=_HTSPipelineBuilder.SCRIPT_ALLOCATION_WRAPPER.name,
            inputs=[output_forecasts.as_mount()],
            outputs=[output_allocations],
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            arguments=[
                HTSConstants.TRAINING_RUN_ID, training_run_id,
                HTSConstants.OUTPUT_PATH, output_allocations,
                HTSConstants.ALLOCATION_METHOD, allocation_param,
                HTSConstants.FORECAST_LEVEL, forecast_param,
                HTSConstants.RAW_FORECASTS, output_forecasts,
            ],
            runconfig=run_config,
            compute_target=compute_target,
            allow_reuse=False
        )
        steps.append(inf_allocation)

        return steps

    @staticmethod
    def get_training_step(pipeline_run: PipelineRun) -> Optional[Run]:
        """
        Get the AutoML training step.

        This can be used to get the automl training step to check how many groups
        are left to train. A link to the step will also be printed. If the step is
        not found, None will be returned.

        :param pipeline_run: The PipelineRun object containing an automl training step.
        """
        step_list = pipeline_run.find_step_run("automl-training")
        if not step_list:
            _HTSPipelineBuilder._CONSOLE_WRITER.println(
                "No AutoML Training run found. This could be because the pipeline has not started training.")
            return None
        at = step_list[0]
        _HTSPipelineBuilder._CONSOLE_WRITER.println(
            "View the AutoML training run here: {}".format(at.get_portal_url()))
        return at

    @staticmethod
    def get_training_step_status(pipeline_run: PipelineRun) -> Tuple[Optional[int], Optional[int]]:
        """
        Get the number of AutoML Training jobs remaining on the run.

        Returns a tuple of reminaing_items, total_items. If the AutoML training step is not found,
        None, None is returned. If there is a problem getting remaning job count or total job
        count None will be returned for the respective number.

        :param pipeline_run: The PipelineRun object containing the automl training step.
        """
        at = _HTSPipelineBuilder.get_training_step(pipeline_run)
        if at is None:
            return None, None
        remaining_items_list = at.get_metrics("Remaining Items").get("Remaining Items", [])
        total_items = at.get_metrics("Total MiniBatches").get("Total MiniBatches")
        if not remaining_items_list:
            _HTSPipelineBuilder._CONSOLE_WRITER.println("Could not retrieve remaining items.")
            remaining_items = None
        else:
            remaining_items = remaining_items_list[-1]

        if not total_items:
            _HTSPipelineBuilder._CONSOLE_WRITER.println("Could not retrieve total items.")

        if total_items and remaining_items:
            _HTSPipelineBuilder._CONSOLE_WRITER.println(
                "{} out of {} jobs remaining".format(remaining_items, total_items))

        return remaining_items, total_items

    @staticmethod
    def _copy_wrapper_files(mm_input: ManyModelsInputDataset, is_training: bool) -> None:
        """Copy the wrapper file according to dataset type and run type"""
        if is_training:
            if not mm_input.is_partition_step_needed:
                files_to_copy = [_HTSPipelineBuilder.SCRIPT_HIERARCHY_BUILDER]
            else:
                files_to_copy = [
                    _HTSPipelineBuilder.SCRIPT_TRAINING_DATASET_PARTITION,
                    _HTSPipelineBuilder.SCRIPT_HIERARCHY_BUILDER]
            files_to_copy.append(_HTSPipelineBuilder.SCRIPT_DATA_AGG)
            files_to_copy.append(_HTSPipelineBuilder.SCRIPT_AUTOML_TRAINING)
            files_to_copy.append(_HTSPipelineBuilder.SCRIPT_PROPORTIONS_CALCULATION)
            files_to_copy.append(_HTSPipelineBuilder.SCRIPT_EXPLANATION_WRAPPER)
        else:
            if not mm_input.is_partition_step_needed:
                files_to_copy = []
            else:
                files_to_copy = [_HTSPipelineBuilder.SCRIPT_INFERENCE_DATASET_PARTITION]
            files_to_copy.append(_HTSPipelineBuilder.SCRIPT_AUTOML_FORECAST_WRAPPER)
            files_to_copy.append(_HTSPipelineBuilder.SCRIPT_ALLOCATION_WRAPPER)

        for f in files_to_copy:
            shutil.copy(f, _HTSPipelineBuilder._PROJECT_FOLDER)

    @staticmethod
    def _build_dataset_partition_step(
            compute_target: Union[str, ComputeTarget],
            run_config: RunConfiguration,
            mm_input: ManyModelsInputDataset,
            is_training: bool,
            source_directory: str,
            training_run_id: Optional[str] = HTSConstants.DEFAULT_ARG_VALUE,
            arguments: Optional[List[Union[str, int]]] = None,
            pipeline_scenario: str = AutoMLPipelineScenario.HTS,
    ) -> PythonScriptStep:
        """Build dataset partition step."""
        if is_training:
            step_name = _HTSStepConstants.HTS_TRAINING_DATASET_PARTITION
            script_name = _HTSPipelineBuilder.SCRIPT_TRAINING_DATASET_PARTITION.name
            pipeline_type = "training"
        else:
            step_name = _HTSStepConstants.HTS_INFERENCE_DATASET_PARTITION
            script_name = _HTSPipelineBuilder.SCRIPT_INFERENCE_DATASET_PARTITION.name
            pipeline_type = "inference"
        # step_name needs to be different from the one HTS use to avoid the run type get changed
        if pipeline_scenario == AutoMLPipelineScenario.MANY_MODELS:
            step_name = "mm-data-partition"
        _HTSPipelineBuilder._CONSOLE_WRITER.println(
            "A partitioned tabular dataset will be created with the name {} after {}. "
            "You may use it for future {}.".format(
                pipeline_type, mm_input.partitioned_dataset_name, pipeline_type))
        step_arguments = [
            HTSConstants.PARTITIONED_DATASET_NAME, mm_input.partitioned_dataset_name,
            HTSConstants.TRAINING_RUN_ID, training_run_id,
            HTSConstants.INPUT_DATA_NAME, mm_input.dataset_consumption_config.name,
            HTSConstants.PIPELINE_SCENARIO, pipeline_scenario
        ]
        step_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            step_name, arguments
        ))
        partition_step = PythonScriptStep(
            name=step_name,
            script_name=script_name,
            compute_target=compute_target,
            source_directory=source_directory,
            inputs=[mm_input.partition_step_input],
            outputs=[mm_input.link_partition_output_config],
            arguments=step_arguments,
            runconfig=run_config,
            allow_reuse=False
        )
        return partition_step

    @staticmethod
    def _build_hierarchy_builder_step(
            hts_input: ManyModelsInputDataset,
            compute_target: Union[str, ComputeTarget],
            run_config: RunConfiguration,
            hierarchy_builder_output: str,
            arguments: Optional[List[Union[str, int]]] = None
    ) -> PythonScriptStep:
        """Build hierarchy builder step."""
        outputs = [hierarchy_builder_output]
        if hts_input.input_dataset_type == HTSSupportedInputType.FILE_DATASET:
            step_arguments = [
                HTSConstants.OUTPUT_PATH, hierarchy_builder_output,
                HTSConstants.BLOB_PATH, hts_input.training_level_dataset,
            ]
            outputs.append(hts_input.training_level_dataset)
        else:
            step_arguments = [
                HTSConstants.OUTPUT_PATH, hierarchy_builder_output,
                HTSConstants.BLOB_PATH, HTSConstants.DEFAULT_ARG_VALUE,
                HTSConstants.INPUT_DATA_NAME, hts_input.python_script_partitioned_input.name
            ]

        step_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            _HTSStepConstants.HTS_HIERARCHY_BUILDER, arguments
        ))

        hierarchy_builder_step = PythonScriptStep(
            name=_HTSStepConstants.HTS_HIERARCHY_BUILDER,
            script_name=_HTSPipelineBuilder.SCRIPT_HIERARCHY_BUILDER.name,
            compute_target=compute_target,
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            inputs=[hts_input.python_script_partitioned_input],
            arguments=step_arguments,
            outputs=outputs,
            runconfig=run_config,
            allow_reuse=False
        )

        return hierarchy_builder_step

    @staticmethod
    def _build_data_agg_step(
            hts_input: ManyModelsInputDataset,
            compute_target: Union[str, ComputeTarget],
            mini_batch_size: PipelineParameter,
            automl_settings: Dict[str, Any],
            process_count_per_node: PipelineParameter,
            run_invocation_timeout: int,
            node_count: int,
            agg_metadata: str,
            hierarchy_builder_output: str,
            train_env: Environment,
            arguments: Optional[List[Union[str, int]]] = None
    ) -> ParallelRunStep:
        """Build data aggregation step."""
        prs_config = _HTSPipelineBuilder._get_prs_config(
            mm_input_data=hts_input,
            partition_keys=hts_client_utilities.get_hierarchy_to_training_level(automl_settings),
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            entry_script=_HTSPipelineBuilder.SCRIPT_DATA_AGG.name,
            compute_target=compute_target,
            node_count=node_count,
            process_count_per_node=process_count_per_node,
            run_invocation_timeout=run_invocation_timeout,
            environment=train_env,
            error_threshold=10,
            append_row_file_name="outputs.txt"
        )

        input_datasets = [hts_input.prs_input]

        step_arguments = [HTSConstants.OUTPUT_PATH, agg_metadata,
                          HTSConstants.BLOB_PATH, hts_input.agg_blob_dir,
                          HTSConstants.HTS_GRAPH, hierarchy_builder_output,
                          HTSConstants.NODES_COUNT, node_count]
        step_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            _HTSStepConstants.HTS_DATA_AGGREGATION, arguments
        ))

        agg_data_prs = ParallelRunStep(
            name=_HTSStepConstants.HTS_DATA_AGGREGATION,
            parallel_run_config=prs_config,
            arguments=step_arguments,
            inputs=input_datasets,
            output=agg_metadata,
            side_inputs=[hierarchy_builder_output],
            allow_reuse=False
        )

        return agg_data_prs

    @staticmethod
    def _build_forecast_parallel_step(
            hts_input: ManyModelsInputDataset,
            environment: Experiment,
            compute_target: Union[str, ComputeTarget],
            node_count: int,
            process_count_per_node: PipelineParameter,
            run_invocation_timeout: int,
            training_run_id: str,
            output_forecasts: str,
            partition_keys: Optional[str] = None,
            arguments: Optional[List[Union[str, int]]] = None
    ) -> ParallelRunStep:
        """Build forecast parallel step."""
        inf_prc = _HTSPipelineBuilder._get_prs_config(
            mm_input_data=hts_input,
            partition_keys=partition_keys,
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            entry_script=_HTSPipelineBuilder.SCRIPT_AUTOML_FORECAST_WRAPPER.name,
            compute_target=compute_target,
            node_count=node_count,
            process_count_per_node=process_count_per_node,
            run_invocation_timeout=run_invocation_timeout,
            environment=environment,
            append_row_file_name=HTSConstants.HTS_FILE_RAW_PREDICTIONS,
            description="forecast-parallel-config",
            run_max_try=3
        )
        inputs = [hts_input.prs_input]

        step_arguments = [
            HTSConstants.TRAINING_RUN_ID, training_run_id,
            HTSConstants.OUTPUT_PATH, output_forecasts,
            HTSConstants.APPEND_HEADER_PRS, True,
            HTSConstants.NODES_COUNT, node_count,
        ]
        step_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            _HTSStepConstants.HTS_FORECAST, arguments
        ))

        inf_prs = ParallelRunStep(
            name=_HTSStepConstants.HTS_FORECAST,
            inputs=inputs,
            arguments=step_arguments,
            output=output_forecasts,
            parallel_run_config=inf_prc,
            allow_reuse=False
        )

        return inf_prs

    @staticmethod
    def _build_explain_allocation_step(
            training_metadata: PipelineData,
            hierarchy_builder_output: PipelineData,
            compute_target: Union[str, ComputeTarget],
            runconfig: RunConfiguration,
            output_datastore: Dataset,
            training_datastore: Dataset,
            enable_engineered_explanations: bool,
            arguments: Optional[List[Union[str, int]]] = None
    ) -> PythonScriptStep:
        """
        Build The step for allocation of explanations.

        :param training_metadata: The metadata obtained from the training step.
        :param compute_target: The compute target to be used for allocation.
        :param output_datastore: The data store used to output the explanations.
        :param training_datastore: The data store used by a training step.
        :return: The explanation step.
        """
        output_explanations = PipelineData(
            name=HTSConstants.HTS_EXPLANATIONS_OUT,
            datastore=output_datastore,
            pipeline_output_name=HTSConstants.HTS_DIR_EXPLANATIONS)

        step_arguments = [
            HTSConstants.EXPLANATION_DIR, training_metadata,
            HTSConstants.HTS_GRAPH, hierarchy_builder_output,
            HTSConstants.ENGINEERED_EXPLANATION, enable_engineered_explanations,
            HTSConstants.OUTPUT_PATH, output_explanations,
        ]
        step_arguments.extend(_HTSPipelineBuilder._get_additional_step_arguments(
            _HTSStepConstants.HTS_EXPLAIN_ALLOCATION, arguments
        ))

        return PythonScriptStep(
            name=_HTSStepConstants.HTS_EXPLAIN_ALLOCATION,
            script_name=_HTSPipelineBuilder.SCRIPT_EXPLANATION_WRAPPER.name,
            outputs=[output_explanations],
            source_directory=_HTSPipelineBuilder._PROJECT_FOLDER,
            inputs=[training_metadata, hierarchy_builder_output],
            arguments=step_arguments,
            compute_target=compute_target,
            runconfig=runconfig,
            allow_reuse=False
        )

    @staticmethod
    def _dump_settings(automl_settings: Dict[str, Any]) -> None:
        """Dump the settings to a json file in the project folder."""
        settings_path = os.path.join(_HTSPipelineBuilder._PROJECT_FOLDER, HTSConstants.SETTINGS_FILE)
        hru.dump_object_to_json(automl_settings, settings_path)

    @staticmethod
    def _get_additional_step_arguments(
            step_name: str, arguments: Optional[List[Union[str, int]]] = None
    ) -> List[Union[str, int]]:
        """Get additional step arguments from input arguments."""
        filtered_args = []
        if not arguments:
            return filtered_args

        for i, arg in enumerate(arguments):
            if arg in _HTSPipelineBuilder.STEP_NAME_ADDITIONAL_ARGUMENTS[step_name]:
                if i < len(arguments) - 1:
                    filtered_args.append(arg)
                    filtered_args.append(arguments[i + 1])
                else:
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            ArgumentBlankOrEmpty,
                            argument_name=arg,
                            reference_code=ReferenceCodes._HTS_NO_ARGUMENT_PROVIDED,
                            target='arguments'))

        return filtered_args

    @staticmethod
    def _get_prs_config(
            mm_input_data: ManyModelsInputDataset,
            partition_keys: Optional[List[str]],
            source_directory: str,
            entry_script: str,
            compute_target: ComputeTarget,
            node_count: int,
            process_count_per_node: int,
            run_invocation_timeout: int,
            environment: Environment,
            error_threshold: int = -1,
            append_row_file_name: Optional[str] = None,
            description: Optional[str] = None,
            run_max_try: Optional[int] = None,
    ) -> ParallelRunConfig:
        """Get the config for the PRS step."""
        output_action = "append_row"
        if mm_input_data.input_dataset_type == HTSSupportedInputType.FILE_DATASET:
            partition_keys = None
            mini_batch_size = 1
        else:
            mini_batch_size = None
            error_threshold = -1

        parallel_run_config = ParallelRunConfig(
            source_directory=source_directory,
            entry_script=entry_script,
            partition_keys=partition_keys,
            run_invocation_timeout=run_invocation_timeout,
            error_threshold=error_threshold,
            output_action=output_action,
            environment=environment,
            process_count_per_node=process_count_per_node,
            mini_batch_size=mini_batch_size,
            compute_target=compute_target,
            append_row_file_name=append_row_file_name,
            description=description,
            node_count=node_count,
            run_max_try=run_max_try,
        )

        return parallel_run_config

    @staticmethod
    def _get_dataset_consumption_config(
            train_data: Union[TabularDataset, FileDataset, DatasetConsumptionConfig, PipelineData],
            dataset_name: str
    ) -> DatasetConsumptionConfig:
        """Convert dataset to DatasetConsumptionConfig."""
        if isinstance(train_data, DatasetConsumptionConfig):
            return train_data
        else:
            return DatasetConsumptionConfig(dataset_name, train_data)

    @staticmethod
    def _get_run_config(env: Environment) -> RunConfiguration:
        """Get the run config for step run."""
        run_config = RunConfiguration()
        run_config.docker.use_docker = True
        run_config.environment = env
        return run_config
