# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Context manager that wraps an AutoML run context."""
from typing import Any, Callable, cast, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
from contextlib import contextmanager
from tempfile import NamedTemporaryFile, TemporaryDirectory
import json
import logging
import os
import pickle
import re
import shutil
import sklearn

from .onnx_convert import OnnxConverter
from azureml._common._error_definition import AzureMLError
from azureml._restclient.constants import RUN_ORIGIN
from azureml.automl.core.shared import constants, exceptions, logging_utilities, reference_codes
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AutoMLInternal
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.pickler import DefaultPickler
from azureml.automl.core._run import RunType
import azureml.automl.core.inference as inference

# Timeout in seconds for artifact upload
ARTIFACT_UPLOAD_TIMEOUT_SECONDS = 1200
logger = logging.getLogger(__name__)

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    has_mlflow = True
except ImportError:
    has_mlflow = False

logger = logging.getLogger(__name__)


class AutoMLAbstractRunContext(ABC):
    """Wrapper class for an AutoML run context."""

    def __init__(self):
        """Initialize the run context wrapper."""
        self._run_id = None  # type: Optional[str]
        self._uploaded_artifacts = None  # type: Optional[Dict[str, Any]]
        self._model_sizes = {}  # type: Dict[str, int]
        self._pickler = DefaultPickler()

    @abstractmethod
    def _get_run_internal(self) -> RunType:
        """Retrieve the run context. Must be overridden by subclasses."""
        raise NotImplementedError  # PII safe to raise directly

    def set_local(self, local: bool) -> None:
        """
        Set whether this run is local or not.

        :param local: Whether this run is local or not
        """
        with self.get_run() as run:
            run._is_local_run = local

    @property
    def parent_run_id(self) -> str:
        """
        Get the parent run id for this execution context, or the run id if this is a parent run.

        :return: the parent run id
        """
        match = re.fullmatch(r'(.*?)_(?:setup|[0-9]+)', self.run_id)
        if match is None:
            return self.run_id
        return match.group(1)

    @property
    def run_id(self) -> str:
        """
        Get the run id associated with the run wrapped by this run context. The run id is assumed to be immutable.

        :return: the run id
        """
        if self._run_id is None:
            with self.get_run() as run:
                self._run_id = run.id
        return cast(str, self._run_id)

    @contextmanager
    def get_run(self):
        """
        Yield a run context.

        Wrapped by contextlib to convert it to a context manager. Nested invocations will return the same run context.
        """
        yield self._get_run_internal()

    def save_model_output(self, fitted_pipeline: Any, remote_path: str, working_dir: str) -> None:
        """
        Save the given fitted model to the given path using this run context.

        :param fitted_pipeline: the fitted model to save
        :param remote_path: the path to save to
        """
        logger.info("Saving models.")
        self._save_model(fitted_pipeline, remote_path, self._save_python_model, working_dir, save_model_path=True)

    def save_onnx_model_output(self, onnx_model: object, remote_path: str, working_dir: str) -> None:
        """
        Save the given onnx model to the given remote path using this run context.

        :param onnx_model: the onnx model to save
        :param remote_path: the path to save to
        """
        self._save_model(onnx_model, remote_path, self._save_onnx_model, working_dir)

    def save_onnx_model_resource(self, onnx_resource: Dict[Any, Any], remote_path: str, working_dir: str) \
            -> None:
        """
        Save the given onnx model resource to the given remote path using this run context.

        :param onnx_resource: the onnx model resource dict to save
        :param remote_path: the path to save to
        """
        self._save_file(onnx_resource, remote_path, False, self._save_dict_to_json_output, working_dir)

    def _save_model(self, model_object: Any, remote_path: str,
                    serialization_method: "Callable[[Any], None]",
                    working_directory: Optional[str],
                    save_model_path: bool = False) -> None:
        self._save_file(model_object, remote_path, binary_mode=True, serialization_method=serialization_method,
                        working_directory=working_directory, save_model_path=save_model_path)

    def _save_file(self, save_object: Any, remote_path: str, binary_mode: bool,
                   serialization_method: "Callable[[Any], None]",
                   working_directory: str,
                   save_model_path: bool = False) -> None:
        if binary_mode:
            write_mode = "wb+"
        else:
            write_mode = "w+"
        output = None
        try:
            # Get the suffix of the model path, e.g. 'outputs/model.pt' will get '.pt'.
            _, suffix = os.path.splitext(remote_path)
            # Init the temp file with correct suffix.
            output = NamedTemporaryFile(mode=write_mode, suffix=suffix, delete=False, dir=working_directory)
            serialization_method(save_object, output)
            with self.get_run() as run_object:
                if save_model_path:
                    # Save the property of the remote model path.
                    run_object.add_properties({
                        constants.PROPERTY_KEY_OF_MODEL_PATH: remote_path
                    })
                artifact_response = run_object.upload_file(remote_path, output.name)
                if artifact_response:
                    self._uploaded_artifacts = artifact_response.artifacts
        finally:
            if output is not None:
                output.close()
                try:
                    os.unlink(output.name)
                except PermissionError as e:
                    DeleteFileException = exceptions.DeleteFileException.from_exception(
                        e,
                        target="_save_file",
                        reference_code=reference_codes.ReferenceCodes._DELETE_FILE_PERMISSION_ERROR
                    ).with_generic_msg("PermissionError while cleaning up temp file.")
                    logging_utilities.log_traceback(DeleteFileException, logger)

    def _get_artifact_id(self, artifact_path: str) -> str:
        """
        Parse the run history response message to get the artifact ID.

        :param artifact_path: the path to artifact
        :return: the composed artifact ID string
        """
        try:
            if self._uploaded_artifacts and self._uploaded_artifacts.get(artifact_path) is not None:
                return cast(str, inference.AMLArtifactIDHeader
                            + self._uploaded_artifacts[artifact_path].artifact_id)
            else:
                return ""
        except Exception:
            return ""

    def _get_artifact_id_run_properties(self):
        properties = {
            inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation:
                self._get_artifact_id(constants.CONDA_ENV_FILE_PATH),
            inference.AutoMLInferenceArtifactIDs.ModelDataLocation:
                self._get_artifact_id(constants.MODEL_PATH),
            inference.AutoMLInferenceArtifactIDs.ModelSizeOnDisk:
                str(self._model_sizes.get(constants.MODEL_PATH, '')),
            inference.AutoMLInferenceArtifactIDs.ScoringDataLocation:
                self._get_artifact_id(constants.SCORING_FILE_PATH),
            inference.AutoMLInferenceArtifactIDs.ScoringDataLocationV2:
                self._get_artifact_id(constants.SCORING_FILE_V2_PATH)
        }
        return properties

    def _save_onnx_model(self, model_object: Any, model_output) -> None:
        OnnxConverter.save_onnx_model(model_object, model_output.name)

    def _save_python_model(self, model_object: Any, model_output) -> None:
        with(open(model_output.name, 'wb')):
            _, ext = os.path.splitext(model_output.name)
            if ext == '.pt' or ext == '.pth':
                try:
                    import torch
                    torch.save(model_object, model_output)
                except Exception:
                    self._pickler.dump(model_object, model_output.name, model_output)
            else:
                self._pickler.dump(model_object, model_output.name, model_output)
            model_output.flush()

    def _save_mlflow_model(self, fitted_pipeline: Any, remote_path: str, working_dir: str, is_transformer: bool) \
            -> Tuple[List[str], List[str]]:
        """
        Save the model in mlflow format.

        :param fitted_pipeline: The model to be saved.
        :param remote_path: The remote path to save this model under.
        :param working_dir: The local working directory to save the models in before uploading.
        :return: None
        """
        try:
            import torch
            is_torch = isinstance(fitted_pipeline, torch.nn.Module)
        except Exception:
            is_torch = False

        run = self._get_run_internal()
        output_dir = os.path.join(working_dir, remote_path)

        # Improving this behavior with 1440665
        env = run.get_environment()
        cd = env.python.conda_dependencies._conda_dependencies if env and env.python.conda_dependencies else None

        logger.info("Saving MLFlow model.")

        if is_transformer:
            logger.info("Saving data transformer as ML model to {}.".format(output_dir))
            mlflow.sklearn.save_model(
                sk_model=fitted_pipeline,
                path=output_dir,
                conda_env=cd,
                serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_PICKLE)
        elif isinstance(fitted_pipeline, sklearn.pipeline.Pipeline):
            logger.info("Saving sklearn model to {}.".format(output_dir))
            mlflow.sklearn.save_model(
                sk_model=fitted_pipeline,
                path=output_dir,
                conda_env=cd,
                serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_PICKLE)
        elif is_torch:
            logger.info("Saving pytorch model to {}.".format(output_dir))
            mlflow.pytorch.save_model(
                pytorch_model=fitted_pipeline,
                path=output_dir,
                conda_env=cd,
                pickle_module=pickle)
        else:
            message = "Unknown model type could not be saved with mlflow."
            raise ClientException._with_error(
                AzureMLError.create(AutoMLInternal, target="save_mlflow", error_details=message)
            )

        local_paths = []
        remote_paths = []

        files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(output_dir) for f in filenames]
        for filename in files:
            local_paths.append(filename)
            filename_stub = filename.split(remote_path)[-1][1:]  # chop off temp directory and leading slash
            remote_paths.append(os.path.join(remote_path, filename_stub))

        return local_paths, remote_paths

    def _save_str_output(self, str_object: Any, output) -> None:
        with open(output.name, "w") as f:
            f.write(str_object)

    def _save_dict_to_json_output(self, dict_object: Dict[Any, Any], output) -> None:
        with open(output.name, 'w') as f:
            json.dump(dict_object, f)

    def save_str_output(self, input_str: str, remote_path: str,
                        overwrite_mode: bool = False,
                        working_directory: Optional[str] = None) -> None:
        """
        Save the str file as a txt into the Artifacts.

        :param input_str: the input string.
        :param remote_path: the file name in the Artifacts.
        """
        self._save_file(input_str, remote_path, binary_mode=False,
                        serialization_method=self._save_str_output, working_directory=working_directory)

    def batch_save_artifacts(self,
                             working_directory: Optional[str],
                             input_strs: Dict[str, str],
                             model_outputs: Dict[str, Any],
                             save_as_mlflow: bool = False,
                             is_transformer: bool = False) -> None:
        """
        Save a batch of text files and models into the Artifacts.
        This is more efficient than saving individual artifacts.

        :param working_directory: Directory to use for temporary storage.
        :param input_strs: Dictionary of strings. The key is the artifact name and the value is the content.
        :param model_outputs: Dictionary of models. The key is the artifact name and the value is the model.
        :param save_as_mlflow: Flag for whether to save using MLFlow to save the model.
        :param is_transformer: Flag to check if model_outputs contain data tranformer.
        """
        temp_resources = []
        file_keys = []
        file_paths = []

        try:
            if save_as_mlflow and not has_mlflow:
                logger.warning("MLFlow is not present in the current environment. Can't save MLFlow models and "
                               "defaulting back to pickle.")
                save_as_mlflow = False

            for name, contents in input_strs.items():
                text_file = NamedTemporaryFile(mode="w", delete=False, dir=working_directory)
                self._save_str_output(contents, text_file)
                temp_resources.append(text_file)
                file_keys.append(name)
                file_paths.append(text_file.name)

            for name, model in model_outputs.items():
                # Get the suffix of the model path, e.g. 'outputs/model.pt' will get '.pt'.
                _, suffix = os.path.splitext(name)
                # Init the temp file with correct suffix.
                should_save_mlflow = save_as_mlflow and not isinstance(model, list)
                if should_save_mlflow:
                    try:
                        td = TemporaryDirectory(dir=working_directory)
                        temp_resources.append(td)
                        remote_path = constants.MLFLOW_FEATURIZATION_OUTPUT \
                            if is_transformer else constants.MLFLOW_OUTPUT_PATH
                        mlflow_files, mlflow_paths = \
                            self._save_mlflow_model(model, remote_path, td.name, is_transformer)
                        file_keys.extend(mlflow_paths)
                        file_paths.extend(mlflow_files)
                    except Exception as e:
                        should_save_mlflow = False
                        logger.warn("Failed when saving mlflow model with {}.".format(type(e)))
                if not should_save_mlflow:
                    model_file = NamedTemporaryFile(mode="wb", suffix=suffix, delete=False, dir=working_directory)
                    self._save_python_model(model, model_file)
                    self._model_sizes[name] = os.path.getsize(model_file.name)
                    temp_resources.append(model_file)
                    file_keys.append(name)
                    file_paths.append(model_file.name)

            self._batch_save_artifact_files(file_keys, file_paths)
        finally:
            for f in temp_resources:
                if isinstance(f, TemporaryDirectory):
                    f.cleanup()
                else:
                    f.close()
                    try:
                        os.unlink(f.name)
                    except PermissionError as e:
                        delete_file_exception = exceptions.DeleteFileException.from_exception(
                            e,
                            target="batch_save_artifacts",
                            reference_code=reference_codes.ReferenceCodes._DELETE_FILE_BATCH_PERMISSION_ERROR
                        ).with_generic_msg("PermissionError while cleaning up temp file.")
                        logging_utilities.log_traceback(delete_file_exception, logger)

    def _batch_save_artifact_files(self, file_keys: List[str], file_paths: List[str]) -> None:
        """
        Save a batch of files in artifact store.
        Batch uploading files is more efficient than uploading files one by one.
        """
        with self.get_run() as run_object:
            # Save the property of the remote model path.
            remote_model_path = ''
            if constants.MODEL_PATH in file_keys:
                # Save the model.pkl file
                remote_model_path = constants.MODEL_PATH
            elif constants.PT_MODEL_PATH in file_keys:
                # Save the model.pt file
                remote_model_path = constants.PT_MODEL_PATH
            run_object.add_properties({
                constants.PROPERTY_KEY_OF_MODEL_PATH: remote_model_path
            })

            upload_response = run_object.upload_files(file_keys, file_paths, return_artifacts=True,
                                                      timeout_seconds=ARTIFACT_UPLOAD_TIMEOUT_SECONDS)
            if upload_response:
                self._uploaded_artifacts = upload_response[0]

    def _register_mlflow_model(self):
        """
        Register the manually saved model so that we can use models:/ URI to fetch it.

        :return: ModelVersion
        """
        client = MlflowClient()
        child_run = self._get_run_internal()
        mlflow_run = client.get_run(child_run.id)

        model_name = child_run.id
        model_desc = "AutoML trained model."
        model_source_uri = '{}/outputs'.format(mlflow_run.info.artifact_uri)

        logger.info("Registering model found at {}.".format(model_source_uri))
        client.create_registered_model(model_name)
        model = client.create_model_version(model_name, model_source_uri, child_run.id, description=model_desc)
        logger.info("Registered model to models:/{}/{}".format(model.name, model.version))
        return model
