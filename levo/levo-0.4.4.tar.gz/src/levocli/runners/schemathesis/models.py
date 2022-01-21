"""Lightweight adaptation of Schemathesis internal data structures."""
import threading
from typing import Dict, List, Optional, Union

import attr
from levo_commons.events import Payload
from levo_commons.models import AssertionResult, SerializedError, Status


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
