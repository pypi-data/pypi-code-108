__all__ = [
    'fetch_pipelines',
    'load_file_from_file_system',
    'load_file_from_file_system_nonautoai',
    'NextRunDetailsGenerator',
    'prepare_auto_ai_model_to_publish_normal_scenario',
    'prepare_auto_ai_model_to_publish_notebook_normal_scenario',
    'prepare_auto_ai_model_to_publish',
    'remove_file',
    'ProgressGenerator',
    'is_ipython',
    'try_import_lale',
    'try_load_dataset',
    'check_dependencies_versions',
    'try_import_autoai_libs',
    'try_import_autoai_ts_libs',
    'try_import_tqdm',
    'try_import_xlrd',
    'try_import_graphviz',
    'prepare_cos_client',
    'create_model_download_link',
    'create_summary',
    'prepare_auto_ai_model_to_publish_notebook',
    'get_node_and_runtime_index',
    'download_experiment_details_from_file',
    'prepare_model_location_path',
    'download_wml_pipeline_details_from_file',
    'init_cos_client',
    'check_graphviz_binaries',
    'try_import_joblib',
    'get_sw_spec_and_type_based_on_sklearn',
    'validate_additional_params_for_optimizer',
    'is_list_composed_from_enum',
    'validate_optimizer_enum_values',
    'all_logging_disabled',
    'check_if_ts_pipeline_is_winner',
    'get_values_for_imputation_strategy',
    'translate_imputation_string_strategy_to_enum'
]

#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import io
import json
import os
import enum
import gzip
import inspect
import re
from contextlib import redirect_stdout
from functools import wraps
from subprocess import check_call
from sys import executable
from tarfile import open as open_tar
from typing import Dict, Union, Tuple, List, TYPE_CHECKING, Optional, Any
from warnings import warn
from zipfile import ZipFile
from contextlib import contextmanager
import logging
from collections.abc import Sequence

import pkg_resources
import ibm_watson_machine_learning._wrappers.requests as requests
from packaging import version

from .enums import (RegressionAlgorithms, RegressionAlgorithmsCP4D, ClassificationAlgorithms,
                    ClassificationAlgorithmsCP4D, ForecastingAlgorithms, ForecastingAlgorithmsCP4D, Transformers,
                    Metrics, TShirtSize, PredictionType, DataConnectionTypes, ImputationStrategy)
from .errors import (MissingPipeline, DataFormatNotSupported, LibraryNotCompatible,
                     CannotInstallLibrary, CannotDownloadTrainingDetails, CannotDownloadWMLPipelineDetails,
                     VisualizationFailed, AdditionalParameterIsUnexpected, InvalidSequenceValue, NoAvailableMetrics,
                     DiscardedModel, WrongModelName, StrategyIsNotApplicable, InconsistentImputationListElements)

if TYPE_CHECKING:
    from io import BytesIO, BufferedIOBase
    from pandas import DataFrame
    from collections import OrderedDict
    from sklearn.pipeline import Pipeline
    from ibm_watson_machine_learning import APIClient
    from ibm_watson_machine_learning.helpers import DataConnection, S3Connection
    from ibm_boto3 import resource, client


def create_model_download_link(file_path: str):
    """
    Creates download link and shows it in the jupyter notebook

    Parameters
    ----------
    file_path: str, required
    """
    if is_ipython():
        from IPython.display import display
        from ibm_watson_machine_learning.utils import create_download_link
        display(create_download_link(file_path))


def fetch_pipelines(run_params: dict,
                    path: str,
                    wml_client: 'APIClient',
                    pipeline_name: str = None,
                    load_pipelines: bool = False,
                    store: bool = False) -> Tuple[Union[None, Dict[str, 'Pipeline']], bool]:
    """
    Helper function to download and load computed AutoAI pipelines (sklearn pipelines).

    Parameters
    ----------
    run_params: dict, required
        Fetched details of the run/fit.

    path: str, required
        Local system path indicates where to store downloaded pipelines.

    pipeline_name: str, optional
        Name of the pipeline to download, if not specified, all pipelines are downloaded.

    load_pipelines: bool, optional
        Indicator if we load and return downloaded piepelines.

    store: bool, optional
        Indicator to store pipelines in local filesystem

    wml_client: APIClient, required

    Returns
    -------
    List of sklearn Pipelines or None if load_pipelines is set to False.
    """

    def check_pipeline_nodes(pipeline: dict, request_json: dict, wml_client) -> bool:
        """
        Automate check all pipeline nodes to find xgboost or lightgbm dependency.
        """
        snapml_estimators = [i.value for i in ClassificationAlgorithms if 'Snap' in i.value] + [
            i.value for i in RegressionAlgorithms if 'Snap' in i.value]
        xgboost_estimators = ['XGBClassifierEstimator', 'XGBRegressorEstimator', 'XGBClassifier', 'XGBRegressor']
        lightgbm_estimators = ['LGBMClassifierEstimator', 'LGBMRegressorEstimator', 'LGBMClassifier', 'LGBMRegressor']

        # note: check dependencies for estimators and other packages
        estimator_name = pipeline['context']['intermediate_model'].get('pipeline_nodes', [None])[-1]
        if estimator_name in xgboost_estimators:
            check_lale = check_dependencies_versions(request_json, wml_client, 'xgboost')

        elif estimator_name in lightgbm_estimators:
            check_lale = check_dependencies_versions(request_json, wml_client, 'lightgbm')

        elif estimator_name in snapml_estimators:
            check_lale = check_dependencies_versions(request_json, wml_client, 'snapml')
        else:
            check_lale = check_dependencies_versions(request_json, wml_client, None)

        # TODO: When another package estimators will be available update above!
        # --- end note

        return check_lale

    joblib = try_import_joblib()

    path = os.path.abspath(path)
    pipelines_names = []
    pipelines = {}
    check_lale = True
    is_ts_metrics = 'timeseries' in run_params['entity']['status'].get('metrics', [None])[0]['context']

    if wml_client.ICP:
        model_paths = []

        # note: iterate over all computed pipelines
        for pipeline in run_params['entity']['status'].get('metrics', []):

            # note: fetch and create model paths from file system
            model_path = pipeline['context']['intermediate_model']['location']['model']
            # --- end note

            # note: populate available pipeline names
            if pipeline_name is None:  # checking all pipelines
                model_paths.append(model_path)
                pipelines_names.append(
                    f"Pipeline_{pipeline['context']['intermediate_model']['name'].split('P')[-1]}")

                # note: check dependencies for estimators
                request_json = download_request_json(run_params, pipelines_names[-1], wml_client)
                check_lale = check_pipeline_nodes(pipeline, request_json, wml_client)


            # checking only chosen pipeline
            elif pipeline_name == f"Pipeline_{pipeline['context']['intermediate_model']['name'].split('P')[-1]}":
                model_paths.append(model_path)
                pipelines_names = [f"Pipeline_{pipeline['context']['intermediate_model']['name'].split('P')[-1]}"]

                # note: check dependencies for estimators and other packages
                request_json = download_request_json(run_params, pipelines_names[-1], wml_client)
                check_lale = check_pipeline_nodes(pipeline, request_json, wml_client)

                break
            # --- end note

        if load_pipelines:
            # Disable printing to suppress warning from ai4ml
            with redirect_stdout(open(os.devnull, "w")):
                for model_path, pipeline_name in zip(model_paths, pipelines_names):
                    pipelines[pipeline_name] = joblib.load(load_file_from_file_system(wml_client=wml_client,
                                                                                      file_path=model_path))

        if store:
            for name, pipeline in pipelines.items():
                local_model_path = os.path.join(path, name)
                joblib.dump(pipeline, local_model_path)
                print(f"Selected pipeline stored under: {local_model_path}")

                # note: display download link to the model
                create_model_download_link(local_model_path)
                # --- end note

    else:
        from ibm_boto3 import client
        cos_client = client(
            service_name='s3',
            endpoint_url=run_params['entity']['results_reference']['connection']['endpoint_url'],
            aws_access_key_id=run_params['entity']['results_reference']['connection']['access_key_id'],
            aws_secret_access_key=run_params['entity']['results_reference']['connection']['secret_access_key']
        )
        buckets = []
        filenames = []
        keys = []

        pipeline_suffix = "gz" if is_ts_metrics else "pickle"
        for pipeline in run_params['entity']['status'].get('metrics', []):
            model_number = pipeline['context']['intermediate_model']['name'].split('P')[-1]
            model_phase = chose_model_output(model_number, is_ts_metrics=is_ts_metrics)

            if pipeline['context']['phase'] == model_phase:
                model_path = f"{pipeline['context']['intermediate_model']['location']['model']}"

                if pipeline_name is None:
                    buckets.append(run_params['entity']['results_reference']['location']['bucket'])
                    filenames.append(
                        f"{path}/Pipeline_{pipeline['context']['intermediate_model']['name'].split('P')[-1]}.{pipeline_suffix}")
                    keys.append(model_path)
                    pipelines_names.append(
                        f"Pipeline_{pipeline['context']['intermediate_model']['name'].split('P')[-1]}")

                    # note: check dependencies for estimators and other packages
                    request_json = download_request_json(run_params, pipelines_names[-1], wml_client)
                    check_lale = check_pipeline_nodes(pipeline, request_json, wml_client)

                elif pipeline_name == f"Pipeline_{pipeline['context']['intermediate_model']['name'].split('P')[-1]}":
                    buckets = [run_params['entity']['results_reference']['location']['bucket']]
                    filenames = [
                        f"{path}/Pipeline_{pipeline['context']['intermediate_model']['name'].split('P')[-1]}.{pipeline_suffix}"]
                    keys = [model_path]
                    pipelines_names = [f"Pipeline_{pipeline['context']['intermediate_model']['name'].split('P')[-1]}"]

                    # note: check dependencies for estimators and other packages
                    request_json = download_request_json(run_params, pipelines_names[-1], wml_client)
                    check_lale = check_pipeline_nodes(pipeline, request_json, wml_client)

                    break

        for bucket, filename, key, name in zip(buckets, filenames, keys, pipelines_names):
            cos_client.download_file(Bucket=bucket, Filename=filename, Key=key)
            if load_pipelines:

                # Disable printing to suppress warning from ai4ml
                with redirect_stdout(open(os.devnull, "w")):
                    if is_ts_metrics:
                        with gzip.open(filename, "rb") as f:
                            pipeline_content = f.read()
                            pipelines[name] = joblib.load(io.BytesIO(pipeline_content))
                    else:
                        pipelines[name] = joblib.load(filename)

                if not store:
                    if os.path.exists(filename):
                        os.remove(filename)

                else:
                    print(f"Selected pipeline stored under: {filename}")

                    # note: display download link to the model
                    create_model_download_link(filename)
                    # --- end note
    if load_pipelines and pipelines:
        return pipelines, check_lale

    elif load_pipelines:
        raise MissingPipeline(
            pipeline_name if pipeline_name is not None else "global_output pipeline",
            reason="The name of the pipeline is incorrect or there are no pipelines computed.")


