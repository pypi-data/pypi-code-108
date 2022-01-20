# Copyright 2019 Splunk Inc. All rights reserved.

""" The Reporter class is intended to be used as a general interface to send
errors detected during validation to.

This is done in order to avoid raising errors for logging, and instead
provide a mechanism to store and retrieve report records such that a completed
validation check can be performed and provide detailed feedback for the errors
encountered.
"""
import codecs
import collections
import inspect
import json
import logging
import os.path
import re
import string
import traceback
from datetime import datetime
from functools import reduce


def unknown_char(e):
    return "?", e.end


codecs.register_error("unknown_char", unknown_char)

logger = logging.getLogger(__name__)
# Used for storing the records, no ReportRecord class created because OO not
# needed
ReportRecord = collections.namedtuple(
    "ReportRecord",
    [
        "result",
        "message",
        "filename",
        "line",
        "code",
        "message_filename",
        "message_line",
    ],
)
MAX_MESSAGES_PER_CHECK = 25

STATUS_TYPES = (
    "error",
    "failure",
    "skipped",
    "manual_check",
    "not_applicable",
    "warning",
    "success",
)

STATUS_PRIORITIES = {status: idx for (idx, status) in enumerate(STATUS_TYPES)}

FILE_PATTERN = re.compile(r"(F|f)ile:\s*[.,0-9a-zA-Z\\/_-]*")
LINE_PATTERN = re.compile(r"(L|l)ine\s*\w*:\s*[\d.]*")


def _reduce_record_summary(acc, x):
    acc[x.result] = acc.get(x.result, 0) + 1
    return acc


def _extract_values(pattern, message):
    """Find the filename AND line depending on the pattern."""
    v1, v2 = "", ""
    result = pattern.search(message)
    if result:
        group = result.group()
        v1, v2 = group.split(":", 1)
    # strip [,.] from captured line number for normalizing message
    # is (filename, lineno) is not passed as params
    return tuple(map(lambda x: re.sub(r"[,.]$", r"", x.strip()), (v1, v2)))


def extract_filename_lineno(message):
    filename = _extract_values(FILE_PATTERN, message)[1]
    lineno = _extract_values(LINE_PATTERN, message)[1]
    return filename, lineno


