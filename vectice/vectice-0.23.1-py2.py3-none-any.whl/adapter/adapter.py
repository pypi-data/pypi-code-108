from __future__ import annotations

import logging
import os
import time

from abc import abstractmethod, ABC
from typing import List, Optional, Any, Dict, Sequence, Tuple, Union

from vectice.api import Client, Page
from vectice.api.json_object import JsonObject
from vectice.api.output import JobOutput, JobRunOutput, PagedResponse
from vectice.api.output.attachments_output import AttachmentOutput
from vectice.api.output.connection_output import ConnectionOutput
from vectice.api.output.dataset_output import DatasetOutput
from vectice.api.output.dataset_version_output import DatasetVersionOutput
from vectice.api.output.model_output import ModelOutput
from vectice.api.output.model_version_output import ModelVersionOutput
from vectice.entity.model import ModelType
from vectice.models import (
    Artifact,
    ArtifactType,
    RunnableJob,
    Job,
    JobRun,
    JobRunStatus,
    DatasetVersionArtifact,
    Artifacts,
    ModelVersion,
    ModelVersionArtifact,
    CodeVersionArtifact,
    DataResource,
    CreateDataset,
    Attachments,
    UpdateModelVersion,
    DatasetMetadataArtifact,
)
from vectice.utils.artifact_api_utils import get_artifact_id, get_artifact_version_id, update_artifact_properties


# TODO implement TypeAlias when we use python 3.10 e.g list_model_version_dataframe -> DataFrame
# DataFrame: TypeAlias = "DataFrame"


class AbstractAdapter(ABC):
    @property
    @abstractmethod
    def active_runs(self) -> Dict[int, ActiveRun]:
        pass

    @abstractmethod
    def create_run(self, name: str) -> RunnableJob:
        pass

    @abstractmethod
    def end_run(
        self, run: ActiveRun, outputs: Optional[List[Artifact]] = None, status: str = JobRunStatus.COMPLETED
    ) -> Optional[int]:
        pass

    @abstractmethod
    def start_run(self, run: RunnableJob, inputs: Optional[List[Artifact]] = None) -> ActiveRun:
        pass

    @abstractmethod
    def save_job_and_associated_runs(self, name: str) -> None:
        pass

    @abstractmethod
    def save_run(
        self,
        run: Any,
        inputs: Optional[List[Artifact]] = None,
        outputs: Optional[List[Artifact]] = None,
    ) -> Optional[int]:
        pass

    @abstractmethod
    def run_failed(self, run: Optional[ActiveRun] = None):
        pass


class ActiveRun:
    """Wrapper around dict response to enable using Python ``with`` syntax."""

    _outputs: Optional[List[Artifact]]
    _adapter: AbstractAdapter
    _job: JsonObject
    _run: JsonObject
    _inputs: JsonObject

    def __init__(self, job: JsonObject, run: JsonObject, inputs: JsonObject, adapter: AbstractAdapter):
        self._adapter = adapter
        self._job = job
        self._run = run
        self._inputs = inputs
        self._outputs = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def __enter__(self) -> ActiveRun:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        status = JobRunStatus.COMPLETED if exc_type is None else JobRunStatus.FAILED
        try:
            self._adapter.end_run(self, status=status)
        except Exception as e:
            self._adapter.run_failed(self)
            self._logger.warning(f"Run failed because {e}")
        finally:
            return exc_type is None

    @property
    def outputs(self) -> Optional[List[Artifact]]:
        return self._outputs

    @property
    def run(self) -> JsonObject:
        return self._run

    @property
    def job(self) -> JsonObject:
        return self._job

    def add_output(self, output: Artifact):
        if self._outputs is None:
            self._outputs = []
        self._outputs.append(output)

    def add_outputs(self, outputs: List[Artifact]):
        if len(outputs) > 0:
            if self._outputs is None:
                self._outputs = []
            self._outputs.extend(outputs)


