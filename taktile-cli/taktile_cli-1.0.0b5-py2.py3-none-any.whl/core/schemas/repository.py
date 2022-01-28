from datetime import datetime
from typing import Dict, List, Optional, Union

import certifi
from pydantic import UUID4, BaseModel, validator
from taktile_types.enums.instance import ServiceType

from tktl.constants import NON_EXISTING_DEPLOYMENT_DEFAULT_STATUS, URL_UNAVAILABLE
from tktl.core.config import settings
from tktl.core.t import AccessKind
from tktl.core.utils import flatten


class TablePrintableBaseModelMixin:
    def table_repr(self, subset: List[str] = None) -> Dict:
        ...


class Endpoint(BaseModel):
    name: str
    kind: str
    deployment_id: Optional[UUID4]
    profiling_supported: bool
    has_rest_sample_data: Optional[bool] = True
    has_arrow_sample_data: Optional[bool] = True

    class Config:
        validate_assignment = True

    @validator("deployment_id")
    def set_deployment_id(cls, deployment_id: UUID4):
        return deployment_id

    def table_repr(self, subset=None):
        as_dict = self.dict()
        as_dict["NAME"] = as_dict.pop("name")
        as_dict["KIND"] = str(as_dict.pop("kind"))
        as_dict["PROFILING SUPPORTED"] = str(as_dict.pop("profiling_supported"))
        as_dict["DEPLOYMENT ID"] = str(as_dict.pop("deployment_id"))
        return as_dict


class UserRepository(BaseModel):
    id: UUID4
    full_name: str


class RepositorySecret(BaseModel):
    id: UUID4
    repository_id: UUID4
    secret_name: str


class RepositoryDeployment(BaseModel, TablePrintableBaseModelMixin):
    id: UUID4
    created_at: datetime
    status: Optional[str]
    public_docs_url: Optional[str]

    rest_cpu_request: Optional[str]
    rest_memory_request: Optional[str]
    rest_gpu_request: Optional[str]
    rest_replicas: Optional[int]
    max_rest_replicas: Optional[int]

    arrow_replicas: Optional[int]
    arrow_cpu_request: Optional[str]
    arrow_memory_request: Optional[str]
    arrow_gpu_request: Optional[str]

    git_ref: str
    commit_hash: str
    n_endpoints: Optional[int]

    @validator("status", always=True)
    def validate_status(cls, value):
        return value if value else NON_EXISTING_DEPLOYMENT_DEFAULT_STATUS

    @validator("n_endpoints", always=True)
    def validate_n_endpoints(cls, value):
        return value or 0

    def table_repr(self, subset=None):
        as_dict = self.dict(exclude={"service_type", "endpoints",})
        repr = {}
        repr["ID"] = str(as_dict["id"])
        repr["BRANCH"] = as_dict["git_ref"]
        repr["COMMIT"] = as_dict["commit_hash"][0:7]
        repr["STATUS"] = as_dict["status"]
        repr["ENDPOINTS"] = as_dict["n_endpoints"]
        repr["CREATED AT"] = str(as_dict["created_at"])
        repr["REST DOCS URL"] = _format_http_url(as_dict["public_docs_url"])

        repr[
            "REST REPLICAS"
        ] = f"{as_dict['max_rest_replicas']} ({as_dict['rest_replicas']})"
        repr["REST SIZE"] = self.get_requests(ServiceType.REST, as_dict)

        if as_dict["arrow_replicas"] != "0":
            repr["ARROW REPLICAS"] = as_dict["arrow_replicas"]
            repr["ARROW SIZE"] = self.get_requests(ServiceType.GRPC, as_dict)
        if subset:
            return {k: v for k, v in repr.items() if k in subset}
        return repr

    def get_requests(self, kind: ServiceType, values: Dict):
        kind_name = "rest" if kind == ServiceType.REST else "arrow"

        if values[f"{kind_name}_cpu_request"] is None:
            return ""
        requests = f"{values[f'{kind_name}_cpu_request']} {values[f'{kind_name}_memory_request']}"
        if values[f"{kind_name}_gpu_request"] != "0":
            return requests + f" {values[f'{kind_name}_gpu_request']} gpus"
        return requests


class Repository(BaseModel, TablePrintableBaseModelMixin):
    id: UUID4
    ref_id: int
    repository_name: str
    repository_owner: str
    repository_description: Optional[str] = None
    access: AccessKind
    deployments: List[RepositoryDeployment]
    n_deployments: Optional[int] = None

    @validator("n_deployments", always=True)
    def validate_n_deployments(cls, _, values):
        return len(values["deployments"])

    def __hash__(self):
        return self.id.__hash__()

    def table_repr(self, subset=None):
        as_dict = self.dict(exclude={"ref_id", "deployments"})
        as_dict["ID"] = f"{as_dict.pop('id')}"
        as_dict[
            "FULL NAME"
        ] = f"{as_dict.pop('repository_owner')}/{as_dict.pop('repository_name')}"
        as_dict["DEPLOYMENTS"] = as_dict.pop("n_deployments")
        as_dict["ACCESS"] = f"{as_dict.pop('access').value}"
        desc = as_dict.pop("repository_description")
        as_dict["DESCRIPTION"] = f"{desc[0:20] + '...' if desc else '-'}"
        if subset:
            return {k: v for k, v in as_dict.items() if k in subset}
        return as_dict


class RepositoryList(BaseModel):
    __root__: List[Repository]

    def get_repositories(self) -> List[Repository]:
        return [r for r in self.__root__]

    def get_deployments(self) -> List[RepositoryDeployment]:
        return flatten([[d for d in r.deployments] for r in self.__root__])


class ReportResponse(BaseModel):
    deployment_id: UUID4
    endpoint_name: str
    report_type: str
    chart_name: Optional[str] = None
    variable_name: Optional[str] = None
    value: Union[List, Dict]


def _format_http_url(url: Optional[str], docs: bool = True) -> str:
    if url == URL_UNAVAILABLE or url is None:
        return URL_UNAVAILABLE
    if settings.LOCAL_STACK:
        return f"http://{url}:8000/{'docs' if docs else ''}"
    if settings.E2E:
        return f"http://{url}/{'docs' if docs else ''}".replace(
            ".local.taktile.com", "-rest.default.svc.cluster.local", 1
        )

    return f"https://{url}/{'docs' if docs else ''}"


def _format_grpc_url(url: Optional[str]) -> str:
    if url == URL_UNAVAILABLE or url is None:
        return URL_UNAVAILABLE
    if settings.LOCAL_STACK:
        return (
            f"grpc+tcp://{url}:5005"
            if (url and url != "UNAVAILABLE")
            else "UNAVAILABLE"
        )
    if settings.E2E:
        return (
            f"grpc+tcp://{url}:5005".replace(
                ".local.taktile.com", "-grpc.default.svc.cluster.local", 1
            )
            if (url and url != "UNAVAILABLE")
            else "UNAVAILABLE"
        )
    return f"grpc+tls://{url}:5005" if (url and url != "UNAVAILABLE") else "UNAVAILABLE"


def load_certs():
    with open(certifi.where(), "r") as cert:
        return cert.read()


Resources = Union[Repository, RepositoryDeployment, Endpoint, UserRepository]