def load_file_from_file_system(wml_client: 'APIClient',
                               file_path: str,
                               stream: bool = True) -> 'io.BytesIO':
    """
    Load file into memory from the file system.

    Parameters
    ----------
    wml_client: APIClient, required
        WML v4 client.

    file_path: str, required
        Path in the file system of the file.

    stream: bool, optional
        Indicator to stream data content.

    Returns
    -------
    Sklearn Pipeline
    """
    # note: prepare the file path
    file_path = file_path.split('auto_ml/')[-1]

    if wml_client.default_project_id:
        file_path = f"{file_path}?project_id={wml_client.default_project_id}"

    else:
        file_path = f"{file_path}?space_id={wml_client.default_space_id}"
    # --- end note

    buffer = io.BytesIO()
    response_with_model = requests.get(
        url=f"{wml_client.service_instance._href_definitions.get_wsd_model_attachment_href()}auto_ml/{file_path}",
        headers=wml_client._get_headers(),
        stream=stream)
    if stream:
        for data in response_with_model.iter_content():
            buffer.write(data)
    else:
        buffer.write(response_with_model.content)

    buffer.seek(0)

    return buffer


def load_file_from_file_system_nonautoai(wml_client: 'APIClient',
                                         file_path: str,
                                         stream: bool = True) -> 'io.BytesIO':
    """
    Load file into memory from the file system.

    Parameters
    ----------
    wml_client: APIClient, required
        WML v4 client.

    file_path: str, required
        Path in the file system of the file.

    stream: bool, optional
        Indicator to stream data content.

    Returns
    -------
        File content
    """
    # note: prepare the file path
    # --- end note

    buffer = io.BytesIO()

    response_with_model = requests.get(
        url=f"{wml_client.service_instance._href_definitions.get_wsd_model_attachment_href()}{file_path}",
        headers=wml_client._get_headers(),
        params=wml_client._params(),
        stream=stream)

    if stream:
        for data in response_with_model.iter_content():
            buffer.write(data)
    else:
        buffer.write(response_with_model.content)

    buffer.seek(0)

    return buffer


class NextRunDetailsGenerator:
    """
    Generator class to produce next list of run details.

    Parameters
    ----------
    wml_client: APIClient, required
        WML Client Instance
    """

    def __init__(self, wml_client: 'APIClient', href: str) -> None:
        self.wml_client = wml_client
        self.next_href = href

    def __iter__(self):
        return self

    def __next__(self):
        if self.next_href is not None:
            response = requests.get(
                url=f"{self.wml_client.wml_credentials['url']}{self.next_href}",
                headers=self.wml_client._get_headers())
            details = response.json()
            self.next_href = details.get('next', {'href': None})['href']
            return details.get('resources', [])

        else:
            raise StopIteration


def preprocess_request_json(request_json: Dict) -> Dict:
    """Removes S3 types from older trainings and replace them with container type."""
    if "content_location" in request_json:
        if "location" in request_json["content_location"]:
            if request_json["content_location"]["location"].get("type") == 's3':
                request_json["content_location"]["location"]["type"] = 'container'

        if request_json["content_location"].get("type") == 's3':
            request_json["content_location"]["type"] = 'container'

    if "training_data_references" in request_json:
        for ref in request_json["training_data_references"]:
            if ref.get("type") == 's3':
                ref['type'] = 'container'

            if "location" in ref:
                if ref['location'].get("type") == 's3':
                    ref['location']['type'] = 'container'

    return request_json


def chose_model_output(model_number: str, is_ml_metrics: bool = True, is_ts_metrics: bool = False) -> str:
    """Chose correct path for particular model number"""
    if is_ts_metrics:
        return 'after_final_pipelines_generation'
    elif is_ml_metrics:
        model_number = int(model_number)
        hpo_c_numbers = (4, 8, 12, 16)
        cognito_numbers = (3, 7, 11, 15)
        hpo_d_numbers = (2, 6, 10, 14)
        pre_hpo_d_numbers = (1, 5, 9, 13)

        if model_number in pre_hpo_d_numbers:
            return 'pre_hpo_d_output'

        elif model_number in hpo_d_numbers:
            return 'hpo_d_output'

        elif model_number in cognito_numbers:
            return 'cognito_output'

        elif model_number in hpo_c_numbers:
            return 'hpo_c_output'

        else:
            return 'global_output'


def prepare_auto_ai_model_to_publish_notebook_normal_scenario(
        pipeline_model: Union['Pipeline', 'TrainablePipeline'],
        result_connection,
        cos_client,
        run_params: Dict,
        space_id: str) -> Union[Tuple[str, Dict[str, dict]]]:
    """
    Prepares autoai model to publish in Watson Studio via COS.
    Option only for auto-gen notebooks with correct result references on COS.

    Parameters
    ----------
    pipeline_model: Union['Pipeline', 'TrainablePipeline'], required
        model object to publish

    result_connection: DataConnection, required
        Connection object with COS credentials and all needed locations for jsons

    cos_client: ibm_boto3.resource, required
        initialized COS client

    run_params: dictionary, required
        Dictionary with training details

    space_id: str, required

    Returns
    -------
    String with path to the saved model and jsons in COS.
    """
    path = result_connection.location._model_location
    model_number = pipeline_model.split('_')[-1]
    run_id = path.split('/data/')[0].split('/')[-1]
    is_ts_metrics = 'autoai-ts' in path
    request_path = f"{path.split('/data/')[0]}/assets/{run_id}_P{model_number}_{chose_model_output(model_number, is_ts_metrics=is_ts_metrics)}/resources/wml_model/request.json"

    bucket = result_connection.location.bucket
    cos_client.meta.client.download_file(Bucket=bucket, Filename='request.json', Key=request_path)
    with open('request.json', 'r') as f:
        request_str = f.read()

    # note: only if there was 1 estimator during training
    if 'content_location' not in request_str:
        request_path = f"{path.split('/data/')[0]}/assets/{run_id}_P{model_number}_compose_model_type_output/resources/wml_model/request.json"
        cos_client.meta.client.download_file(Bucket=bucket, Filename='request.json', Key=request_path)
        with open('request.json', 'r') as f:
            request_str = f.read()

    request_json: Dict[str, dict] = json.loads(request_str)
    if 'connection' in run_params['entity']['results_reference']:
        if "content_location" in request_json:
            if "location" in request_json["content_location"]:
                if request_json["content_location"]["location"].get("type") != 's3':
                    request_json['content_location']['connection'] = run_params['entity']['results_reference']['connection']

    request_json = preprocess_request_json(request_json)

    artifact_name = f"autoai_sdk{os.path.sep}{pipeline_model}.pickle"

    return artifact_name, request_json


