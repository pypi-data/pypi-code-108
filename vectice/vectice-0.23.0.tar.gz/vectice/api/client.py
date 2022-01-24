from typing import List, Optional, Tuple, Any, BinaryIO

from vectice.api.Page import Page
from vectice.api.attachment import AttachmentApi
from vectice.api.connections import ConnectionApi
from vectice.api.dataset import DatasetApi
from vectice.api.dataset_version import DatasetVersionApi
from vectice.api.job import JobApi
from vectice.api.job_artifact import ArtifactApi
from vectice.api.job_run import RunApi
from vectice.api.json_object import JsonObject
from vectice.api.model import ModelApi
from vectice.api.model_version import ModelVersionApi
from vectice.api.output.attachments_output import AttachmentOutput
from vectice.api.output.connection_output import ConnectionOutput
from vectice.api.output.dataset_output import DatasetOutput
from vectice.api.output.dataset_version_output import DatasetVersionOutput
from vectice.api.output.job_output import JobOutput
from vectice.api.output.job_run_output import JobRunOutput
from vectice.api.output.metric_output import EntityMetricOutput
from vectice.api.output.model_output import ModelOutput
from vectice.api.output.model_version_output import ModelVersionOutput
from vectice.api.output.paged_response import PagedResponse
from vectice.api.output.property_output import EntityPropertyOutput
from vectice.api.project import ProjectApi
from vectice.api.rule import RuleApi
from vectice.models import Artifact, RunnableJob


