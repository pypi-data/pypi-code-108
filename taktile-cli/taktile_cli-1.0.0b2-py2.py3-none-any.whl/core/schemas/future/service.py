import typing as t

from pydantic import BaseModel
from taktile_types.enums.endpoint import EndpointKinds, ProfileKinds

from tktl.core.future.t import ArrowFormatKinds


class EndpointInfoSchema(BaseModel):
    name: str
    position: t.Optional[int]
    path: str
    kind: EndpointKinds
    profile_kind: t.Optional[ProfileKinds]
    explain_path: t.Optional[str]
    response_kind: t.Optional[ArrowFormatKinds]
    input_names: t.List[str] = []
    output_names: t.Optional[str] = None
    profile_columns: t.Optional[t.List[str]] = None
    input_example: t.Optional[t.List[t.Any]] = None
    output_example: t.Optional[t.List[t.Any]] = None
    explainer_example: t.Optional[t.List[t.Any]] = None
    tags: t.Optional[t.List[str]]


class InfoEndpointResponseModel(BaseModel):
    schema_version: str
    taktile_cli: str
    profiling: str
    git_sha: t.Optional[str]
    git_ref: t.Optional[str]
    endpoints: t.List[EndpointInfoSchema]