# TODO: remove this function
def prepare_auto_ai_model_to_publish_notebook(pipeline_model: Union['Pipeline', 'TrainablePipeline'],
                                              result_connection,
                                              cos_client,
                                              obm: Optional[bool] = False) -> Union[Tuple[Dict[str, dict], str], str]:
    """
    Prepares autoai model to publish in Watson Studio via COS.
    Option only for auto-gen notebooks with correct result references on COS.

    Parameters
    ----------
    pipeline_model: Union['Pipeline', 'TrainablePipeline'], required
        model object to publish

    result_connection: DataConnection, required
        Connection object with COS credentials and all needed locations for jsons

    cos_client: ibm_boto3.resource, required
        initialized COS client

    obm: bool, optional
        Indicator if we need to extract OBM data

    Returns
    -------
    String with path to the saved model and jsons in COS.
    """
    joblib = try_import_joblib()

    artifact_type = ".gzip"

    artifact_name = f"artifact_auto_ai_model{artifact_type}"
    model_artifact_name = f"model_.tar.gz"
    wml_pipeline_definition_name = "pipeline-model.json"
    obm_model_name = "obm_model.zip"
    temp_model_name = '__temp_model.pickle'

    # note: path to the json describing the autoai POD specification
    path_parts = result_connection.location._model_location.split('model.pickle')
    if len(path_parts) == 1:
        path = result_connection.location._model_location.split('model.zip')[0]
        path = f"{path}pre_hpo_d_output/Pipeline1/"

    else:
        path = result_connection.location._model_location.split('model.pickle')[0]

    pipeline_model_json_path = f"{path}pipeline-model.json"
    schema_path = f"{path}schema.json"

    bucket = result_connection.location.bucket

    # note: Check if we have OBM experiment and get paths for obm model and schema
    if obm:
        obm_model_path = f"{path.split('/data/')[0]}/data/obm/model.zip"
        schema_path = f"{path.split('/data/')[0]}/data/obm/schemas.json"
        cos_client.meta.client.download_file(Bucket=bucket, Filename=obm_model_name, Key=obm_model_path)

    # note: need to download model schema and wml pipeline definition json
    cos_client.meta.client.download_file(Bucket=bucket, Filename=wml_pipeline_definition_name,
                                         Key=pipeline_model_json_path)
    cos_client.meta.client.download_file(Bucket=bucket, Filename='schema.json', Key=schema_path)

    with open('schema.json', 'r') as f:
        schema_json = f.read()

    # note: update the schema, it has wrong field types
    schema_json = schema_json.replace('fieldType', 'type')
    # --- end note

    # note: saved passed model as pickle, for further tar.gz packaging
    joblib.dump(pipeline_model, temp_model_name)
    # --- end note

    # note: create a tar.gz file with model pickle, name it as 'model_run_id.tar.gz', model.pickle inside
    with open_tar(model_artifact_name, 'w:gz') as tar:
        tar.add(temp_model_name, arcname='model.pickle')

    remove_file(filename=temp_model_name)
    # --- end note

    # note: create final zip to publish on WML cloud v4 GA
    with ZipFile(artifact_name, 'w') as zip_file:
        if obm:
            # note: write order is important!
            zip_file.write(obm_model_name)
        zip_file.write(model_artifact_name)
        zip_file.write(wml_pipeline_definition_name)

    remove_file(filename=model_artifact_name)
    remove_file(filename=wml_pipeline_definition_name)
    if obm:
        remove_file(filename=obm_model_name)
    # --- end note

    return json.loads(schema_json), artifact_name


def prepare_auto_ai_model_to_publish_normal_scenario(
        pipeline_model: Union['Pipeline', 'TrainablePipeline'],
        run_params: dict,
        run_id: str,
        wml_client: 'APIClient',
        space_id: str,
        result_reference: 'DataConnection' = None) -> Union[Tuple[str, Dict[str, dict]]]:
    """
    Helper function to specify `content_location` statement for AutoAI models to store in repository.

    Parameters
    ----------
    pipeline_model: Union['Pipeline', 'TrainablePipeline'], required
        Model that will be prepared for an upload.

    run_params: dict, required
        Fetched details of the run/fit.

    run_id: str, required
        Fit/run ID associated with the model.

    wml_client: APIClient, required

    space_id: str, required

    result_reference: DataConnection, optional
        Needed when we have something different than old S3 on a Cloud.

    Returns
    -------
    If cp4d: Dictionary with model schema and artifact name to upload, stored temporally in the user local file system.
    else: path name to the stored model in COS
    """
    try:
        request_json: Dict[str, dict] = download_request_json(run_params, pipeline_model, wml_client, result_reference)
    except:
        raise MissingPipeline(
            pipeline_model,
            reason="The name of the pipeline is incorrect or there are no pipelines computed."
        )
    # note: fill connection details
    if 'connection' in run_params['entity']['results_reference']:
        if "content_location" in request_json:
            if "location" in request_json["content_location"]:
                if request_json["content_location"]["location"].get("type") != 's3' and request_json["content_location"]["location"].get("type") != 'container':
                    request_json['content_location']['connection'] = run_params['entity']['results_reference']['connection']

    artifact_name = f"autoai_sdk{os.path.sep}{pipeline_model}.pickle"

    return artifact_name, request_json


# TODO: remove this function
def prepare_auto_ai_model_to_publish(
        pipeline_model: Union['Pipeline', 'TrainablePipeline'],
        run_params: dict,
        run_id: str,
        wml_client: 'APIClient') -> Union[Tuple[Dict[str, dict], str], str]:
    """
    Helper function to download and load computed AutoAI pipelines (sklearn pipelines).
    Parameters
    ----------
    pipeline_model: Union['Pipeline', 'TrainablePipeline'], required
        Model that will be prepared for an upload.
    run_params: dict, required
        Fetched details of the run/fit.
    run_id: str, required
        Fit/run ID associated with the model.
    wml_client: APIClient, required
    Returns
    -------
    If cp4d: Dictionary with model schema and artifact name to upload, stored temporally in the user local file system.
    else: path name to the stored model in COS
    """

    joblib = try_import_joblib()

    artifact_type = ".tar.gz" if wml_client.ICP else ".gzip"

    artifact_name = f"artifact_auto_ai_model{artifact_type}"
    model_artifact_name = f"model_{run_id}.tar.gz"
    wml_pipeline_definition_name = "pipeline-model.json"
    obm_model_name = "obm_model.zip"
    temp_model_name = '__temp_model.pickle'

    # note: prepare file paths of pipeline-model and schema (COS / file system location)
    pipeline_info = run_params['entity']['status'].get('metrics')[-1]
    pipeline_model_path = f"{pipeline_info['context']['intermediate_model']['location']['pipeline_model']}"
    schema_path = f"{pipeline_info['context']['intermediate_model']['schema_location']}"
    obm_model_path = None
    # --- end note

    # note: Check if we have OBM experiment and get paths for obm model and schema
    if 'obm' in run_params['entity']['status'].get('feature_engineering_components', {}):
        obm_model_path = f"{pipeline_model_path.split('/data/')[0]}/data/obm/model.zip"
        schema_path = f"{pipeline_model_path.split('/data/')[0]}/data/obm/schemas.json"

    if wml_client.ICP:
        # note: downloading pipeline-model.json and schema.json from file system on CP4D
        schema_json = load_file_from_file_system(wml_client=wml_client, file_path=schema_path).read().decode()
        pipeline_model_json = load_file_from_file_system(wml_client=wml_client,
                                                         file_path=pipeline_model_path).read().decode()
        with open(wml_pipeline_definition_name, 'w') as f:
            f.write(pipeline_model_json)
        # --- end note

        # note: save obm model.zip locally
        if obm_model_path is not None:
            obm_model = load_file_from_file_system(wml_client=wml_client,
                                                   file_path=obm_model_path).read().decode()

            with open(obm_model_name, 'w') as f:
                f.write(obm_model)
        # --- end note

    else:
        cos_client = init_cos_client(run_params['entity']['results_reference']['connection'])
        bucket = run_params['entity']['results_reference']['location']['bucket']

        # note: need to download model schema and wml pipeline definition json
        cos_client.meta.client.download_file(Bucket=bucket, Filename=wml_pipeline_definition_name,
                                             Key=pipeline_model_path)
        cos_client.meta.client.download_file(Bucket=bucket, Filename='schema.json', Key=schema_path)

        with open('schema.json', 'r') as f:
            schema_json = f.read()

        # note: save obm model.zip locally
        if obm_model_path is not None:
            cos_client.meta.client.download_file(Bucket=bucket, Filename=obm_model_name, Key=obm_model_path)
        # --- end note

    # note: update the schema, it has wrong field types and missing id
    schema_json = schema_json.replace('fieldType', 'type')
    # --- end note

    # note: saved passed model as pickle, for further tar.gz packaging
    joblib.dump(pipeline_model, temp_model_name)
    # --- end note

    # note: create a tar.gz file with model pickle, name it as 'model_run_id.tar.gz', model.pickle inside
    with open_tar(model_artifact_name, 'w:gz') as tar:
        tar.add(temp_model_name, arcname='model.pickle')

    remove_file(filename=temp_model_name)
    # --- end note

    with ZipFile(artifact_name, 'w') as zip_file:
        if obm_model_path is not None:
            # note: write order is important!
            zip_file.write(obm_model_name)
        zip_file.write(model_artifact_name)
        zip_file.write(wml_pipeline_definition_name)

    remove_file(filename=model_artifact_name)
    remove_file(filename=wml_pipeline_definition_name)
    if obm_model_path is not None:
        remove_file(filename=obm_model_name)
    # --- end note

    return json.loads(schema_json), artifact_name


