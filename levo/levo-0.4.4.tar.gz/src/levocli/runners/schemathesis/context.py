import os
import shutil
from typing import Dict, List, Optional

import attr
from levo_commons.models import AssertionResult, SerializedError
from levo_commons.status import Status
from schemathesis.constants import CodeSampleStyle


@attr.s(slots=True)
class EndpointExecutionContext:
    """Contextual information for a single endpoint that's being executed."""

    name: str = attr.ib()
    test_item_id: Optional[str] = attr.ib(default=None)
    operations_processed: int = attr.ib(default=0)
    test_case_id_to_item_id: Dict = attr.ib(factory=dict)
    # Maintain the assertions and errors separately for each check so that we can show relevant errors for each test.
    data_generation_method_to_assertions: Dict[str, List[AssertionResult]] = attr.ib(
        factory=dict
    )
    errors: List[SerializedError] = attr.ib(factory=list)
    success_count: int = attr.ib(default=0)
    failed_count: int = attr.ib(default=0)
    errored_count: int = attr.ib(default=0)
    status: Status = attr.ib(default=Status.success)
    duration: float = attr.ib(default=0.0)


@attr.s(slots=True)
class ExecutionContext:
    """Storage for the current context of the execution."""

    hypothesis_output: List[str] = attr.ib(factory=list)
    workers_num: int = attr.ib(default=1)
    # It is set in runtime, from a `Initialized` event
    operations_count: Optional[int] = attr.ib(default=None)
    show_errors_tracebacks: bool = attr.ib(default=False)
    validate_schema: bool = attr.ib(default=True)
    current_line_length: int = attr.ib(default=0)
    terminal_size: os.terminal_size = attr.ib(factory=shutil.get_terminal_size)
    cassette_file_name: Optional[str] = attr.ib(default=None)
    junit_xml_file: Optional[str] = attr.ib(default=None)
    verbosity: int = attr.ib(default=0)
    code_sample_style: CodeSampleStyle = attr.ib(default=CodeSampleStyle.default())
    endpoint_to_context: Dict[str, EndpointExecutionContext] = attr.ib(factory=dict)
    status: Status = attr.ib(default=Status.success)
    success_count: int = attr.ib(default=0)
    failed_count: int = attr.ib(default=0)
    errored_count: int = attr.ib(default=0)
