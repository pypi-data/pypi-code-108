import dataclasses
from typing import Dict, List, Optional, Set

from django_rest_client import (
    APIResource,
    APIResponse,
    CreateableAPIResourceMixin,
    ListableAPIResourceMixin,
    PaginationAPIResourceMixin,
    RetrievableAPIResourceMixin,
)
from django_rest_client.types import Toid, TParams
from typing_extensions import Literal

from pydragonfly.sdk.const import ANALYZED, CLEAN, FAILED, REVOKED

from .report import Report
from ._utils import omit_keys


class AnalysisResult:
    """
    .. versionadded:: 0.0.4
    """

    @dataclasses.dataclass
    class RuleResult:
        name: str
        weight: int
        score: int

        def __hash__(self):
            return hash((self.name, self.weight))

        def __eq__(self, other):
            return self.name == other.name and self.weight == other.weight

    # defaults
    id: Toid
    created_at: str
    gui_url: str
    api_url: str
    status: str
    evaluation: str = CLEAN
    weight: int = 0
    malware_families: List[str] = []
    #: deprecated in favor of ``mitre_techniques``.
    malware_behaviours: List[str] = []
    mitre_techniques: List[Dict] = []
    sample: Dict = {}
    reports: List[Dict] = []
    matched_rules: List[RuleResult] = []
    # extras
    score: int = 0
    malware_family: Optional[str] = None
    #: deprecated
    malware_behaviour: Optional[str] = None
    errors: List[str] = []

    def __init__(self, analysis_id: Toid):
        self.id = analysis_id
        # fetch and populate
        self.refresh()

    def __dict__(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "gui_url": self.gui_url,
            "api_url": self.api_url,
            "status": self.status,
            "evaluation": self.evaluation,
            "weight": self.weight,
            "score": self.score,
            "malware_families": self.malware_families,
            "mitre_techniques": self.mitre_techniques,
            "sample": self.sample,
            "reports": self.reports,
            "matched_rules": [dataclasses.asdict(mr) for mr in self.matched_rules],
        }

    def asdict(self) -> dict:
        return self.__dict__()

    def is_ready(self) -> bool:
        return self.status in [ANALYZED, FAILED, REVOKED]

    def refresh(self) -> None:
        """
        Refetch result from server.
        """
        data = self.__fetch()
        self.__populate(data)

    def __fetch(self) -> dict:
        matched_rules = []
        data = Analysis.retrieve(
            object_id=self.id,
            params=TParams(
                expand=["sample"],
                omit=[
                    "sample.file_deleted",
                    "sample.sections",
                    "sample.flags",
                    "sample.dlls_imported",
                    "sample.entry_points",
                    "sample.user",
                    "sample.file_version_info",
                ],
            ),
        ).data
        self.status = data["status"]
        if self.is_ready():
            for report in data["reports"]:  # we fetch matched-rules against each report
                rules = Report.matched_rules(
                    object_id=report["id"]
                ).data  # this can raise an exception
                if rules:
                    matched_rules.extend(rules)

        return {**data, "matched_rules": matched_rules}

    def __populate(self, data: dict) -> None:
        # defaults
        self.created_at = data["created_at"]
        self.gui_url = data["gui_url"]
        self.api_url = data["api_url"]
        self.status = data["status"]
        self.evaluation = data["evaluation"]
        self.weight = data["weight"]
        self.malware_families = data["malware_families"]
        self.mitre_techniques = (
            [
                {
                    "tid": tactic["tid"],
                    "name": tactic["name"],
                    "techniques": [
                        {
                            "tid": technique["tid"],
                            "name": technique["name"],
                        }
                        for technique in tactic["techniques"]
                    ],
                }
                for tactic in data["mitre_techniques"]
                if tactic["techniques"]
            ]
            if data["mitre_techniques"]
            else []
        )
        self.malware_behaviours = [  # deprecated
            technique["name"]
            for tactic in self.mitre_techniques
            for technique in tactic["techniques"]
        ]
        self.sample = data["sample"]
        self.reports = [
            omit_keys(report, ["time", "malware_families"])
            for report in data["reports"]
        ]
        matched_rules: Set[AnalysisResult.RuleResult] = set()
        for rule in data["matched_rules"]:
            matched_rules.add(
                AnalysisResult.RuleResult(
                    name=rule["rule"],
                    weight=rule["weight"],
                    score=(
                        round(min(100, rule["weight"]) / 10)
                        if rule["weight"] != 0
                        else 0
                    ),
                )
            )
        self.matched_rules = list(matched_rules)
        # extra
        self.score = round(min(100, self.weight) / 10) if self.weight != 0 else 0
        self.malware_family = (
            self.malware_families[0] if self.malware_families else None
        )
        self.malware_behaviour = (  # deprecated
            self.malware_behaviours[0] if self.malware_behaviours else None
        )
        self.errors = list(
            set([report["error"] for report in self.reports if report["error"]])
        )


@dataclasses.dataclass
class CreateAnalysisRequestBody:
    profiles: List[int]
    private: bool = False
    allow_actions: bool = False
    root: bool = False
    os: Optional[Literal["WINDOWS", "LINUX"]] = None
    arguments: Optional[List[str]] = None
    dll_entrypoints: Optional[List[str]] = None


class Analysis(
    APIResource,
    RetrievableAPIResourceMixin,
    ListableAPIResourceMixin,
    CreateableAPIResourceMixin,
    PaginationAPIResourceMixin,
):
    """
    :class:`pydragonfly.Dragonfly.Analysis`
    """

    OBJECT_NAME = "api.analysis"
    EXPANDABLE_FIELDS = {
        "retrieve": ["sample", "reports"],
        "list": [],
    }
    ORDERING_FIELDS = [
        "created_at",
        "sample__filename",
        "weight",
    ]
    CreateAnalysisRequestBody = CreateAnalysisRequestBody
    Result = AnalysisResult

    @classmethod
    def create(
        cls,
        data: CreateAnalysisRequestBody,
        sample_name: str,
        sample_buffer: bytes,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        # first: POST sample uploading it
        resp1 = cls._request(
            "POST",
            url="api/sample",
            files={"sample": (sample_name, sample_buffer)},
        )
        # second: POST analysis using the new sample ID
        # build request body
        req_data = {
            **{k: v for k, v in dataclasses.asdict(data).items() if v is not None},
            "sample_id": resp1.data["id"],
        }
        if resp1.data["malware_type"] == "DLL":
            req_data["dll_entrypoints"] = (
                data.dll_entrypoints
                if data.dll_entrypoints
                else resp1.data["entry_points"]
            )  # dll_entrypoints is required in case of DLL
        resp2 = cls._request(
            "POST",
            url=cls.class_url(),
            json=req_data,
            params=params,
        )
        return resp2

    @classmethod
    def aggregate_evaluations(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.class_url() + "/aggregate/evaluations"
        return cls._request("GET", url=url, params=params)

    @classmethod
    def aggregate_status(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.class_url() + "/aggregate/status"
        return cls._request("GET", url=url, params=params)

    @classmethod
    def aggregate_malware_families(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.class_url() + "/aggregate/malware_families"
        return cls._request("GET", url=url, params=params)

    @classmethod
    def aggregate_malware_type(
        cls,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.class_url() + "/aggregate/malware_type"
        return cls._request("GET", url=url, params=params)

    @classmethod
    def revoke(
        cls,
        object_id: Toid,
        params: Optional[TParams] = None,
    ) -> APIResponse:
        url = cls.instance_url(object_id) + "/revoke"
        return cls._request("POST", url=url, params=params)