def modify_pipeline_model_json(data_location: str, model_path: str) -> None:
    """
    Change the location of KB model in pipeline-model.json

    Parameters
    ----------
    data_location: str, required
        pipeline-model.json data local path

    model_path: str, required
        Path to KB model stored in COS.
    """
    with open(data_location, 'r') as f:
        data = json.load(f)

    data['pipelines'][0]['nodes'][-1]['parameters']['output_model']['location'] = f"{model_path}model.pickle"

    with open(data_location, 'w') as f:
        f.write(json.dumps(data))


def init_cos_client(connection: dict) -> 'resource':
    """Initiate COS client for further usage."""
    from ibm_botocore.client import Config
    from ibm_boto3 import resource

    # note: In case of connection_asset we need too get COS credentials from connection details.
    if connection.get("properties") is not None:
        if "access_key" in connection["properties"] and "secret_key" in connection["properties"]:
            connection = {
                "endpoint_url": connection["properties"].get("url"),
                "access_key_id": connection["properties"].get("access_key"),
                "secret_access_key": connection["properties"].get("secret_key"),
            }
        else:
            connection = {
                "endpoint_url": connection["properties"].get("url"),
                "api_key": connection["properties"].get("api_key"),
                "auth_endpoint": connection["properties"].get("iam_url")
            }
    # --- end note

    if connection.get('auth_endpoint') is not None and connection.get('api_key') is not None:
        cos_client = resource(
            service_name='s3',
            ibm_api_key_id=connection['api_key'],
            ibm_auth_endpoint=connection['auth_endpoint'],
            config=Config(signature_version="oauth"),
            endpoint_url=connection['endpoint_url']
        )
    else:
        cos_client = resource(
            service_name='s3',
            endpoint_url=connection['endpoint_url'],
            aws_access_key_id=connection['access_key_id'],
            aws_secret_access_key=connection['secret_access_key']
        )
    return cos_client


def remove_file(filename: str):
    """Helper function to clean user local storage from temporary package files."""
    if os.path.exists(filename):
        os.remove(filename)


class ProgressGenerator:
    def __init__(self):
        self.progress_messages = {
            "pre_hpo_d_output": 15,
            "hpo_d_output": 30,
            "cognito_output": 50,
            "hpo_c_output": 70,
            "compose_model_type_output": 80,
            "fold_output": 90,
            "global_output": 99,
            # timeseries
            'after_pipeline_execution': 50,
            'after_holdout_execution': 80,
            'after_final_pipelines_generation': 99
        }
        self.total = 100
        self.position = 0
        self.max_position = 5

    def get_progress(self, text):
        for i, e in enumerate(self.progress_messages):
            if e in text:
                pos = self.max_position
                self.max_position = max(self.max_position, self.progress_messages[e])
                if pos < self.max_position:
                    progress = pos - self.position
                    self.position = pos
                    return progress

        if self.position + 1 >= self.max_position:
            return 0
        else:
            self.position += 1
            return 1

    def get_total(self):
        return self.total


def is_ipython():
    """Check if code is running in the notebook."""
    try:
        name = get_ipython().__class__.__name__
        if name != 'ZMQInteractiveShell':
            return False
        else:
            return True

    except Exception:
        return False


def try_import_lale():
    """
    Check if lale package is installed in local environment, if not, just download and install it.
    """
    lale_version = '0.4.15'
    try:
        try:
            installed_module_version = fallback_to_pip_for_version_check({'name': 'lale'})

        except Exception:
            installed_module_version = pkg_resources.get_distribution('lale').version

        if version.parse(installed_module_version) < version.parse(lale_version):
            warn(f"\"lale\" package version is too low than {lale_version}."
                 f"Installing version {lale_version}")

            try:
                check_call([executable, "-m", "pip", "install", f"lale=={lale_version}"])

            except Exception as e:
                raise CannotInstallLibrary(value_name=e,
                                           reason="lale failed to install. Please install it manually.")

    except pkg_resources.DistributionNotFound as e:
        warn(f"\"lale\" is not installed."
             f"Installing version {lale_version}")

        try:
            check_call([executable, "-m", "pip", "install", f"lale=={lale_version}"])

        except Exception as e:
            raise CannotInstallLibrary(value_name=e,
                                       reason="lale failed to install. Please install it manually.")


def try_import_autoai_libs(minimum_version: str = None):
    """
    Check if autoai_libs package is installed in local environment, if not, just download and install it.
    """
    package = {'name': 'autoai-libs'}
    default_version = '1.13.0'

    if minimum_version is not None:
        default_version = minimum_version

    def install_autoai_libs(version):
        """Try to install autoai-libs via pip."""
        try:
            check_call([executable, "-m", "pip", "install", f"autoai_libs>={version}"])

        except Exception as e:
            raise CannotInstallLibrary(value_name=e,
                                       reason=f"autoai_libs>={version} failed to install. Please install it manually.")

    try:
        import autoai_libs

        if minimum_version is not None:
            try:
                installed_module_version = fallback_to_pip_for_version_check(package)

            except Exception:
                installed_module_version = pkg_resources.get_distribution(package['name']).version

            if version.parse(installed_module_version) < version.parse(minimum_version):
                install_autoai_libs(version=minimum_version)

    except ImportError:
        warn(f"\"autoai_libs\" package is not installed. "
             f"This is the needed dependency for pipeline model refinery, we will try to install it now...")
        install_autoai_libs(version=default_version)


def try_import_autoai_ts_libs():
    """
    Check if autoai_ts_libs package is installed in local environment, if not, just download and install it.
    """
    try:
        import autoai_ts_libs

    except ImportError:
        warn(f"\"autoai_libs\" package is not installed. "
             f"This is the needed dependency for pipeline model refinery, we will try to install it now...")

        try:
            check_call([executable, "-m", "pip", "install", "autoai-ts-libs"])

        except Exception as e:
            raise CannotInstallLibrary(value_name=e,
                                       reason="autoai-ts-libs failed to install. Please install it manually.")

def try_import_tqdm():
    """
    Check if tqdm package is installed in local environment, if not, just download and install it.
    """
    try:
        import tqdm

    except ImportError:
        warn(f"\"tqdm\" package is not installed. "
             f"This is the needed dependency for pipeline training, we will try to install it now...")

        try:
            check_call([executable, "-m", "pip", "install", "tqdm==4.43.0"])

        except Exception as e:
            raise CannotInstallLibrary(value_name=e,
                                       reason="tqdm==4.43.0 failed to install. Please install it manually.")


def try_import_xlrd():
    """
    Check if xlrd package is installed in local environment, if not, just download and install it.
    """
    try:
        import xlrd

    except ImportError:
        warn(f"\"xlrd\" package is not installed. "
             f"This is the needed dependency for loading dataset from xls files, we will try to install it now...")

        try:
            check_call([executable, "-m", "pip", "install", "xlrd==1.2.0"])

        except Exception as e:
            raise CannotInstallLibrary(value_name=e,
                                       reason="xlrd==1.2.0 failed to install. Please install it manually.")


def try_import_graphviz():
    """
    Check if graphviz package is installed in local environment, if not, just download and install it.
    """
    try:
        import graphviz

    except ImportError:
        warn(f"\"graphviz\" package is not installed. "
             f"This is the needed dependency for visualizing data join graph, we will try to install it now...")

        try:
            check_call([executable, "-m", "pip", "install", "graphviz==0.14"])

        except Exception as e:
            raise CannotInstallLibrary(value_name=e,
                                       reason="graphviz==0.14 failed to install. Please install it manually.")


def try_import_joblib():
    """
    Check if joblib is available from scikit-learn or externally and change 'load' method to inform the user about
    compatibility issues.
    """

    try:
        # note only up to scikit version 0.20.3
        from sklearn.externals import joblib

    except ImportError:
        # only for scikit 0.23.*
        import joblib

    return joblib