class Reporter(object):
    def __init__(self):
        self._report_records = []
        self.metrics = {"start_time": None, "end_time": None, "execution_time": None}

    def report_records(
        self, max_records=MAX_MESSAGES_PER_CHECK, status_types_to_return=STATUS_TYPES
    ):
        """Returns a list of the report records that have been accumulated

        :param: max_records The number of records to return. To return all
            records pass in sys.maxint
        :param: status_types_to_return a list of strings specifying the report
            status types to return
        """
        all_records = sorted(
            self._report_records, key=lambda x: STATUS_PRIORITIES[x.result]
        )
        filtered_records = [
            report_record
            for report_record in all_records
            if report_record.result in status_types_to_return
        ]
        if len(filtered_records) > max_records:
            last_index = max_records - 1  # Last record is a summary of the remainder
            records = filtered_records[:last_index]
            remainder = filtered_records[last_index:]
            counts = reduce(_reduce_record_summary, remainder, dict())
            summaries = []
            for status, count in iter(counts.items()):
                summaries.append(f"{count} {status} messages")
            text = ", ".join(summaries)

            # Used to respect to __save_result_message conventions
            current_frame = inspect.currentframe()
            (
                _,
                check_file_path,
                check_code_hit_line_number,
                _,
                check_code_hit_line,
                _,
            ) = inspect.getouterframes(current_frame)[1]
            _, check_code_fine_name = os.path.split(check_file_path)
            records.append(
                ReportRecord(
                    "warning",
                    "Suppressed " + text,
                    check_code_fine_name,
                    check_code_hit_line_number,
                    check_code_hit_line[0].strip(),
                    None,
                    None,
                )
            )
            return records

        return filtered_records

    def __save_result_message(
        self,
        result,
        message,
        frame,
        message_file_name=None,
        message_line_number=None,
        frame_offset=1,
    ):
        # What is this black magic below????
        (
            _,
            check_file_path,
            check_code_hit_line_number,
            _,
            check_code_hit_line,
            _,
        ) = inspect.getouterframes(frame)[frame_offset]
        _, check_code_file_name = os.path.split(check_file_path)
        message_stripped_of_unprintables = "".join(
            s for s in message if s in string.printable
        )
        report_record = ReportRecord(
            result,
            message_stripped_of_unprintables,
            check_code_file_name,
            check_code_hit_line_number,
            check_code_hit_line[0].strip(),
            message_file_name,
            message_line_number,
        )
        self._report_records.append(report_record)

    @staticmethod
    def __format_message(message, message_file_name=None, message_line_number=None):
        """Formats file and numbers in a consistent fashion"""
        # tailor file_name, then line_number
        file_info_tailored_message = FILE_PATTERN.sub("", message, 1)
        tailored_message = LINE_PATTERN.sub("", file_info_tailored_message, 1).strip()

        captured_file_name, captured_line_number = extract_filename_lineno(message)
        output_file_name = message_file_name or captured_file_name
        output_line_number = message_line_number or captured_line_number

        if output_file_name and not output_line_number:
            return f"{tailored_message} File: {output_file_name}"
        if output_file_name and output_line_number:
            return f"{tailored_message} File: {output_file_name} Line Number: {output_line_number}"

        return tailored_message

    def warn(self, message, file_name=None, line_number=None):
        """A warn will require that the app be inspected by a real human. Like a
        todo item
        """
        reporter_output = self.__format_message(
            message, message_file_name=file_name, message_line_number=line_number
        )
        self.__save_result_message(
            "warning",
            reporter_output,
            inspect.currentframe(),
            message_file_name=file_name,
            message_line_number=line_number,
        )

    def assert_warn(self, assertion, message, file_name=None, line_number=None):
        """If assertion is false, log a warning"""
        if not assertion:
            self.warn(message, file_name, line_number)

    def manual_check(self, message, file_name=None, line_number=None):
        """Declare that this check requires a human to validate"""
        reporter_output = self.__format_message(
            message, message_file_name=file_name, message_line_number=line_number
        )
        self.__save_result_message(
            "manual_check",
            reporter_output,
            inspect.currentframe(),
            message_file_name=file_name,
            message_line_number=line_number,
        )

    def assert_manual_check(self, assertion, message, file_name=None, line_number=None):
        """If assertion is false, add to a human's todo list"""
        if not assertion:
            self.manual_check(message, file_name, line_number)

    def not_applicable(self, message):
        """Report that this check does not apply to the current app"""
        self.__save_result_message("not_applicable", message, inspect.currentframe())
        logger.debug(message)

    def skip(self, message):
        """Report that this check was not run."""
        self.__save_result_message("skipped", message, inspect.currentframe())
        logger.debug(message)

    def assert_not_applicable(self, assertion, message):
        """If assertion is false, put this in a human's queue"""
        if not assertion:
            self.not_applicable(message)

    def fail(self, message, file_name=None, line_number=None):
        """Failure is when a problem has been found that the app can't be
        accepted without fixing
        """
        reporter_output = self.__format_message(
            message, message_file_name=file_name, message_line_number=line_number
        )
        self.__save_result_message(
            "failure",
            reporter_output,
            inspect.currentframe(),
            message_file_name=file_name,
            message_line_number=line_number,
        )

    def ast_manual_check(self, message, files_with_ast_results):
        self._ast_report(message, files_with_ast_results, self.manual_check)

    def ast_fail(self, message, files_with_ast_results):
        self._ast_report(message, files_with_ast_results, self.fail)

    @staticmethod
    def _ast_report(message, files_with_ast_results, report_function):
        for file_path, usage in files_with_ast_results.items():
            for component, results in usage.items():
                for result in results:
                    if "args" in result:
                        check_message = message.format(
                            component,
                            json.dumps(result["args"], ensure_ascii=False),
                            json.dumps(result["keywords"], ensure_ascii=False),
                        )
                    else:
                        check_message = message.format(component)
                    report_function(
                        check_message,
                        file_name=file_path,
                        line_number=result["line_number"],
                    )

    def assert_fail(self, assertion, message, file_name=None, line_number=None):
        """If assertion is false, log failure"""
        if not assertion:
            self.fail(message, file_name, line_number)

    def exception(self, exception, category="error"):
        """Error is when there's something wrong with the check script.
        Don't call this directly- just throw an exception
        """
        message = str(exception[1])
        stack_frame = traceback.extract_tb(exception[2])[0]
        line_number = None
        code_section = None
        filename = None

        if stack_frame:
            filename = stack_frame[0]
            line_number = stack_frame[1]
            code_section = stack_frame[3]

        report_record = ReportRecord(
            category, message, filename, line_number, code_section, None, None
        )
        self._report_records.append(report_record)

    def warnings(self):
        """Retrieve all advice report_records to return to submitter"""
        return [m for m in self._report_records if m.result == "warning"]

    def start(self):
        """Sets metrics to store when the check started."""
        self.metrics["start_time"] = datetime.now()

    def complete(self):
        """Sets metrics to store when the check completed."""
        if self.metrics["start_time"] is None:
            raise Exception("Start must be called prior to complete.")
        self.metrics["end_time"] = datetime.now()
        self.metrics["execution_time"] = (
            self.metrics["end_time"] - self.metrics["start_time"]
        ).total_seconds()

    def state(self):
        """Return the overall state of the checks
        Checks can be (In order of severity):
        - error
        - failure
        - manual_check
        - warning
        - not_applicable
        - skipped
        - success  # default

        Note that the reporter starts in a success state, and if there is no
        interaction it will stay that way.
        """
        # Relates to ACD-1001
        counts = reduce(_reduce_record_summary, self._report_records, dict())
        for index in [
            "error",
            "failure",
            "manual_check",
            "warning",
            "not_applicable",
            "skipped",
        ]:
            if counts.get(index, -1) > 0:
                return index
        return "success"