class Client(ProjectApi):
    """
    Low level Vectice API client.
    """

    def __init__(self, project_token: str, auto_connect=True, allow_self_certificate=True):
        super().__init__(
            project_token=project_token, auto_connect=auto_connect, allow_self_certificate=allow_self_certificate
        )
        self._allow_self_certificate = allow_self_certificate
        self._api_config = {
            "project_token": self.project_token,
            "allow_self_certificate": self._allow_self_certificate,
            "_token": self._token,
        }

    @property
    def _config(self) -> dict:
        self._api_config["_token"] = self._token
        self._api_config["allow_self_certificate"] = self._allow_self_certificate
        self._api_config["project_token"] = self.project_token
        return self._api_config

    def start_run(
        self,
        run: RunnableJob,
        inputs: Optional[List[Artifact]] = None,
    ) -> JsonObject:
        """
        Start a run.

        :param run: The run to start
        :param inputs: A list of artifacts to linked to the run
        :return: A json object
        """
        return RuleApi(**self._config).start_run(run.job, run.run, inputs)

    def stop_run(self, run: JsonObject, outputs: Optional[List[Artifact]] = None):
        """

        :param run:
        :param outputs:
        :return:
        """
        return RuleApi(**self._config).stop_run(run, outputs)

    def list_jobs(
        self, search: Optional[str] = None, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[JobOutput]:
        """

        :param search: A text to filter jobs we are looking for
        :param page_index: The index of the page
        :param page_size: The size of the page
        :return: A paged response that contains a list of JobOutput instances.
        """
        return JobApi(**self._config).list_jobs(search, page_index, page_size)

    def create_job(self, job: JsonObject) -> JobOutput:
        """
        Create a job

        :param job: A job description (json)
        :return: A JobOutput instance
        """
        return JobApi(**self._config).create_job(job)

    def update_job(self, job_id: int, job: JsonObject):
        """
        Update a job

        :param job: A job description (json)
        :return: The json structure
        """
        return JobApi(**self._config).update_job(job_id, job)

    def list_runs(self, job_id: int, page_index=Page.index, page_size=Page.size) -> List[JobRunOutput]:
        """
        List runs of a specific job.

        :param job_id: The identifier of the job
        :param page_index: The index of the page
        :param page_size: The size of the page
        :return: a list of JobRunOutput
        """
        return RunApi(job_id=job_id, **self._config).list_runs(page_index, page_size)

    def create_run(self, job_id: int, run: JsonObject):
        """
        Create a run

        :param job_id: The identifier of the job
        :param run: A run description (json)
        :return: The json structure
        """
        return RunApi(job_id=job_id, **self._config).create_run(run)

    def update_run(self, job_id: int, run_id: int, run: JsonObject):
        """
        Update a run

        :param job_id: The identifier of the job
        :param run_id:
        :param run:
        :return: The json structure
        """
        return RunApi(job_id=job_id, **self._config).update_run(run_id, run)

    def create_artifact(self, job_id: int, run_id: int, artifact: JsonObject):
        """
        Create artifact

        :param job_id: The identifier of the job
        :param run_id:
        :param artifact:
        :return: The json structure
        """
        return ArtifactApi(job_id=job_id, run_id=run_id, **self._config).create_artifact(artifact)

    def update_artifact(self, job_id: int, run_id: int, artifact_id: int, artifact: JsonObject):
        """
        Update artifact

        :param job_id: The identifier of the job
        :param run_id:
        :param artifact_id:
        :param artifact:
        :return: The json structure
        """
        return ArtifactApi(job_id=job_id, run_id=run_id, **self._config).update_artifact(artifact_id, artifact)

    def list_datasets(
        self, search: str = None, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[DatasetOutput]:
        """
        List datasets

        :param search: a text used to filter list of datasets
        :param page_index: The index of the page
        :param page_size: The size of the page
        :return: The json structure
        """
        return DatasetApi(**self._config).list_datasets(search, page_index, page_size)

    def create_dataset(self, dataset: JsonObject):
        """
        Create a dataset

        :param dataset:
        :return: The json structure
        """
        return DatasetApi(**self._config).create_dataset(dataset)

    def update_dataset(self, dataset_id: int, dataset: JsonObject):
        """
        Update a dataset

        :param dataset_id:
        :param dataset:
        :return: The json structure
        """
        return DatasetApi(**self._config).update_dataset(dataset_id, dataset)

    def list_models(self, search: str = None, page_index=Page.index, page_size=Page.size) -> PagedResponse[ModelOutput]:
        """
        List models

        :param search:
        :param page_index: The index of the page
        :param page_size: The size of the page
        :return: The json structure
        """
        return ModelApi(**self._config).list_models(search, page_index, page_size)

    def create_model(self, model: JsonObject):
        """
        Create a model

        :param model:
        :return: The json structure
        """
        return ModelApi(**self._config).create_model(model)

    def update_model(self, model_id: int, model: JsonObject):
        """
        Update a model

        :param model_id:
        :param model:
        :return: The json structure
        """
        return ModelApi(**self._config).update_model(model_id, model)

    def list_dataset_versions(
        self, dataset_id: int, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[DatasetVersionOutput]:
        """
        List dataset versions

        :param dataset_id:
        :param page_index: The index of the page
        :param page_size: The size of the page
        :return:
        """
        return DatasetVersionApi(dataset_id=dataset_id, **self._config).list_dataset_versions(page_index, page_size)

    def create_dataset_version(self, dataset_id: int, dataset_version: JsonObject):
        """
        Create a dataset version

        :param dataset_id:
        :param dataset_version:
        :return: The json structure
        """
        return DatasetVersionApi(dataset_id=dataset_id, **self._config).create_dataset_version(dataset_version)

    def update_dataset_version(self, dataset_id: int, dataset_version_id: int, dataset_version: JsonObject):
        """
        Update a dataset version

        :param dataset_id:
        :param dataset_version_id:
        :param dataset_version:
        :return: The json structure
        """
        return DatasetVersionApi(dataset_id=dataset_id, **self._config).update_dataset_version(
            dataset_version_id, dataset_version
        )

    def get_dataset_version(
        self, dataset_id: int, search: str, page_index=Page.index, page_size=Page.size
    ) -> Optional[DatasetVersionOutput]:
        """
        Get a dataset version

        :param dataset_id:
        :param search:
        :param page_index: The index of the page
        :param page_size: The size of the page
        :return:
        """
        return DatasetVersionApi(dataset_id=dataset_id, **self._config).get_dataset_version(
            search, page_index, page_size
        )

    def create_dataset_version_properties(self, dataset_id: int, dataset_version_id: int, properties: List[dict]):
        """
        Create data version properties

        :param dataset_id:
        :param dataset_version_id:
        :param properties:
        :return:
        """
        return DatasetVersionApi(dataset_id=dataset_id, **self._config).create_dataset_version_properties(
            dataset_version_id, properties
        )

    def update_dataset_version_properties(
        self, dataset_id: int, dataset_version_id: int, property_id: int, properties: JsonObject
    ):
        """
        Create data version properties

        :param dataset_id:
        :param dataset_version_id:
        :param properties:
        :param property_id:
        :return:
        """
        return DatasetVersionApi(dataset_id=dataset_id, **self._config).update_dataset_version_properties(
            dataset_version_id, property_id, properties
        )

    def list_dataset_version_properties(
        self, dataset_id: int, dataset_version_id: int, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[EntityPropertyOutput]:
        """
        List dataset version properties

        :param dataset_id:
        :param dataset_version_id:
        :param page_index: The index of the page
        :param page_size: The size of the page
        :return:
        """
        return DatasetVersionApi(dataset_id=dataset_id, **self._config).list_dataset_version_properties(
            dataset_version_id, page_index, page_size
        )

    def list_model_versions(
        self, model_id: int, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[ModelVersionOutput]:
        """
        List model versions

        :param model_id:
        :param page_index: The index of the page
        :param page_size: The size of the page
        :return:
        """
        return ModelVersionApi(model_id=model_id, **self._config).list_model_versions(page_index, page_size)

    def list_model_version_metrics(
        self, model_id: int, model_version_id: int, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[EntityMetricOutput]:
        """
        List model versions

        :param model_id:
        :param model_version_id:
        :param page_index: The index of the page
        :param page_size: The size of the page
        :return:
        """
        return ModelVersionApi(model_id=model_id, **self._config).list_model_version_metrics(
            model_version_id, page_index, page_size
        )

    def list_model_version_properties(
        self, model_id: int, model_version_id: int, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[EntityPropertyOutput]:
        """
        List model versions

        :param model_id:
        :param model_version_id:
        :param page_index: The index of the page
        :param page_size: The size of the page
        :return:
        """
        return ModelVersionApi(model_id=model_id, **self._config).list_model_version_properties(
            model_version_id, page_index, page_size
        )

    def create_model_version_properties(self, model_id: int, model_version_id: int, properties: List[dict]):
        """
        Create model version properties

        :param model_id:
        :param model_version_id:
        :param properties:
        :return:
        """
        return ModelVersionApi(model_id=model_id, **self._config).create_model_version_properties(
            model_version_id, properties
        )

    def update_model_version_properties(
        self, model_id: int, model_version_id: int, property_id: int, properties: JsonObject
    ):
        """
        Create model version properties

        :param model_id:
        :param model_version_id:
        :param properties:
        :param property_id:
        :return:
        """
        return ModelVersionApi(model_id=model_id, **self._config).update_model_version_properties(
            model_version_id, property_id, properties
        )

    def create_model_version(self, model_id: int, model_version: JsonObject):
        """
        Create a model version

        :param model_id:
        :param model_version:
        :return: The json structure
        """
        return ModelVersionApi(model_id=model_id, **self._config).create_model_version(model_version)

    def update_model_version(self, model_id: int, model_version_id: int, model_version: JsonObject):
        """
        Update a model version

        :param model_id:
        :param model_version_id:
        :param model_version:
        :return: The json structure
        """
        return ModelVersionApi(model_id=model_id, **self._config).update_model_version(model_version_id, model_version)

    def get_attachment(self, artifact_type: str, artifact_version: int, file_id: int):
        """
        Downloads the specified attachment

        :param artifact_type:
        :param artifact_version:
        :param file_id:
        :return: The file requested
        """
        return AttachmentApi(**self._config).get_attachment(artifact_type, artifact_version, file_id)

    def create_attachments(
        self, artifact_type: str, artifact_version: int, files: Optional[List[Tuple[str, Tuple[Any, BinaryIO]]]]
    ):
        """
        Create an attachment

        :param artifact_type:
        :param artifact_version:
        :param files:
        :return: The json structure
        """
        return AttachmentApi(**self._config).post_attachment(artifact_type, artifact_version, files)

    def update_attachments(
        self, artifact_type: str, artifact_version: int, files: List[Tuple[str, Tuple[Any, BinaryIO]]]
    ):
        """
        Update an attachment

        :param artifact_type:
        :param artifact_version:
        :param files:
        :return: The json structure
        """
        return AttachmentApi(**self._config).update_attachments(artifact_type, artifact_version, files)

    def delete_attachment(self, artifact_type: str, artifact_version: int, file_id: int):
        """
        Delete attachment

        :param artifact_type:
        :param artifact_version:
        :param file_id:
        :return: The json structure
        """
        return AttachmentApi(**self._config).delete_attachment(artifact_type, artifact_version, file_id)

    def list_attachments(self, artifact_type: str, artifact_version: int) -> PagedResponse[AttachmentOutput]:
        """
        List attachments

        :param artifact_type:
        :param artifact_version:
        :return: The json structure
        """
        return AttachmentApi(**self._config).list_attachments(artifact_type, artifact_version)

    def list_connections(
        self, search_name: Optional[str] = None, connection_type: Optional[str] = None
    ) -> PagedResponse[ConnectionOutput]:
        """
        List connections

        :param search_name:
        :param connection_type:
        :return: The json structure
        """
        api = ConnectionApi(self._config["_token"], allow_self_certificate=self._config["allow_self_certificate"])
        return api.list_connections(search_name=search_name, connection_type=connection_type)
