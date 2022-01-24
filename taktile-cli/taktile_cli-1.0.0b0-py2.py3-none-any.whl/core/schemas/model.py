from pydantic import BaseModel


class Model(BaseModel):
    """
    Model class

    :param str id:
    :param str name:
    :param str project_id:
    :param str experiment_id:
    :param list tags:
    :param str model_type:
    :param str url:
    :param str model_path:
    :param str deployment_state:
    :param str summary:
    :param str detail:
    """

    id: str
    name: str
    project_id: str
    experiment_id: str
    tags: list
    model_type: str
    url: str
    model_path: str
    deployment_state: str
    summary: dict
    detail: dict
    notes: str


class ModelFile(BaseModel):
    """
    Model file

    :param str file: file path
    :param str url: Url with AWS key
    :param int size: File size in bytes
    """

    file: str
    url: str
    size: int
