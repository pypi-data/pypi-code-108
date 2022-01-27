from doctest import ELLIPSIS
# from doctest import OutputChecker as BaseOutputChecker

# import pytest
from sybil import Sybil
from sybil.example import Example  # sbt
# from sybil.parsers.capture import parse_captures
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.doctest import DocTest  # sbt
# from scottbrian_utils.time_hdr import get_datetime_match_string
# import re
# import os
# from typing import Any

# class SbtOutputChecker(BaseOutputChecker):
#     def __init__(self):
#         self.mod_name = None
#         self.msgs = []
#
#     def check_output(self, want, got, optionflags):
#         old_want = want
#         old_got = got
#
#         def repl_dt(match_obj: Any) -> str:
#             return found_items.__next__().group()
#
#         if self.mod_name == 'time_hdr' or self.mod_name == 'README':
#             # find the actual occurrences and replace in want
#             for time_hdr_dt_format in ["%a %b %d %Y %H:%M:%S",
#                                        "%m/%d/%y %H:%M:%S"]:
#                 match_str = get_datetime_match_string(time_hdr_dt_format)
#
#                 match_re = re.compile(match_str)
#                 found_items = match_re.finditer(got)
#                 want = match_re.sub(repl_dt, want)
#
#             # replace elapsed time in both want and got
#             match_str = 'Elapsed time: 0:00:00.[0-9| ]{6,6}'
#             replacement = 'Elapsed time: 0:00:00       '
#             want = re.sub(match_str, replacement, want)
#             got = re.sub(match_str, replacement, got)
#
#         if self.mod_name == 'file_catalog' or self.mod_name == 'README':
#             match_str = r'\\'
#             replacement = '/'
#             got = re.sub(match_str, replacement, got)
#
#             match_str = '//'
#             replacement = '/'
#             got = re.sub(match_str, replacement, got)
#
#         if self.mod_name == 'diag_msg' or self.mod_name == 'README':
#             for diag_msg_dt_fmt in ["%H:%M:%S.%f","%a %b-%d %H:%M:%S"]:
#                 match_str = get_datetime_match_string(diag_msg_dt_fmt)
#
#                 match_re = re.compile(match_str)
#                 found_items = match_re.finditer(got)
#                 want = match_re.sub(repl_dt, want)
#
#             match_str = "<.+?>"
#             replacement = '<input>'
#             got = re.sub(match_str, replacement, got)
#
#         self.msgs.append([old_want, want, old_got, got])
#         return BaseOutputChecker.check_output(self, want, got, optionflags)


class SbtDocTestParser(DocTestParser):
    def __init__(self, optionflags=0):
        DocTestParser.__init__(self, optionflags=optionflags)
        # self.runner._checker = SbtOutputChecker()

    def evaluate(self, sybil_example: Example) -> str:
        example = sybil_example.parsed
        namespace = sybil_example.namespace
        output = []
        mod_name = sybil_example.path.rsplit(sep=".", maxsplit=1)[0]
        mod_name = mod_name.rsplit(sep="\\", maxsplit=1)[1]
        # self.runner._checker.mod_name = mod_name

        self.runner.run(
            DocTest([example], namespace, name=None,
                    filename=None, lineno=example.lineno, docstring=None),
            clear_globs=False,
            out=output.append
        )
        # print(f'{self.runner._checker.msgs=}')
        # self.runner._checker.msgs = []
        return ''.join(output)


pytest_collect_file = Sybil(
    parsers=[
        SbtDocTestParser(optionflags=ELLIPSIS),
        PythonCodeBlockParser(),
    ],
    patterns=['*.rst', '*.py'],
    # excludes=['log_verifier.py']
).pytest()