def try_load_dataset(
        buffer: Union['BytesIO', 'BufferedIOBase'],
        sheet_name: str = 0,
        separator: str = ',',
        encoding: Optional[str] = 'utf-8') -> Union['DataFrame', 'OrderedDict']:
    """
    Load data into a pandas DataFrame from BytesIO object.

    Parameters
    ----------
    buffer: Union['BytesIO', 'BufferedIOBase'], required
        Buffer with bytes data.

    sheet_name: str, optional
        Name of the xlsx sheet to read.

    separator: str, optional
        csv separator

    encoding: str, optional

    Returns
    -------
    DataFrame or OrderedDict
    """
    from pandas import read_csv, read_excel

    try:
        buffer.seek(0)
        data = read_csv(buffer, sep=separator, encoding=encoding)

    except Exception as e1:
        try:
            try_import_xlrd()
            buffer.seek(0)
            data = read_excel(buffer, sheet_name=sheet_name)

        except Exception as e2:
            raise DataFormatNotSupported(None, reason=f"Error1: {e1} Error2: {e2}")

    return data


def try_load_tar_gz(
        buffer: Union['BytesIO', 'BufferedIOBase'],
        separator: str = ',',
        encoding: Optional[str] = 'utf-8') -> Union['DataFrame', 'OrderedDict']:
    """
    Load csv packed into tar.gz into a pandas DataFrame from BytesIO object.

    Parameters
    ----------
    buffer: Union['BytesIO', 'BufferedIOBase'], required
        Buffer with bytes data.

    separator: str, optional
        csv separator

    encoding: str, optional

    Returns
    -------
    DataFrame or OrderedDict
    """
    from pandas import read_csv
    import uuid
    import tarfile

    tmp_file = f'tmp_file_{uuid.uuid4()}.tar.gz'

    try:
        with open(tmp_file, 'wb') as out:
            out.write(buffer.read())

        tar = tarfile.open(tmp_file, "r:gz")
        tar.extractall()
        tar.close()

        extracted_file_name = 'holdout_data_indices.csv'

        data = read_csv(extracted_file_name, sep=separator, encoding=encoding)
        return data
    finally:
        os.remove(tmp_file)
        os.remove('holdout_data_indices.csv')


def check_dependencies_versions(request_json: dict, wml_client, estimator_pkg: str) -> bool:
    """
    Check packages installed versions and inform the user about needed ones.

    Parameters
    ----------
    request_json: dict, required
        Dictionary with request from training saved on user COS or CP4D fs.

    wml_client: APIClient, required
        Internal WML client used for sw spec requests.

    estimator_pkg: str, required
        Name of the estimator package to check with.
    """
    sw_spec_name = request_json.get('hybrid_pipeline_software_specs', [{'name': None}])[-1]['name']
    sw_spec_id = wml_client.software_specifications.get_id_by_name(sw_spec_name)
    sw_spec = wml_client.software_specifications.get_details(sw_spec_id)

    packages = sw_spec['entity']['software_specification']['software_configuration']['included_packages']

    check_lale = True
    if 'lale' in str(packages):
        check_lale = False

    packages_to_check = ['numpy', 'scikit-learn', 'autoai-libs', 'gensim', 'lale']

    if estimator_pkg is not None:
        packages_to_check.append(estimator_pkg)
        packages_to_check.append(f'py-{estimator_pkg}')

    errored_packages = []

    for package in packages:
        if package['name'] in packages_to_check:
            try:
                # note: try to use pip for version check! if failed use pkg_resources
                try:
                    installed_module_version = fallback_to_pip_for_version_check(package)

                except Exception:
                    installed_module_version = pkg_resources.get_distribution(package['name']).version

                # workaround for autai-libs and numpy versions in SW spec
                if package['name'] == 'autoai-libs' or package['name'] == 'numpy' \
                        or package['name'] == 'lale' or package['name'] == 'snapml':

                    if package['name'] == 'numpy':
                        numpy_installed_version = version.parse(installed_module_version)
                        numpy_sw_spec_version = version.parse(package['version'])

                        if numpy_installed_version.major != numpy_sw_spec_version.major:
                            errored_packages.append(package)

                        elif numpy_installed_version.minor != numpy_sw_spec_version.minor:
                            errored_packages.append(package)

                    elif version.parse(installed_module_version) < version.parse(package['version']):
                        # we should produce different error for lale and snap_ml as only 2 major numbers are significant
                        packages_less_strict_error_list = ['lale', 'snapml']
                        if package['name'] in packages_less_strict_error_list and len(
                                package['version'].split('.')) >= 3:
                            _version = package['version'].split('.')[:3]  # take only 3 major version number
                            package['version'] = '.'.join(_version)
                            package['version'] = f">={package['version']}"

                        errored_packages.append(package)

                # Note: temporary check / workaround for lightgbm on WS
                elif package['name'] == 'lightgbm' or package['name'] == 'py-lightgbm':
                    if installed_module_version == '3.1.1' or installed_module_version == '3.2.1':
                        pass

                else:
                    if installed_module_version != package['version']:
                        errored_packages.append(package)

            except pkg_resources.DistributionNotFound as e:
                errored_packages.append(package)

        else:
            pass

    if errored_packages:
        raise LibraryNotCompatible(reason=f"Please check if you have installed correct versions "
                                          f"of the following packages: {errored_packages} "
                                          f"These packages are required to load ML model successfully "
                                          f"on your environment.")

    return check_lale


def prepare_cos_client(
        training_data_references: List['DataConnection'] = None,
        training_result_reference: 'DataConnection' = None) -> Tuple[Union[List[Tuple['DataConnection', 'resource']]],
                                                                     Union[Tuple['DataConnection', 'resource'], None]]:
    """
    Create COS clients for training data and results.

    Parameters
    ----------
    training_data_references: List['DataConnection'], optional

    training_result_reference: 'DataConnection', optional

    Returns
    -------
    list of COS clients for training data , client for results
    """
    from ibm_watson_machine_learning.helpers import S3Connection
    from ibm_boto3 import resource
    from ibm_botocore.client import Config

    def differentiate_between_credentials(connection: 'S3Connection') -> 'resource':
        # note: we do not know which version of COS credentials user used during training
        if hasattr(connection, 'auth_endpoint') and hasattr(connection, 'api_key'):
            cos_client = resource(
                service_name='s3',
                ibm_api_key_id=connection.api_key,
                ibm_auth_endpoint=connection.auth_endpoint,
                config=Config(signature_version="oauth"),
                endpoint_url=connection.endpoint_url
            )

        else:
            cos_client = resource(
                service_name='s3',
                endpoint_url=connection.endpoint_url,
                aws_access_key_id=connection.access_key_id,
                aws_secret_access_key=connection.secret_access_key
            )
        # --- end note

        return cos_client

    cos_client_results = None
    data_cos_clients = []

    if training_result_reference is not None:
        if (isinstance(training_result_reference.connection, S3Connection) or
                training_result_reference._check_if_connection_asset_is_s3()):
            cos_client_results = (training_result_reference,
                                  differentiate_between_credentials(connection=training_result_reference.connection))

    if training_data_references is not None:
        for reference in training_data_references:
            if (isinstance(reference.connection, S3Connection) or reference._check_if_connection_asset_is_s3()):
                data_cos_clients.append((reference,
                                         differentiate_between_credentials(connection=reference.connection)))

    return data_cos_clients, cos_client_results


