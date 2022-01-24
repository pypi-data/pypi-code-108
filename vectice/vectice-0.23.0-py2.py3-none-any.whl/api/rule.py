from datetime import datetime, timezone
from typing import List, Optional

from vectice.models import Job, Artifact, JobRun, VecticeError

from ._http import HttpError
from ._utils import calculate_duration
from .json_object import JsonObject
from .project import ProjectApi
from ..entity import DatasetVersion, ModelVersion, CodeVersion
from ..entity.job_artifact import ArtifactType


class RuleApi(ProjectApi):
    def __init__(self, project_token: str, _token: Optional[str] = None, allow_self_certificate=True):
        super().__init__(project_token=project_token, _token=_token, allow_self_certificate=allow_self_certificate)
        self._rule_path = super().api_base_path + "/rules"

    @property
    def api_base_path(self) -> str:
        return self._rule_path

    def start_run(self, job: Job, run: Optional[JobRun] = None, inputs: Optional[List[Artifact]] = None) -> JsonObject:
        if run is None:
            run = JobRun()
        if inputs is None:
            inputs = []
        else:
            inputs = [item for item in inputs if item is not None]
        if job.name is None:
            raise ValueError('"name" must be provided in job.')
        # self._check_artifacts(inputs)
        return self._post(
            self.api_base_path + "/start-run",
            {"job": job, "jobRun": run, "inputArtifacts": inputs},
        )

    def stop_run(self, run: dict, outputs: Optional[List[Artifact]] = None):
        if run.get("id") is None:
            raise ValueError('"id" must be provided in run.')
        if run.get("endDate") is None:
            now = datetime.now(timezone.utc)
            run["endDate"] = now.isoformat()
            run["duration"] = calculate_duration(now, run["startDate"])
        if outputs is None:
            outputs = []
        else:
            outputs = [item for item in outputs if item is not None]
        # self._check_artifacts(outputs)
        try:
            return self._post(self.api_base_path + "/stop-run", {"jobRun": run, "outputArtifacts": outputs})
        except HttpError as e:
            raise VecticeError("stop_run", e)

    @staticmethod
    def _check_artifacts(artifacts: List[dict]):
        for i in range(len(artifacts)):
            artifact = artifacts[i]
            # Fill DTO from an existing artifact
            if isinstance(artifact, DatasetVersion):
                artifacts[i] = {
                    "artifactType": "DATASET",
                    "dataset": {
                        "parentId": artifact.dataset_id,
                        "autoVersion": False,
                        "version": {"versionNumber": artifact.version_number},
                    },
                }
                continue
            if isinstance(artifact, ModelVersion):
                artifacts[i] = {
                    "artifactType": "MODEL",
                    "model": {
                        "parentId": artifact.model_id,
                        "version": {"versionNumber": artifact.version_number},
                    },
                }
                continue
            if isinstance(artifact, CodeVersion):
                artifacts[i] = {
                    "artifactType": "CODE",
                    "code": {
                        "parentId": artifact.code_id,
                        "version": {"versionNumber": artifact.version_number},
                    },
                }
                continue
            if "artifactType" not in artifact:
                raise ValueError('"artifactType" must be provided in artifact.')
            if artifact["artifactType"] not in ArtifactType.__members__:
                raise ValueError(f"Unsupported artifact type: {artifact['artifactType']}")