class Adapter(AbstractAdapter):
    def __init__(
        self,
        project_token: str,
        auto_connect: bool = True,
        autocode: bool = False,
        allow_self_signed_certificate: bool = True,
    ):
        self._client = Client(project_token, auto_connect, allow_self_signed_certificate)
        self._active_runs: Dict[int, ActiveRun] = {}
        self._last_created_run: Optional[RunnableJob] = None
        self._last_started_run: Optional[ActiveRun] = None
        self._logger = logging.getLogger(self.__class__.__name__)
        self.autocode = autocode
        try:
            self._client.auth_project_token(project_token)
        except Exception:
            raise ValueError(
                "The entered token is invalid. Please check the entered value. You may find and copy a Project Token directly under the Settings menu, on your Project"
            )
        self._vectice_path = self._client.vectice_path

    @property
    def active_runs(self) -> Dict[int, ActiveRun]:
        return self._active_runs

    @property
    def vectice_path(self) -> Optional[str]:
        """
        Returns the project and workspace being used.

        :return: A string of the Vectice path
        """
        self._logger.info(self._vectice_path)
        return self._vectice_path

    def get_current_runnable_job(self, run: Optional[RunnableJob] = None) -> RunnableJob:
        if run is not None:
            result: RunnableJob = run
        else:
            if self._last_created_run is None:
                raise RuntimeError("A job context must have been created.")
            else:
                result = self._last_created_run
        return result

    def start_run(self, run: Optional[RunnableJob] = None, inputs: Optional[List[Artifact]] = None) -> ActiveRun:
        """
        Start the run created before by calling :func:`~Vectice.create_run` function

        :param run: The runnable job to start
        :param inputs: A list of artifacts used as inputs by this run.
        :return: A reference to a run in progress
        """

        run = self.get_current_runnable_job(run)
        code_artifact_is_present = False
        artifact_name, attachments = None, None
        if inputs is not None:
            for an_input in inputs:
                if an_input is not None:
                    an_input.jobArtifactType = "INPUT"
                    code_artifact_is_present = code_artifact_is_present or an_input.artifactType == ArtifactType.CODE
                    artifact_name, attachments = self._parse_attachments(an_input)
        if not code_artifact_is_present and self.autocode:
            if inputs is None:
                inputs = []
            artifact = CodeVersionArtifact.create(".")
            if artifact is not None:
                inputs.append(artifact)

        response = self._client.start_run(run, inputs)
        if attachments and attachments.files:
            self._save_attachments(artifact_name, attachments)
        active_run = ActiveRun(response["job"], response["jobRun"], response["jobArtifacts"], self)
        self._active_runs[active_run.run["id"]] = active_run
        self._last_started_run = active_run
        return active_run

    def _get_current_active_run(self, run: Optional[ActiveRun] = None) -> ActiveRun:
        if run is not None:
            result: ActiveRun = run
        else:
            if self._last_started_run is None:
                raise RuntimeError("A job context must have been created.")
            else:
                result = self._last_started_run
        return result

    def end_run(
        self,
        run: Optional[ActiveRun] = None,
        outputs: Optional[List[Artifact]] = None,
        status: str = JobRunStatus.COMPLETED,
    ) -> Optional[int]:
        """
        End the current (last) active run started by :func:`~Vectice.start_run`.
        To end a specific run, use :func:`~Vectice.stop_run` instead.

        :return: Identifier of the run in Vectice if successfully saved
        """
        run = self._get_current_active_run(run)
        artifact_name, attachments = None, None
        if outputs is not None:
            run.add_outputs(outputs)
        if run.outputs is not None:
            for an_output in run.outputs:
                if an_output is not None:
                    artifact_name, attachments = self._parse_attachments(an_output)
                    an_output.jobArtifactType = "OUTPUT"
        run.run["status"] = status
        self._client.stop_run(run.run, run.outputs)
        if attachments and attachments.files:
            self._save_attachments(artifact_name, attachments)
        if "id" in run.run:
            run_id: Optional[int] = int(run.run["id"])
        else:
            run_id = None
        del self._active_runs[run.run["id"]]
        return run_id

    # TODO Update to handle more artifactTypes
    def _save_attachments(self, artifact_name: Optional[str], attachments: Attachments):
        try:
            model_id = self.list_models(artifact_name).list[0].id
            version_id = self.list_model_versions(model_id).list[0].id
            self._client.create_attachments("modelversion", version_id, files=attachments.files)
        except Exception as e:
            self._logger.warning(f"Attachments failed to upload due to {e}")

    @staticmethod
    def _parse_attachments(an_input: Optional[Artifact] = None):
        artifact_name, attachments = None, None
        if isinstance(an_input, ModelVersionArtifact) and an_input.artifactType == ArtifactType.MODEL:
            attachments = an_input.attachments
            artifact_name = an_input.model.parentName
            # remove attachments from payload to avoid any unwanted behaviour
            an_input.attachments = Attachments(None, None)
        return artifact_name, attachments

    def __save_run(
        self,
        run: Optional[RunnableJob] = None,
        inputs: Optional[List[Artifact]] = None,
        outputs: Optional[List[Artifact]] = None,
    ) -> Optional[int]:
        if run is None:
            run = self._last_created_run
        active_run = self.start_run(run, inputs)
        return self.end_run(active_run, outputs)

    def save_job_and_associated_runs(self, name: str) -> None:
        raise RuntimeError("No implementation for this library")

    def save_run(
        self,
        run: Any,
        inputs: Optional[List[Artifact]] = None,
        outputs: Optional[List[Artifact]] = None,
    ) -> Optional[int]:
        """
        Save run with its associated inputs and outputs

        :param run: The run we want to save
        :param inputs: A list of inputs (artifacts) you are using in this run
        :param outputs: A list of outputs (artifacts) you are using in this run
        :return: Identifier of the run in Vectice if successfully saved
        """
        if isinstance(run, RunnableJob):
            return self.__save_run(run, inputs, outputs)
        else:
            raise RuntimeError("Incompatible object provided.")

    def create_run(self, job_name: str, job_type: Optional[str] = None, run_name: Optional[str] = None) -> RunnableJob:
        """
        Create an instance of a future run of a job.
        The run is not started.
        You need to start it by calling start_run

        :param job_type: The type of the job. see :class:`~vectice.models.JobType` for the list of accepted type.
        :param job_name: The name of the job that should run.
        :param run_name: The name of the run.
        :return: An instance of a non started run.
        """
        if job_name is None:
            raise RuntimeError("Job name must be set")
        self._last_created_run = RunnableJob(Job(job_name, job_type), JobRun(name=run_name))
        return self._last_created_run

    def run_failed(self, run: Optional[ActiveRun] = None):
        """
        Indicates that the run failed
        """
        self.__update_run_status(run, JobRunStatus.FAILED)

    def run_aborted(self, run: Optional[ActiveRun] = None):
        """
        Indicates that the run was aborted by the user
        """
        self.__update_run_status(run, JobRunStatus.ABORTED)

    def __update_run_status(self, active_run: Optional[ActiveRun], status: str):
        try:
            active_run = self._get_current_active_run(active_run)
            active_run.run["status"] = status
            self._client.update_run(active_run.job["id"], active_run.run["id"], active_run.run)
        except RuntimeError:
            logging.error("run failed to start.")

    @staticmethod
    def setup_api_token(token_file: str, api_endpoint: Optional[str] = None) -> None:
        """
        Parses the the API Token json file and sets the os environmental variable for the "VECTICE_API_TOKEN"
        for the user.

        :param token_file: The filepath to the json file containing the "VECTICE_API_TOKEN", found on the Vectice App
        :param api_endpoint: The api endpoint used to connect to the Vectice App
        :return: None
        """
        try:
            token = Artifacts.parse_api_token(token_file)
        except Exception as e:
            raise RuntimeError(f"File failed to parse: {e}")
        logging.info("Api token json file Parsed!")
        if api_endpoint:
            os.environ["VECTICE_API_ENDPOINT"] = api_endpoint
        Client.auth_api_token(api_token=token.key, api_endpoint=api_endpoint)
        os.environ["VECTICE_API_TOKEN"] = token.key
        logging.info(f"{token.name} parsed and configured!")

    def list_jobs(
        self, search: Optional[str] = None, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[JobOutput]:
        """
        List all jobs

        :param search: A text to filter jobs base on their name
        :param page_index: The index of the page we want
        :param page_size: The size of the page we want
        :return: A list of filtered jobs
        """
        return self._client.list_jobs(search, page_index, page_size)

    def list_runs(self, job_id: int, page_index=Page.index, page_size=Page.size) -> Sequence[JobRunOutput]:
        """
        List all run of a specific job

        :param job_id: The Vectice job identifier
        :param page_index: The index of the page we want
        :param page_size: The size of the page we want
        :return: A list of runs
        """
        return self._client.list_runs(job_id, page_index, page_size)

    def create_dataset(
        self,
        dataset_name: str,
        data_properties: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None,
    ) -> Optional[int]:
        """
        create a new dataset without a connection.

        :param dataset_name: the dataset name
        :param data_properties: the properties added to the dataset version, accepts either a tuple eg. (key, value) or a list of tuples with multiple properties eg. [(key, value), (key, value)]
        :return: identifier of the created dataset
        """
        dataset, dataset_id = None, None
        created_dataset = CreateDataset(name=dataset_name).add_properties(data_properties=data_properties).as_dict()
        dataset = self._client.create_dataset({"name": created_dataset["name"], "pattern": "*"})
        dataset_id = int(dataset["id"])
        if created_dataset.get("properties"):
            self._client.create_dataset_version(dataset_id=int(dataset["id"]), dataset_version=created_dataset)
        self._logger.info(f"Dataset: {dataset_name} has been successfully created.")
        return dataset_id

    def create_dataset_with_connection_id(
        self,
        connection_id: int,
        dataset_name: str,
        files: Optional[List[str]],
        folders: Optional[List[str]] = None,
        data_properties: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None,
    ) -> Optional[int]:
        """
        create a new dataset linked to the connection with associated items in it
        :param connection_id: the connection identifier
        :param dataset_name: the dataset name
        :param files: the list of files to be set in the dataset
        :param folders: the list of folders to be set in the dataset
        :param data_properties: the properties added to the dataset, accepts either a tuple eg. (key, value) or a list of tuples with multiple properties eg. [(key, value), (key, value)]
        :return: identifier of the created dataset
        """
        dataset_version_id, dataset, dataset_id = None, None, None
        data_resources = DataResource.create_resources(files, folders)
        created_dataset = (
            CreateDataset(name=dataset_name, connectionId=connection_id, files=files, folders=folders)
            .add_properties(data_properties=data_properties)
            .as_dict()
        )
        if data_resources:
            dataset = self._client.create_dataset(
                {
                    "name": created_dataset["name"],
                    "connectionId": created_dataset["connectionId"],
                    "dataResources": data_resources,
                }
            )
            time.sleep(1)
            dataset_id = int(dataset["id"])
            dataset_version_id = self._client.list_dataset_versions(dataset_id=int(dataset["id"])).list[0].id
        elif not data_resources:
            dataset = self._client.create_dataset(
                {"name": created_dataset["name"], "connectionId": created_dataset["connectionId"]}
            )
            dataset_id = int(dataset["id"])
            if created_dataset.get("properties"):
                self._client.create_dataset_version(dataset_id=int(dataset["id"]), dataset_version=created_dataset)
        if dataset and dataset_version_id and dataset_id and created_dataset.get("properties"):
            self._client.create_dataset_version_properties(
                dataset_id=dataset_id, dataset_version_id=dataset_version_id, properties=created_dataset["properties"]
            )
        self._logger.info(f"Dataset: {dataset_name} has been successfully created.")
        return dataset_id

    def create_dataset_with_connection_name(
        self,
        connection_name: str,
        dataset_name: str,
        files: Optional[List[str]],
        folders: Optional[List[str]] = None,
        data_properties: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None,
    ) -> Optional[int]:
        """
        create a new dataset linked to the connection with associated items in it
        :param connection_name: the connection name
        :param dataset_name: the dataset name
        :param files: the list of files to be set in the dataset
        :param folders: the list of folders to be set in the dataset
        :param data_properties: the properties added to the dataset, accepts either a tuple eg. (key, value) or a list of tuples with multiple properties eg. [(key, value), (key, value)]
        :return: identifier of the created dataset
        """
        dataset_version_id, dataset, dataset_id = None, None, None
        data_resources = DataResource.create_resources(files, folders)
        created_dataset = (
            CreateDataset(name=dataset_name, connectionName=connection_name, files=files, folders=folders)
            .add_properties(data_properties=data_properties)
            .as_dict()
        )
        if data_resources:
            dataset = self._client.create_dataset(
                {
                    "name": created_dataset["name"],
                    "connectionName": created_dataset["connectionName"],
                    "dataResources": data_resources,
                }
            )
            time.sleep(1)
            dataset_id = int(dataset["id"])
            dataset_version_id = self._client.list_dataset_versions(dataset_id=int(dataset["id"])).list[0].id
        elif not data_resources:
            dataset = self._client.create_dataset(
                {"name": created_dataset["name"], "connectionName": created_dataset["connectionName"]}
            )
            dataset_id = int(dataset["id"])
            if created_dataset.get("properties"):
                self._client.create_dataset_version(dataset_id=int(dataset["id"]), dataset_version=created_dataset)
        if dataset and dataset_version_id and dataset_id and created_dataset.get("properties"):
            self._client.create_dataset_version_properties(
                dataset_id=dataset_id, dataset_version_id=dataset_version_id, properties=created_dataset["properties"]
            )
        self._logger.info(f"Dataset: {dataset_name} has been successfully created.")
        return dataset_id

    @classmethod
    def create_dataset_version(cls, description: Optional[str] = None) -> DatasetVersionArtifact:
        """
        Create an artifact that contains a version of a dataset

        :param description: A description of the dataset version
        :return: A dataset version artifact
        """
        return Artifacts.create_dataset_version(description)

    def update_dataset(
        self, dataset_name: Optional[str] = None, dataset_id: Optional[int] = None, notes: Optional[str] = None
    ):
        """
        Update a dataset associated with the provided dataset name or dataset id.

        :param dataset_name: The name of the dataset to be updated
        :param dataset_id: The dataset id of the dataset to be updated
        :param notes: The dataset notes
        :return: None
        """
        dataset = None
        try:
            if dataset_name:
                dataset = self._client.list_datasets(dataset_name).list[0]
                dataset_id = dataset.id
                dataset.description = notes
            if dataset_id:
                dataset = [dataset for dataset in self._client.list_datasets().list if dataset.id == dataset_id][0]
                dataset_id = dataset.id
                dataset.description = notes
                self._client.update_dataset(dataset_id=dataset_id, dataset=dataset.__dict__)
                self._logger.info(f"Dataset '{dataset_name or dataset_id}' has been updated successfully")
        except Exception as e:
            raise ValueError(f"Dataset could not be updated due to {e}")

    def update_dataset_version(
        self,
        dataset_name: Optional[str] = None,
        dataset_id: Optional[int] = None,
        dataset_version_number: Optional[int] = None,
        dataset_version_id: Optional[int] = None,
        notes: Optional[str] = None,
        properties: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None,
    ):
        """
        Update a dataset version associated with the provided dataset name or dataset id and the dataset version number or dataset version id.

        properties can be as follows: [("key", "value"), ("key", "value")] or ("key", "value")

        :param dataset_name: The name of the dataset to be updated
        :param dataset_id: The dataset id of the dataset to be updated
        :param dataset_version_number: The dataset version number of the dataset to be updated
        :param dataset_version_id: The dataset version id of the dataset version to be updated
        :param notes: The dataset notes
        :param properties: The properties of the dataset to be updated or added
        :return: None
        """
        dataset = CreateDataset().add_properties(data_properties=properties).as_dict()
        try:
            if dataset_name:
                dataset_id = get_artifact_id(client=self._client, artifact_name=dataset_name)
            if dataset_version_number and dataset_id:
                dataset_version_id = get_artifact_version_id(
                    client=self._client, artifact_id=dataset_id, version_number=dataset_version_number
                )
            if dataset_id and dataset_version_id:
                if notes is not None:
                    self._client.update_dataset_version(
                        dataset_id=dataset_id,
                        dataset_version_id=dataset_version_id,
                        dataset_version={"description": notes},
                    )
                if dataset.get("properties"):
                    update_artifact_properties(self._client, dataset_id, dataset_version_id, dataset)
            self._logger.info(f"Dataset '{dataset_name or dataset_id}' has been updated successfully")
        except Exception as e:
            raise RuntimeError(f"Dataset version could not be updated due to {e}")

    def list_datasets(
        self, search: str = None, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[DatasetOutput]:
        """
        list datasets

        :param search:
        :param page_index:
        :param page_size:
        :return:
        """
        return self._client.list_datasets(search, page_index, page_size)

    def list_dataset_versions(
        self, dataset_id: int, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[DatasetVersionOutput]:
        """

        :param dataset_id:
        :param page_index:
        :param page_size:
        :return:
        """
        return self._client.list_dataset_versions(dataset_id, page_index, page_size)

    @classmethod
    def create_model_version(cls, description: Optional[str] = None) -> ModelVersionArtifact:
        """
        Create an artifact that contains a version of a model

        :param description: A description of the model version
        :return: A model version artifact
        """
        return Artifacts.create_model_version(description)

    def update_model(
        self,
        model_id: Optional[int] = None,
        parent_name: Optional[str] = None,
        model_type: Optional[Union[ModelType, str]] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Updates a model at the higher level and not the model version.

        :param model_id: The model's id
        :param parent_name: The model's name
        :param model_type: The model type e.g CLASSIFICATION, REGRESSION etc
        :param description: A description of the model
        :return: None
        """
        if not model_id:
            try:
                model_id = self._client.list_models(parent_name).list[0].id
            except Exception:
                raise ValueError(f"The model '{parent_name}' could not be found")
        if model_type:
            try:
                model_type = ModelVersionArtifact(ModelVersion(), Attachments()).with_type(model_type).model.type
            except Exception:
                raise ValueError(f"The model type of '{model_type}' isn't supported.")
        self._client.update_model(model_id, {"type": model_type, "description": description})
        model_identifier = parent_name if parent_name else model_id
        self._logger.info(f"Model: '{model_identifier}' has been updated")

    def update_model_version(
        self,
        model_name: Optional[str] = None,
        model_id: Optional[int] = None,
        model_version_id: Optional[int] = None,
        model_version_number: Optional[int] = None,
        notes: Optional[str] = None,
        algorithm_name: Optional[str] = None,
        properties: Optional[Union[List[Tuple[str, str]], Tuple[str, str]]] = None,
        files: Optional[List[str]] = None,
    ) -> None:
        """
        Updates a model version. The model_name or model_id are used to find the model. The model_version_id or model_version_number are used
        to find the model version to be updated.

        properties can be as follows: [("key", "value"), ("key", "value")] or ("key", "value")

        :param model_name: The name of the model to update
        :param model_id: The model id to update
        :param model_version_id: The model version's id
        :param model_version_number: The model version number to update
        :param notes: A description of the model
        :param algorithm_name: The model's algorithm name
        :param properties: The properties for the model version
        :param files: The files to be updated. If the filename exists, it will be updated
        :return: None
        """
        model = (
            UpdateModelVersion(
                algorithmName=algorithm_name,
                description=notes,
            )
            .add_properties(data_properties=properties)
            .as_dict()
        )
        try:
            if model_name and not model_id:
                model_id = get_artifact_id(client=self._client, artifact_name=model_name)
            if model_id and model_version_number and not model_version_id:
                model_version_id = get_artifact_version_id(
                    client=self._client, artifact_id=model_id, version_number=model_version_number
                )
            attachments = UpdateModelVersion.create_attachments(files)
            if attachments and attachments.artifact_type and model_version_id:
                self._logger.info("Updating model attachments...")
                self._client.update_attachments(
                    artifact_type=attachments.artifact_type, artifact_version=model_version_id, files=attachments.files
                )
                self._logger.info("Attachments updated successfully.")

            if model_id and model_version_id:
                if notes is not None:
                    self._client.update_model_version(
                        model_id=model_id, model_version_id=model_version_id, model_version={"description": notes}
                    )
                if algorithm_name is not None:
                    self._client.update_model_version(
                        model_id=model_id,
                        model_version_id=model_version_id,
                        model_version={"algorithmName": algorithm_name},
                    )
                if model.get("properties"):
                    update_artifact_properties(self._client, model_id, model_version_id, model)

            self._logger.info(f"Model Version '{model_name or model_id}' has been updated successfully")
        except Exception as e:
            raise RuntimeError(f"Model version could not be updated due to {e}")

    def list_models(self, search: str = None, page_index=Page.index, page_size=Page.size) -> PagedResponse[ModelOutput]:
        """

        :param search:
        :param page_index:
        :param page_size:
        :return:
        """
        return self._client.list_models(search, page_index, page_size)

    def list_model_versions(
        self, model_id: int, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[ModelVersionOutput]:
        """
        Lists model versions in a PagedResponse.

        :param model_id: The id of the model
        :param page_index: The page index e.g 1/20 would return page 1
        :param page_size: The amount of versions on a page
        :return: PagedResponse
        """
        return self._client.list_model_versions(model_id, page_index, page_size)

    def list_model_versions_dataframe(self, model_id: int, page_index=Page.index, page_size=Page.size):
        """
        Lists model versions in a pandas DataFrame and sorts by update date. Requires the pandas module to be installed, which can be done with
        ```pip install pandas``` or ```pip install vectice[pandas]```

        :param model_id: The id of the model
        :param page_index: The page index. For example 1/20 would return page 1
        :param page_size: The number of versions on a page
        :return: pd.DataFrame
        """
        import pandas as pd  # type: ignore

        models = self._client.list_model_versions(model_id, page_index, page_size)
        metric_dataframes = []
        property_dataframes = []
        for idx, model_version in enumerate(models.list, start=0):
            model_metrics = self._client.list_model_version_metrics(
                model_id, model_version.id, page_index, page_size
            ).list
            temp_df_metrics = pd.DataFrame(
                data={metrics.key: [metrics.value] for metrics in model_metrics}, index=[idx]
            )
            metric_dataframes += [temp_df_metrics]

        for idx, model_version in enumerate(models.list, start=0):
            models_properties = self._client.list_model_version_properties(
                model_id, model_version.id, page_index, page_size
            ).list
            temp_df_metrics = pd.DataFrame(
                data={metrics.key: [metrics.value] for metrics in models_properties}, index=[idx]
            )
            property_dataframes += [temp_df_metrics]

        metric_dataframes = pd.concat(metric_dataframes)
        property_dataframes = pd.concat(property_dataframes)
        merged_entities = pd.merge(metric_dataframes, property_dataframes, left_index=True, right_index=True)
        df_model = pd.DataFrame(
            data=models.list,
            columns=["createdDate", "name", "versionNumber", "status", "algorithmName", "isStarred"],
        )
        return pd.merge(df_model, merged_entities, left_index=True, right_index=True).sort_values(
            by=["versionNumber"], ascending=False
        )

    def list_model_version_attachments(self, model_version_id: int) -> PagedResponse[AttachmentOutput]:
        """
        List the attachments associated with a model version.

        :param model_version_id: The artifact version ID.
        :return: PagedResponse[AttachmentOutput]
        """
        return self._client.list_attachments("modelversion", model_version_id)

    def download_model_version_attachment(self, model_version_id: int, file_id: int):
        """
        Download an attachment associated with it's version. e.g model_version_id: 1120 and file_id: 21

        :param model_version_id: The model version ID.
        :param file_id: The ID of the file to be downloaded
        :return:
        """
        download = None
        try:
            download = self._client.get_attachment("modelversion", model_version_id, file_id)
        except Exception as e:
            raise RuntimeError(f"The file_id: {file_id} could not be downloaded due to: {e}")
        if download is None:
            raise ValueError(f"File_id: {file_id} failed to download. Ensure model version and file exists.")
        self._logger.info(f"File_id: {file_id} downloaded successfully.")
        return download

    def delete_model_version_attachment(self, model_version_id: int, file_id: int):
        """
        Delete an attachment associated with it's version. model_version_id: 1120 and file_id: 21

        :param model_version_id: The model version ID.
        :param file_id: The ID of the file to be deleted
        :return:
        """
        try:
            self._client.delete_attachment("modelversion", model_version_id, file_id)
        except Exception as e:
            raise RuntimeError(f"The file_id: {file_id} could not be deleted due to: {e}")
        self._logger.info(f"File_id: {file_id} has been successfully deleted.")

    def list_connections(
        self, search_name: Optional[str] = None, connection_type: Optional[str] = None
    ) -> PagedResponse[ConnectionOutput]:
        """
        List attachments associated to current workspace and project.

        :param search_name: Search the name of the connection
        :param connection_type: The connection type of the connections e.g 'GoogleStorage'
        :return:
        """
        return self._client.list_connections(search_name=search_name, connection_type=connection_type)

    @classmethod
    def create_code_version(cls, path: str = ".") -> Optional[CodeVersionArtifact]:
        """
        Create an artifact that contains a version of a code

        :param path: The path to the source code
        :return: A code version artifact
        """
        return Artifacts.create_code_version(path)

    @classmethod
    def create_code_version_with_github_uri(
        cls, uri: str, script_relative_path: Optional[str] = None, login_or_token=None, password=None, jwt=None
    ) -> Optional[CodeVersionArtifact]:
        """
        Create a code artifact based on the GitHub information relative to the given URI and relative path.

        Note: The URI given can include the branch you are working on. otherwise, the default repository branch will be used.

        sample :
            https://github.com/my-organization/my-repository (no branch given so using default branch)
            https://github.com/my-organization/my-repository/tree/my-current-branch (branch given is my-current-branch)

        To access private repositories, you need to authenticate with your credentials.
        see https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/about-authentication-to-github

        :param uri: The uri of the repository with a specific branch if needed.
        :param script_relative_path:  The file that is executed
        :param login_or_token: A real login or a personal access token
        :param password: The password
        :param jwt: The OAuth2 access token
        :return: A CodeVersion or None if the GitHub repository was not found or is not accessible
        """
        return Artifacts.create_code_version_with_github_uri(uri, script_relative_path, login_or_token, password, jwt)

    @classmethod
    def create_code_version_with_gitlab_uri(
        cls, uri: str, script_relative_path: str, private_token: Optional[str] = None, oauth_token: Optional[str] = None
    ) -> Optional[CodeVersionArtifact]:
        """
         Create a code artifact based on the Gitlab information relative to the given URI and relative path.

        Note: The URI given can include the tree you are working on. otherwise, the default repository branch will be used.

        sample uri:
            "https://gitlab.com/my-organization/my-repository" (no branch given so using default branch)
            https://gitlab.com/my-organization/my-repository/tree/my-current-branch (branch given is my-current-branch)

        sample script relative path:
            "file_name.txt" (no folder in path)
            "folder/file_name.txt" (folder and file in path)

        To access private repositories, you need to authenticate with your credentials.
        see https://https://docs.gitlab.com/ee/topics/authentication/

        :param uri: The uri of the repository with a specific branch if needed.
        :param script_relative_path:  The file that is executed
        :param private_token: A real login or a personal access token
        :param oauth_token: The OAuth2 access token
        :return: A CodeVersion or None if the Gitlab repository was not found or is not accessible
        """
        return Artifacts.create_code_version_with_gitlab_uri(uri, script_relative_path, private_token, oauth_token)

    @classmethod
    def create_code_version_with_bitbucket_uri(
        cls,
        uri: str,
        script_relative_path: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Optional[CodeVersionArtifact]:
        """
        Create a code artifact based on the Bitbucket information relative to the given URI and relative path.

        Note: The URI given can include the branch you are working on. otherwise, the default repository branch will be used.

        sample :
            https://bitbucket.org/workspace/project/ (no branch given so using default branch)
            https://bitbucket.org/workspace/project/src/branch (branch given is my-current-branch)

        To access private repositories, you need to authenticate with your credentials.
        see Bitbucket Cloud: https://atlassian-python-api.readthedocs.io/index.html

        :param uri: The uri of the repository with a specific branch if needed.
        :param script_relative_path:  The file that is executed
        :param username: Bitbucket email
        :param password: Bitbucket password
        :return: A CodeVersion or None if the Bitbucket repository was not found or is not accessible
        """
        return Artifacts.create_code_version_with_bitbucket_uri(uri, script_relative_path, username, password)

    @classmethod
    def create_bigquery_dataset_version(
        cls, uri: str, description: Optional[str] = None
    ) -> Optional[DatasetMetadataArtifact]:
        """
        Create a bigquery dataset version using a uri. Creates a BigQuery resource attached to the dataset version. The uri is found in the google
        cloud console in the BigQuery tab.

        Example:
        Tables level : "https://console.cloud.google.com/bigquery?project=Project_Name&d=Dataset_Name&p=Project_Name&t=Table_Name&page=table"
        Dataset level: "https://console.cloud.google.com/bigquery?project=Project_Name&d=Dataset_Name&p=Project_Name&p=Project_Name&page=dataset&ws=!1m4!1m3!3m2!1sProject_Name!2sDataset_Name"

        :param uri: The url of the BigQuery dataset version that will be created
        :param description: The description of the dataset version
        :return: A DatasetMetadataArtifact that can be used in runs as an input or output
        """
        return Artifacts.create_bigquery_dataset(uri, description)

    @classmethod
    def create_gcs_dataset_version(
        cls, uri: Union[str, List[str]], description: Optional[str] = None
    ) -> Optional[DatasetMetadataArtifact]:
        """
        Create a Google Cloud Storage dataset version using an uri or List of uris. Creates a Google Cloud Storage resource attached to the dataset version. The uri is found in the google
        cloud console in the Google Cloud Storage tab.

        Example:
        File level :  bucket_name/folder_name/file_name.csv (Attaches the file)
        Folder level: bucket_name/folder_name (Attaches everything in the the folder)
        List : ['bucket_name/folder_name/file_name.csv', 'bucket_name/folder_name']

        :param uri: The uri or List of the Google Cloud Storage resources that will be used to create a dataset version
        :param description: The description of the dataset version
        :return: A DatasetMetadataArtifact that can be used in runs as an input or output
        """
        return Artifacts.create_gcs_dataset(uri, description)