def create_summary(details: dict, scoring: str) -> 'DataFrame':
    """
    Creates summary in a form of a pandas.DataFrame of computed pipelines (should be used in remote and local scenario
    with COS).

    Parameters
    ----------
    details: dict, required
        Dictionary with all training data

    scoring: str, required
        scoring method

    Returns
    -------
    pandas.DataFrame with pipelines summary
    """
    from pandas import DataFrame

    is_ml_metrics = 'ml_metrics' in details['entity']['status'].get('metrics', [{}])[0]
    is_ts_metrics = 'ts_metrics' in details['entity']['status'].get('metrics', [{}])[0]

    if not is_ml_metrics and not is_ts_metrics:
        raise NoAvailableMetrics()

    def get_metrics_names():
        if is_ml_metrics:
            return details['entity']['status'].get('metrics', [{}])[0].get('ml_metrics', {}).keys()
        elif is_ts_metrics:
            names = list(['validation_' + x for x in
                          details['entity']['status'].get('metrics', [{}])[0].get('ts_metrics', {}).get('training',
                                                                                                        {}).keys()])
            try:
                holdout_names = list(['holdout_' + y for y in
                                      [x for x in details['entity']['status'].get('metrics', [{}]) if
                                       'holdout' in x['ts_metrics']][0]['ts_metrics']['holdout'].keys()])
            except IndexError:
                holdout_names = []
            try:
                backtest_names = list(['backtest_' + y for y in
                                       [x for x in details['entity']['status'].get('metrics', [{}]) if
                                        'backtest' in x['ts_metrics']][0]['ts_metrics']['backtest']['avg'].keys()])
            except IndexError:
                backtest_names = []

            return names + holdout_names + backtest_names

    def is_winner(pipeline_name):  # ts only
        if is_ts_metrics:
            return len(list([x for x in details['entity']['status'].get('metrics', [{}])
                             if x['context']['intermediate_model']['name'] == pipeline_name and 'holdout' in x[
                                 'ts_metrics']])) > 0
        elif is_ml_metrics:
            return True

    if is_ml_metrics:
        columns = ['Pipeline Name', 'Enhancements', 'Estimator']
    elif is_ts_metrics:
        columns = ['Pipeline Name', 'Enhancements', 'Estimator', 'Winner']

    columns = (columns +
               [metric_name for metric_name in
                get_metrics_names()])
    values = []

    for pipeline in details['entity']['status'].get('metrics', []):
        model_number = pipeline['context']['intermediate_model']['name'].split('P')[-1]
        model_phase = chose_model_output(model_number, is_ml_metrics, is_ts_metrics)

        if pipeline['context']['phase'] == model_phase:
            if is_ml_metrics:
                enhancements = []
                steps = pipeline['context']['intermediate_model']['composition_steps']

                if any('hpo' in s for s in steps):
                    enhancements.append('HPO')
                if 'cognito' in steps:
                    enhancements.append('FE')
                if 'TextTransformer' in pipeline['context']['intermediate_model']['pipeline_nodes']:
                    enhancements.append('Text_FE')

                enhancements = ', '.join(enhancements)
            elif is_ts_metrics:
                enhancements = 'HPO, FE'

            def get_metrics_items():
                if is_ml_metrics:
                    return pipeline['ml_metrics'].items()
                elif is_ts_metrics:
                    def prepare_items(metrics, pipeline_name, metric_name, prefix):
                        try:
                            chosen_obj = [x for x in metrics if
                                          x['context']['intermediate_model']['name'] == pipeline_name and metric_name in
                                          x['ts_metrics']][0]
                        except Exception as e:
                            return []

                        if metric_name == 'backtest':
                            return list({prefix + x: chosen_obj['ts_metrics'][metric_name]['avg'][x] for x in
                                         chosen_obj['ts_metrics'][metric_name]['avg']}.items())
                        else:
                            return list({prefix + x: chosen_obj['ts_metrics'][metric_name][x] for x in
                                         chosen_obj['ts_metrics'][metric_name]}.items())

                    pipeline_name = pipeline['context']['intermediate_model']['name']
                    metrics = details['entity']['status'].get('metrics', [])
                    training_items = prepare_items(metrics, pipeline_name, 'training', 'validation_')
                    holdout_items = prepare_items(metrics, pipeline_name, 'holdout', 'holdout_')
                    backtest_items = prepare_items(metrics, pipeline_name, 'backtest', 'backtest_')

                    return training_items + holdout_items + backtest_items

            # note: workaround when some pipelines have less or more metrics computed
            if is_ml_metrics:
                metrics = columns[3:]
            elif is_ts_metrics:
                metrics = columns[4:]
            pipeline_metrics = [None] * len(metrics)
            for metric, value in get_metrics_items():
                for i, metric_name in enumerate(metrics):
                    if metric_name == metric:
                        pipeline_metrics[i] = value
            # --- end note

            if is_ml_metrics:
                values.append(
                    ([f"Pipeline_{pipeline['context']['intermediate_model']['name'].split('P')[-1]}"] +
                     [enhancements] +
                     [pipeline['context']['intermediate_model']['pipeline_nodes'][-1]] +
                     pipeline_metrics
                     ))
            elif is_ts_metrics:
                values.append(
                    ([f"Pipeline_{pipeline['context']['intermediate_model']['name'].split('P')[-1]}"] +
                     [enhancements] +
                     [pipeline['context']['intermediate_model']['pipeline_nodes'][-1]] +
                     [is_winner(pipeline['context']['intermediate_model']['name'])] +
                     pipeline_metrics
                     ))

    pipelines = DataFrame(data=values, columns=columns)
    pipelines.drop_duplicates(subset="Pipeline Name", keep='first', inplace=True)
    pipelines.set_index('Pipeline Name', inplace=True)

    try:
        if is_ml_metrics:
            pipelines = pipelines.sort_values(
                by=[f"training_{scoring}"], ascending=False).rename(
                {
                    f"training_{scoring}":
                        f"training_{scoring}_(optimized)"
                }, axis='columns')
        elif is_ts_metrics:
            metrics_names = get_metrics_names()
            pipelines = pipelines.sort_values(
                by=['Winner'] + ([metrics_names[0]] if len(metrics_names) > 0 else []), ascending=False)

    # note: sometimes backend will not return 'training_' prefix to the metric
    except KeyError:
        pass

    def neg(x):
        if x is None or (x.__class__.__name__ == 'Series' and len(x) == 0):
            return x

        if x.__class__.__name__ == 'Series' or type(x) is list:
            return [neg(a) for a in x]
        else:
            return -x

    # for columns with _neg_ inside name
    neg_columns = [col for col in pipelines if '_neg_' in col]
    pipelines[neg_columns] = pipelines[neg_columns].apply(lambda x: neg(x))
    pipelines = pipelines.rename(columns={col: col.replace('_neg_', '_') for col in neg_columns})

    # for columns with neg_ on beginning of name
    neg_columns = [col for col in pipelines if col.startswith('neg_')]
    pipelines[neg_columns] = pipelines[neg_columns].apply(lambda x: neg(x))
    pipelines = pipelines.rename(columns={col: col[4:] for col in neg_columns})

    return pipelines


def get_node_and_runtime_index(node_name: str, optimizer_config: dict) -> Tuple[int, int]:
    """Find node index from node name in experiment parameters."""
    node_number = None
    runtime_number = None

    for i, node in enumerate(optimizer_config['entity']['document']['pipelines'][0]['nodes']):
        if node_name == 'kb' and (node.get('id') == 'kb' or node.get('id') == 'automl'):
            node_number = i
            break

        elif node_name == 'obm' and node.get('id') == 'obm':
            node_number = i
            break

        elif node_name == 'ts' and (node.get('id') == 'ts' or node.get('id') == 'autoai-ts'):
            node_number = i
            break

    for i, runtime in enumerate(optimizer_config['entity']['document']['runtimes']):
        if node_name == 'kb' and (runtime.get('id') == 'kb' or runtime.get('id') == 'automl' or
                                  runtime.get('id') == 'autoai'):
            runtime_number = i
            break

        elif node_name == 'obm' and runtime.get('id') == 'obm':
            runtime_number = i
            break

        elif node_name == 'ts' and runtime.get('id') == 'autoai':
            runtime_number = i
            break

    return node_number, runtime_number


def download_experiment_details_from_file(result_client_and_connection: Tuple['DataConnection', 'resource']) -> dict:
    """Try to download training details from user COS."""

    try:
        file = result_client_and_connection[1].Object(
            result_client_and_connection[0].location.bucket,
            result_client_and_connection[0].location._training_status).get()

        details = json.loads(file['Body'].read())

    except Exception as e:
        raise CannotDownloadTrainingDetails('', reason=f"Error: {e}")

    return details


def download_wml_pipeline_details_from_file(result_client_and_connection: Tuple['DataConnection', 'resource']) -> dict:
    """Try to download wml pipeline details from user COS."""
    try:
        model_location = result_client_and_connection[0].location._model_location
        is_timeseries = 'autoai-ts' in model_location

        path_parts = model_location.split('model.pickle')
        if len(path_parts) == 1:
            path = model_location.split('model.zip')[0]
            if is_timeseries:
                path = f"{path}after_pipeline_execution/P1/"
            else:
                path = f"{path}pre_hpo_d_output/Pipeline1/"


        else:
            path = model_location.split('model.pickle')[0]

        path = f"{path}pipeline-model.json"

        file = result_client_and_connection[1].Object(
            result_client_and_connection[0].location.bucket,
            path).get()

        details = json.loads(file['Body'].read())

    except Exception as e:
        raise CannotDownloadWMLPipelineDetails('', reason=f"Error: {e}")

    return details


def prepare_model_location_path(model_path: str) -> str:
    """
    To be able to get best pipeline after computation we need to change model_location string to global_output.
    """

    if "data/automl/" in model_path:
        path = model_path.split('data/automl/')[0]
        path = f"{path}data/automl/global_output/"

    else:
        path = model_path.split('data/kb/')[0]
        path = f"{path}data/kb/global_output/"

    return path


def check_graphviz_binaries(f):
    @wraps(f)
    def _f(*method_args, **method_kwargs):
        from graphviz.backend import ExecutableNotFound
        try:
            output = f(*method_args, **method_kwargs)

        except ExecutableNotFound as e:
            raise VisualizationFailed(
                reason=f"Cannot perform visualization with graphviz. Please make sure that you have Graphviz binaries "
                       f"installed in your system. Please follow this guide: https://www.graphviz.org/download/")

        return output

    return _f


