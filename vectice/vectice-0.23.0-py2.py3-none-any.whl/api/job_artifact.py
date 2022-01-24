from typing import Optional

from vectice.entity import Artifact

from .job_run import RunApi
from .json_object import JsonObject


class ArtifactApi(RunApi):
    def __init__(
        self, project_token: str, job_id: int, run_id: int, _token: Optional[str] = None, allow_self_certificate=True
    ):
        super().__init__(
            project_token=project_token, job_id=job_id, _token=_token, allow_self_certificate=allow_self_certificate
        )
        self._run_id = run_id
        self._artifact_path = super().api_base_path + "/" + str(run_id) + "/artifact"

    @property
    def run_id(self) -> int:
        return self._run_id

    @property
    def api_base_path(self) -> str:
        return self._artifact_path

    def create_artifact(self, artifact: JsonObject) -> Artifact:
        if artifact.get("artifactType") is None:
            raise ValueError('"artifactType" must be provided in artifact.')
        if artifact.get("jobArtifactType") is None:
            raise ValueError('"jobArtifactType" must be provided in artifact.')
        return Artifact(self._post(self.api_base_path, artifact))

    def update_artifact(self, artifact_id: int, artifact: JsonObject) -> Artifact:
        return Artifact(self._put(self.api_base_path + "/" + str(artifact_id), artifact))
