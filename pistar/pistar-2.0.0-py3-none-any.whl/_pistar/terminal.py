import shutil
import sys
from typing import Optional, TextIO

from colorama import Fore

from _pistar.utilities.constants import PISTAR_TESTCASE_EXECUTION_STATUS as PISTAR_STATUS

width = shutil.get_terminal_size().columns - 2
log_sep = "-"
log_sep_summary = "="


def get_terminal_width() -> int:
    _width = shutil.get_terminal_size().columns
    return _width


class TerminalWriter:
    def __init__(self, file: Optional[TextIO] = None):
        if file is None:
            file = sys.stdout
        self._file = file
        self._terminal_width: Optional[int] = None

    @property
    def fullwidth(self) -> int:
        if self._terminal_width is not None:
            return self._terminal_width
        return get_terminal_width()

    @fullwidth.setter
    def fullwidth(self, value: int) -> None:
        self._terminal_width = value

    def flush(self):
        self._file.flush()

    def write(self, msg: str):
        self._file.write(msg)

    def line(self, msg: str):
        self._file.write(msg)
        self._file.write('\n')

    def sep(self, sepchar: str, title: str, fullwidth: Optional[int] = None) -> None:
        if fullwidth is None:
            fullwidth = self.fullwidth
        line = f" {title} ".center(fullwidth, sepchar)
        self.line(line)


def console_output(message):
    print(message)


def console_testcase_start(testcase):
    print(f" {testcase.__name__} start ".center(width, log_sep))


def console_testcase_end(testcase):
    print(f" {testcase.__name__} end ".center(width, log_sep) + "\n")


def format_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.2f}s "

    mm, ss = divmod(int(seconds), 60)
    hh, mm = divmod(mm, 60)
    dd, hh = divmod(hh, 24)
    if dd < 1:
        if hh < 1:
            return f"{mm}m{ss}s "
        else:
            return f"{hh}h{mm}m{ss}s "
    plural = dd != 1 and "s" or ""
    return f"{dd} day{plural} {hh}h{mm}m{ss}s "


def console_summary_collection(results, time_consuming, no_color):
    passed_num = 0
    failed_num = 0
    error_num = 0
    passed_testcases = []
    failed_testcases = []
    error_testcases = []

    for key, value in results.items():
        if value == PISTAR_STATUS.PASSED:
            passed_num += 1
            passed_testcases.append(key)
        elif value == PISTAR_STATUS.FAILED:
            failed_num += 1
            failed_testcases.append(key)
        else:
            error_num += 1
            error_testcases.append(key)

    if passed_num or failed_num or error_num:
        print(" test summary info ".center(width, log_sep_summary))

    console_output_case_result(passed_testcases, failed_testcases, error_testcases, no_color)
    console_output_summary(passed_num, failed_num, error_num, time_consuming)


def console_output_case_result(passed_testcases, failed_testcases, error_testcases, no_color):
    pre_pass = "" if no_color else Fore.GREEN
    pre_case = "" if no_color else Fore.RESET
    pre_no_pass = "" if no_color else Fore.RED

    for testcase in passed_testcases:
        print(pre_pass + "PASSED", end=" ")
        print(pre_case + testcase)
    for testcase in error_testcases:
        print(pre_no_pass + "ERROR", end=" ")
        print(pre_case + testcase)
    for testcase in failed_testcases:
        print(pre_no_pass + "FAILED", end=" ")
        print(pre_case + testcase)


def console_output_summary(passed_num, failed_num, error_num, time_consuming):
    summary_info = ""
    summary_info += f" {error_num} error" if error_num else ""
    if error_num != 0 and (failed_num != 0 or passed_num != 0):
        summary_info += ","
    summary_info += f" {failed_num} failed" if failed_num else ""
    if failed_num != 0 and passed_num != 0:
        summary_info += ","
    summary_info += f" {passed_num} passed" if passed_num else ""

    summary_info += " in " if summary_info else " no test cases ran in "
    summary_info += format_time(time_consuming * 0.001)
    print(summary_info.center(width, log_sep_summary))