def get_sw_spec_and_type_based_on_sklearn(client: 'APIClient', spec: str) -> Tuple[str, str]:
    """Based on user environment and pipeline sw spec, check sklearn version and find apropriate sw spec.

    Returns
    -------
    model_type, sw_spec
    """
    import sklearn

    if '0.20.' in sklearn.__version__ and spec in ['autoai-kb_3.0-py3.6', 'autoai-ts_1.0-py3.6']:
        sw_spec = client.software_specifications.get_id_by_name('autoai-kb_3.0-py3.6')
        model_type = 'scikit-learn_0.20'

    elif '0.20.' in sklearn.__version__ and spec not in ['autoai-kb_3.0-py3.6', 'autoai-ts_1.0-py3.6']:
        raise LibraryNotCompatible(reason="Your version of scikit-learn is different then trained pipeline. "
                                          "Trained pipeline version: 0.23.* "
                                          "Your version: " + sklearn.__version__)

    elif '0.23.' in sklearn.__version__ and spec in ['autoai-kb_3.1-py3.7', 'autoai-ts_1.0-py3.7']:
        sw_spec = client.software_specifications.get_id_by_name('autoai-kb_3.1-py3.7')
        model_type = 'scikit-learn_0.23'

    elif '0.23.' in sklearn.__version__ and spec not in ['autoai-kb_3.1-py3.7', 'autoai-ts_1.0-py3.7']:
        raise LibraryNotCompatible(reason="Your version of scikit-learn is different then trained pipeline. "
                                          "Trained pipeline version: 0.20.* "
                                          "Your version: " + sklearn.__version__)

    else:
        raise LibraryNotCompatible(reason="Your version of scikit-learn is not supported. Use one of [0.20.*, 0.23.*]")

    return model_type, sw_spec


def validate_additional_params_for_optimizer(params):
    expected_params = [
        'learning_type', 'positive_label', 'scorer_for_ranking', 'scorers', 'num_folds', 'random_state',
        'preprocessor_flag', 'preprocessor_hpo_flag', 'preprocessor_hpo_estimator', 'hpo_searcher', 'cv_num_folds',
        'hpo_d_iter_threshold', 'hpo_c_iter_threshold', 'max_initial_points', 'preprocess_transformer_chain',
        'daub_ensembles_flag', 'max_num_daub_ensembles', 'run_hpo_after_daub_flag', 'daub_include_only_estimators',
        'run_cognito_flag', 'cognito_ensembles_flag', 'max_num_cognito_ensembles', 'cognito_display_flag',
        'run_hpo_after_cognito_flag', 'cognito_kwargs', 'cognito_scorers', 'daub_adaptive_subsampling_max_mem_usage',
        'daub_adaptive_subsampling_used_mem_ratio_threshold', 'daub_kwargs', 'compute_feature_importances_flag',
        'compute_feature_importances_options', 'compute_feature_importances_pipeline_options', 'show_status_flag',
        'status_msg_handler', 'state_max_report_priority', 'msg_max_report_priority', 'cognito_pass_ptype',
        'hpo_timeout_in_seconds', 'cognito_use_feature_importances_flag', 'cognito_max_iterations',
        'cognito_max_search_level', 'cognito_transform_names', 'cognito_use_grasspile', 'cognito_subsample',
        'holdout_param', 'missing_values_reference_list', 'datetime_processing_flag',
        'datetime_delete_source_columns', 'datetime_processing_options', 'ensemble_pipelines_flag', 'ensemble_tags',
        'ensemble_comb_method', 'ensemble_selection_flag', 'ensemble_weighted_flag', 'ensemble_corr_sel_method',
        'ensemble_corr_termination_diff_threshold', 'ensemble_num_best_pipelines', 'ensemble_num_folds',
        'compute_pipeline_notebooks_flag', 'pipeline_ranking_metric', 'cpus_available', 'wml_status_msg_version',
        'float32_processing_flag', 'train_remove_missing_target_rows_flag', 'train_sample_rows_test_size',
        'train_sample_columns_index_list', 'preprocessor_cat_imp_strategy', 'preprocessor_cat_enc_encoding',
        'preprocessor_num_imp_strategy', 'preprocessor_num_scaler_use_scaler_flag', 'preprocessor_num_scaler_with_mean',
        'preprocessor_num_scaler_with_std', 'preprocessor_string_compress_type', 'FE_drop_unique_columns_flag',
        'FE_drop_constant_columns_flag', 'FE_add_frequency_columns_flag', 'FE_add_missing_indicator_columns_flag',
        'data_provenance', 'target_label_name', 'preprocessor_data_filename', 'cognito_data_filename',
        'holdout_roc_curve_max_size', 'holdout_reg_pred_obs_max_size', 'max_estimator_n_jobs',
        'enabled_feature_engineering_as_json',
        '_enable_snapml_estimators', 'return_holdout_indices', 'retrain_pipelines_on_holdout_data',
        'sampling_type', 'n_parallel_data_connections', 'calculate_data_metrics',
        'batch_size', 'metrics_on_logical_batch', 'logical_batch_size', 'text_columns_names', 'enable_all_data_sources',
        'scorer_fairness_weight'
    ]

    for k in params:
        if k not in expected_params:
            raise AdditionalParameterIsUnexpected(k)


def download_request_json(run_params: dict, model_name: str, wml_client, results_reference: 'DataConnection' = None) -> dict:
    run_id = run_params['metadata']['id']
    is_ml_metrics = 'ml_metrics' in run_params['entity']['status'].get('metrics')[-1]
    is_ts_metrics = 'ts_metrics' in run_params['entity']['status'].get('metrics')[-1]

    if not is_ml_metrics and not is_ts_metrics:
        raise NoAvailableMetrics()

    pipeline_info = run_params['entity']['status'].get('metrics')[-1]
    schema_path = f"{pipeline_info['context']['intermediate_model']['schema_location']}"
    model_number = model_name.split('_')[-1]
    if is_ml_metrics:
        model_output = chose_model_output(model_number)
    elif is_ts_metrics:
        model_output = 'after_final_pipelines_generation'

    request_path = f"{schema_path.rsplit('/data/', 1)[0]}/assets/{run_id}_P{model_number}_{model_output}/resources/wml_model/request.json"

    if wml_client.ICP:
        request_str = load_file_from_file_system(wml_client=wml_client, file_path=request_path).read().decode()
        # note: only if there was 1 estimator during training
        if 'content_location' not in request_str:
            request_path = f"{schema_path.rsplit('/data/', 1)[0]}/assets/{run_id}_P{model_number}_compose_model_type_output/resources/wml_model/request.json"
            request_str = load_file_from_file_system(wml_client=wml_client, file_path=request_path).read().decode()

    else:
        # Note: container type needs to be converted to S3 type to handle credentials!
        bucket = None
        if results_reference is not None:
            results_reference._check_if_connection_asset_is_s3()
            bucket = results_reference.location.bucket  # bucket is removed when casting to dict for Container type
            results_reference = results_reference._to_dict()

        else:
            results_reference = run_params['entity']['results_reference']
        # --- end note

        if results_reference['type'] == DataConnectionTypes.CA:
            connection_details = wml_client.connections.get_details(results_reference['connection']['id'])['entity']
            cos_client = init_cos_client(connection_details)
        else:
            cos_client = init_cos_client(results_reference['connection'])

        bucket = bucket if bucket is not None else results_reference['location']['bucket']
        cos_client.meta.client.download_file(Bucket=bucket, Filename='request.json', Key=request_path)
        with open('request.json', 'r') as f:
            request_str = f.read()

        # note: only if there was 1 estimator during training
        if 'content_location' not in request_str:
            request_path = f"{schema_path.split('/data/')[0]}/assets/{run_id}_P{model_number}_compose_model_type_output/resources/wml_model/request.json"
            cos_client.meta.client.download_file(Bucket=bucket, Filename='request.json', Key=request_path)
            with open('request.json', 'r') as f:
                request_str = f.read()

    request_json: Dict[str, dict] = json.loads(request_str)
    request_json = preprocess_request_json(request_json)

    return request_json


def is_list_composed_from_enum(sequence: List[Union[str, enum.Enum]],
                               enum_class: Union[object, enum.EnumMeta]
                               ) -> None:
    """
    Check if all the elements of a given sequence are values of a given enum class.

    Parameters
    ----------
    sequence: List[Union[str, enum.Enum]
        Sequence of elements.
    enum_class: Union[object, enum.EnumMeta]
        Class for which validation will be performed.
        It can be a class inheriting from enum.Enum or class which only contains
        attributes.

    Raises
    -------
    InvalidSequenceValue, If element is not from enum class values.
    """
    if sequence is not None:
        if isinstance(enum_class, enum.EnumMeta):
            enum_values = [e.value for e in enum_class]
        else:
            attributes = inspect.getmembers(enum_class, lambda attr: not (inspect.isroutine(attr)))
            enum_values = [attr_val for attr_name, attr_val in attributes
                           if not (attr_name.startswith('__') and attr_name.endswith('__'))]

        for el in sequence:
            el_value = el.value if isinstance(el, enum.Enum) else el
            if el_value not in enum_values:
                if f"{el_value}Estimator" not in enum_values:
                    raise InvalidSequenceValue(el, enum_values)


