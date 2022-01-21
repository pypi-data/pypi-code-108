import os
import shutil
from logging import INFO, Logger, getLogger
from typing import Dict, List, Optional

import attr
from levo_commons.models import TestResult
from levo_commons.status import Status

from .models import Plan


@attr.s(slots=True)
class TestCaseExecutionContext:
    """Contextual information for the test case that's being executed."""

    logs: List[str] = attr.ib(factory=list)


@attr.s(slots=True)
class TestSuiteExecutionContext:
    """Contextual information for the test suite that's being executed."""

    name: str = attr.ib()
    test_item_id: Optional[str] = attr.ib(default=None)
    operations_processed: int = attr.ib(default=0)
    test_case_id_to_item_id: Dict = attr.ib(factory=dict)
    results: List[TestResult] = attr.ib(factory=list)
    success_count: int = attr.ib(default=0)
    failed_count: int = attr.ib(default=0)
    errored_count: int = attr.ib(default=0)
    skipped_count: int = attr.ib(default=0)
    status: Status = attr.ib(default=Status.success)
    active_test_case_id: Optional[str] = attr.ib(default=None)
    test_case_id_to_context: Dict[str, TestCaseExecutionContext] = attr.ib(factory=dict)
    logs: List[str] = attr.ib(factory=list)


@attr.s(slots=True)
class ExecutionContext:
    """Contextual information for the test plan that's being executed."""

    plan: Plan = attr.ib()
    logger: Logger = attr.ib(default=None)
    workers_num: int = attr.ib(default=1)
    show_errors_tracebacks: bool = attr.ib(default=False)
    current_line_length: int = attr.ib(default=0)
    terminal_size: os.terminal_size = attr.ib(factory=shutil.get_terminal_size)
    cassette_file_name: Optional[str] = attr.ib(default=None)
    junit_xml_file: Optional[str] = attr.ib(default=None)
    verbosity: int = attr.ib(default=0)
    test_suite_id_to_context: Dict[str, TestSuiteExecutionContext] = attr.ib(
        factory=dict
    )
    success_count: int = attr.ib(default=0)
    failed_count: int = attr.ib(default=0)
    errored_count: int = attr.ib(default=0)
    skipped_count: int = attr.ib(default=0)
    skipped_suite_count: int = attr.ib(default=0)
    active_test_suite_id: Optional[str] = attr.ib(default=None)
    logs: List[str] = attr.ib(factory=list)
