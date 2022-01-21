import logging
import sys
from logging import INFO, Logger, LogRecord, NullHandler, StreamHandler, getLogger

from .context import ExecutionContext


class TestPlanLoggerHandler(StreamHandler):

    context: ExecutionContext
    level: int

    def __init__(self, context: ExecutionContext, level: int = logging.NOTSET):
        self.context = context
        self.level = level

    def emit(self, record: LogRecord) -> None:
        msg = self.format(record)
        self.context.logs.append(msg)
        if (
            self.context.active_test_suite_id
            and self.context.active_test_suite_id
            in self.context.test_suite_id_to_context
        ):
            suite_context = self.context.test_suite_id_to_context[
                self.context.active_test_suite_id
            ]
            suite_context.logs.append(msg)
            if (
                suite_context.active_test_case_id
                and suite_context.active_test_case_id
                in suite_context.test_case_id_to_context
            ):
                case_context = suite_context.test_case_id_to_context[
                    suite_context.active_test_case_id
                ]
                case_context.logs.append(msg)


def build_plan_logger(plan_name: str, context: ExecutionContext) -> Logger:
    plan_logger = getLogger(plan_name)
    plan_logger.setLevel(INFO)
    plan_logger.addHandler(StreamHandler(stream=sys.stdout))
    plan_logger.addHandler(TestPlanLoggerHandler(context))
    return plan_logger
