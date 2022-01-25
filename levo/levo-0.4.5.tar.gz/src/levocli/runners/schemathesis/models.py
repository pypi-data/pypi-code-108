"""Lightweight adaptation of Schemathesis internal data structures."""
import threading
from typing import Any, Dict, List, Optional, Union

import attr
from aenum import Enum
from levo_commons.events import Payload
from levo_commons.models import CWE, AssertionResult, Risk, SerializedError, Status
from levo_commons.params import ParamType


@attr.s(slots=True)
class InitializedPayload(Payload):
    # Total number of operations in the schema
    operations_count: Optional[int] = attr.ib()
    # The place, where the API schema is located
    location: Optional[str] = attr.ib()
    # The base URL against which the tests are running
    base_url: str = attr.ib()
    # API schema specification name
    specification_name: str = attr.ib()


@attr.s(slots=True)
class BeforeExecutionPayload(Payload):
    # Unique ID for a test case
    correlation_id: str = attr.ib()
    method: str = attr.ib()
    # Specification-specific operation name
    verbose_name: str = attr.ib()
    relative_path: str = attr.ib()
    # The current level of recursion during stateful testing
    recursion_level: int = attr.ib()


@attr.s(slots=True)
class AfterExecutionPayload(Payload):
    method: str = attr.ib()
    relative_path: str = attr.ib()
    status: Status = attr.ib()
    correlation_id: str = attr.ib()
    elapsed_time: float = attr.ib()
    assertions: List[AssertionResult] = attr.ib()
    errors: List[SerializedError] = attr.ib()
    data_generation_method: Optional[str] = attr.ib()
    # Captured hypothesis stdout
    hypothesis_output: List[str] = attr.ib(factory=list)
    thread_id: int = attr.ib(factory=threading.get_ident)


@attr.s(slots=True)
class FinishedPayload(Payload):
    has_failures: bool = attr.ib()
    has_errors: bool = attr.ib()
    is_empty: bool = attr.ib()

    total: Dict[str, Dict[Union[str, Status], int]] = attr.ib()
    generic_errors: List[SerializedError] = attr.ib()


class SchemaConformanceCheck(Enum):
    def __init__(
        self,
        readable_name: str,
        passed_summary: str,
        failed_summary: str,
        risk: Risk,
        cwe: CWE,
        cwe_url: str,
        solution: str,
        param_type: Optional[ParamType],
    ):
        self.readable_name = readable_name
        self.passed_summary = passed_summary
        self.failed_summary = failed_summary
        self.risk = risk
        self.cwe = cwe
        self.cwe_url = cwe_url
        self.solution = solution
        self.param_type = param_type

    NOT_A_SERVER_ERROR = (
        "Unexpected Server Error",
        "This API endpoint conforms to the specified schema and does not return any unexpected server errors"
        " (500 error codes).",
        "This API endpoint does not conform to the specified schema as it returns unexpected server errors "
        "(5XX error codes), that are not documented. Please check the log for more details.",
        Risk.medium,
        CWE.ID_600,
        "https://cwe.mitre.org/data/definitions/600.html",
        "https://docs.levo.ai/issues/schema-conformance#what-is-the-solution",
        ParamType.body,
    )
    STATUS_CODE_CONFORMANCE = (
        "Response Status Code",
        "This API endpoint conforms to the specified schema and does not return any (HTTP) response codes"
        " that differ from what is documented in the schema.",
        "This API endpoint response status code does not conform to the specified schema, as it returns a (HTTP)"
        " response code that is undocumented. Please check the log for more details.",
        Risk.medium,
        CWE.ID_394,
        "https://cwe.mitre.org/data/definitions/394.html",
        "https://docs.levo.ai/issues/schema-conformance#what-is-the-solution",
        ParamType.body,
    )
    CONTENT_TYPE_CONFORMANCE = (
        "Response Content Type",
        "This API endpoint conforms to the specified schema, and does not return any (HTTP) content types"
        " that differ from what is documented in the schema.",
        "This API endpoint response content type does not conform to the specified schema, as it returns a (HTTP)"
        " content type that is undocumented. Please check the log for more details.",
        Risk.medium,
        CWE.ID_394,
        "https://cwe.mitre.org/data/definitions/394.html",
        "https://docs.levo.ai/issues/schema-conformance#what-is-the-solution",
        ParamType.body,
    )
    RESPONSE_HEADERS_CONFORMANCE = (
        "Response Headers",
        "This API endpoint conforms to the specified schema, and does not return any (HTTP response) headers "
        "that differ from what is documented in the schema.",
        "This API endpoint response headers does not conform to the specified schema, as it returns "
        "an undocumented HTTP response header. Please check the log for more details.",
        Risk.medium,
        CWE.ID_394,
        "https://cwe.mitre.org/data/definitions/394.html",
        "https://docs.levo.ai/issues/schema-conformance#what-is-the-solution",
        ParamType.headers,
    )
    RESPONSE_SCHEMA_CONFORMANCE = (
        "Response Body",
        "The response received from this API endpoint conforms to the specified response schema.",
        "This API endpoint response does not conform to the specified schema, as it returns "
        "an undocumented HTTP response body element. Please check the log for more details.",
        Risk.medium,
        CWE.ID_394,
        "https://cwe.mitre.org/data/definitions/394.html",
        "https://docs.levo.ai/issues/schema-conformance#what-is-the-solution",
        ParamType.body,
    )

    def get_summary(self, status: Status) -> str:
        return self.passed_summary if status == Status.success else self.failed_summary

    def __str__(self) -> Any:
        return self.readable_name
