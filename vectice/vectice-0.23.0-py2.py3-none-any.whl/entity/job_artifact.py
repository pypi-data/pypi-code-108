from enum import Enum

from vectice.entity._versioned_entity import VersionedEntity


class Artifact(VersionedEntity):
    @property
    def job_artifact_type(self) -> str:
        return str(self["jobArtifactType"])

    @property
    def artifact_type(self) -> str:
        return str(self["artifactType"])

    @property
    def job_run_id(self) -> int:
        return int(self["jobRunId"])

    @property
    def job_property_id(self) -> int:
        return int(self["jobPropertyId"])

    @property
    def code_version_id(self) -> int:
        return int(self["codeVersionId"])

    @property
    def dataset_version_id(self) -> int:
        return int(self["dataSetVersionId"])

    @property
    def model_version_id(self) -> int:
        return int(self["modelVersionId"])

    @property
    def metadata_source(self) -> str:
        return str(self["metadataSource"])


class JobArtifactType(Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"


class ArtifactType(Enum):
    PROPERTY = "PROPERTY"
    DATASET = "DATASET"
    MODEL = "MODEL"
    CODE = "CODE"