def validate_optimizer_enum_values(
        prediction_type: str,
        daub_include_only_estimators: List[Union[ClassificationAlgorithms,
                                                 RegressionAlgorithms,
                                                 ForecastingAlgorithms]],
        include_only_estimators: List[Union[ClassificationAlgorithms,
                                            RegressionAlgorithms,
                                            ForecastingAlgorithms]],
        cognito_transform_names: List[Transformers],
        imputation_strategies: List[ImputationStrategy],
        scoring: str,
        t_shirt_size: str,
        is_cpd=False) -> None:
    """
    Validate if passed optimizer variables takes values from defined enums.

    Parameters
    ----------
    prediction_type: str
        Type of the prediction.
    daub_include_only_estimators: list
        List of estimators.
    include_only_estimators: list
        List of estimators.
    cognito_transform_names: list
        List of transformers.
    imputation_strategies: List
        List of imputation strategies.
    scoring: str
        Type of the metric to optimize with.
    t_shirt_size: str
        The size of the remote AutoAI POD instance.
    is_cpd: bool
        True if run on CP4D environment. CP4D estimators will be used to check.

    Raises
    ------
    InvalidSequenceValue, If element is not from enum class values.
    """
    if is_cpd:
        if prediction_type == PredictionType.REGRESSION:
            estimators_enum = RegressionAlgorithmsCP4D
        elif prediction_type == PredictionType.FORECASTING:
            estimators_enum = ForecastingAlgorithmsCP4D
        else:
            estimators_enum = ClassificationAlgorithmsCP4D
    else:
        if prediction_type == PredictionType.REGRESSION:
            estimators_enum = RegressionAlgorithms
        elif prediction_type == PredictionType.FORECASTING:
            estimators_enum = ForecastingAlgorithms
        else:
            estimators_enum = ClassificationAlgorithms

    sequence_enums_pairs = [
        ([prediction_type], PredictionType),
        (daub_include_only_estimators, estimators_enum),
        (include_only_estimators, estimators_enum),
        (cognito_transform_names, Transformers),
        ([t_shirt_size], TShirtSize),
        (imputation_strategies, ImputationStrategy)
    ]
    if scoring is not None:
        sequence_enums_pairs.append(([scoring], Metrics))
    for (sequence, enum_class) in sequence_enums_pairs:
        is_list_composed_from_enum(sequence, enum_class)


def fallback_to_pip_for_version_check(package: dict) -> str:
    """Use only when you need to check package version by package name with pip."""
    try:
        from pip._internal.utils.misc import get_installed_distributions
        packages = get_installed_distributions()
        installed_module_version = None
        for pkg in packages:
            if pkg.key == package['name']:
                installed_module_version = pkg._version
                break

        if installed_module_version is None:
            raise pkg_resources.DistributionNotFound()

        else:
            return installed_module_version

    except Exception:
        raise pkg_resources.DistributionNotFound()


@contextmanager
def all_logging_disabled(highest_level=logging.CRITICAL):
    """
    A context manager that will prevent any logging messages
    triggered during the body from being processed.
    :param highest_level: the maximum logging level in use.
      This would only need to be changed if a custom level greater than CRITICAL
      is defined.
    """
    # two kind-of hacks here:
    #    * can't get the highest logging level in effect => delegate to the user
    #    * can't get the current module-level override => use an undocumented
    #       (but non-private!) interface

    previous_level = logging.root.manager.disable

    logging.disable(highest_level)

    try:
        yield
    finally:
        logging.disable(previous_level)


def check_if_ts_pipeline_is_winner(details: dict, model_name: str) -> None:
    """Check if ts pipeline is the winner one. It should be used before model store in the repo."""
    is_ts_metrics = 'ts_metrics' in details['entity']['status'].get('metrics', [{}])[0]
    if is_ts_metrics:
        summary = create_summary(details=details, scoring=None)
        summary.reset_index(inplace=True)
        vals = summary[summary['Pipeline Name'] == model_name]['Winner'].values
        if len(vals) == 0:
            raise WrongModelName(model_name)

        else:
            if not vals[0]:
                raise DiscardedModel(model_name)


def get_values_for_imputation_strategy(strategy, prediction_type, imputer_fill_value=None):
    values = {ImputationStrategy.MEAN: {'kb': 'mean',
                                        'ts': {'use_imputation': True,
                                               'imputer_list': ['Fill'],
                                               'imputer_fill_type': 'mean'}},
              ImputationStrategy.MEDIAN: {'kb': 'median',
                                          'ts': {'use_imputation': True,
                                                 'imputer_list': ['Fill'],
                                                 'imputer_fill_type': 'median'}},
              ImputationStrategy.MOST_FREQUENT: {'kb': 'most_frequent'},
              ImputationStrategy.BEST_OF_DEFAULT_IMPUTERS: {'ts': {'use_imputation': True,
                                                                   'imputer_list': ['FlattenIterative', 'Linear', 'Cubic', 'Previous']}},
              ImputationStrategy.VALUE: {'ts': {'use_imputation': True,
                                                'imputer_list': ['Fill'],
                                                'imputer_fill_type': 'value',
                                                'imputer_fill_value': imputer_fill_value if imputer_fill_value else 0}},
              ImputationStrategy.FLATTEN_ITERATIVE: {'ts': {'use_imputation': True,
                                                            'imputer_list': ['FlattenIterative']}},
              ImputationStrategy.LINEAR: {'ts': {'use_imputation': True,
                                                 'imputer_list': ['Linear']}},
              ImputationStrategy.CUBIC: {'ts': {'use_imputation': True,
                                                'imputer_list': ['Cubic']}},
              ImputationStrategy.PREVIOUS: {'ts': {'use_imputation': True,
                                                   'imputer_list': ['Previous']}},
              ImputationStrategy.NEXT: {'ts': {'use_imputation': True,
                                               'imputer_list': ['Next']}},
              ImputationStrategy.NO_IMPUTATION: {'ts': {'use_imputation': False}}}

    if type(strategy) is list: # only for ts, checked earlier
        results = [get_values_for_imputation_strategy(x, prediction_type, imputer_fill_value) for x in strategy]

        def chose_strategies(res_elements):
            indexes = [results.index(el) for el in res_elements]
            return [strategy[i] for i in indexes]

        no_imputation_res = list(filter(lambda x: not x['use_imputation'], results))
        if any(no_imputation_res) and len(strategy) > len(no_imputation_res):
            raise InconsistentImputationListElements(chose_strategies(no_imputation_res))

        result = {'use_imputation': results[0]['use_imputation'],
                  'imputer_list': [x for r in results for x in r['imputer_list']]}

        fill_type_imputation_res = list(filter(lambda x: 'imputer_fill_type' in x, results))
        fill_value_imputation_res = list(filter(lambda x: 'imputer_fill_value' in x, results))

        if len(fill_type_imputation_res) > 1:
            raise InconsistentImputationListElements(chose_strategies(fill_type_imputation_res))
        elif len(fill_type_imputation_res) == 1:
            result['imputer_fill_type'] = fill_type_imputation_res[0]['imputer_fill_type']

        if len(fill_value_imputation_res) > 1:
            raise InconsistentImputationListElements(chose_strategies(fill_value_imputation_res))
        elif len(fill_value_imputation_res) == 1:
            result['imputer_fill_value'] = fill_type_imputation_res[0]['imputer_fill_value']

        return result

    v = values[strategy]

    if prediction_type == PredictionType.FORECASTING:
        if 'ts' not in v:
            l = ['ImputationStrategy.' + s.name for s in ImputationStrategy if values[s].get('ts')]
            raise StrategyIsNotApplicable(strategy, prediction_type, l)

        return v['ts']
    else:
        if 'kb' not in v:
            l = ['ImputationStrategy.' + s.name for s in ImputationStrategy if values[s].get('kb')]
            raise StrategyIsNotApplicable(strategy, prediction_type, l)

        return v['kb']


def translate_imputation_string_strategy_to_enum(strategy, prediction_type):
    if type(strategy) is list and prediction_type == PredictionType.FORECASTING:
        if 'Fill' in strategy:
            strategy.remove('Fill')
        return [translate_imputation_string_strategy_to_enum(x, prediction_type) for x in strategy]

    strategy = re.sub(r'(?<!^)(?=[A-Z])', '_', strategy).lower()

    return ImputationStrategy(strategy)
