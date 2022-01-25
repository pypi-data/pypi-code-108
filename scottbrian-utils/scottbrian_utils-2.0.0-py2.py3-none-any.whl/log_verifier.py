"""Module log_verifier.

======
LogVer
======

The LogVer class is intended to be used during testing to allow a
test case to specify expected log messages and then verify that they
have been issued.

:Example1: pytest test case logs a message and verifies

>>> from scottbrian_utils.log_verifier import LogVer
>>> import logging
>>> def test_example1(caplog: pytest.CaptureFixture[str]) -> None:
...     logger = logging.getLogger('example_1')
...     log_ver = LogVer('example_1')
...     log_msg = 'hello'
...     log_ver.add_msg(log_msg=log_msg)
...     logger.debug(log_msg)
...     match_results = log_ver.get_match_results(caplog=caplog)
...     log_ver.print_match_results(match_results)
...     log_ver.verify_log_results(match_results)
<BLANKLINE>
**********************************
* number expected log records: 1 *
* number expected unmatched  : 0 *
* number actual log records  : 1 *
* number actual unmatched    : 0 *
* number of matched records  : 1 *
**********************************
<BLANKLINE>
*********************************
* unmatched expected records    *
* (logger name, level, message) *
*********************************
<BLANKLINE>
*********************************
* unmatched actual records      *
* (logger name, level, message) *
*********************************
<BLANKLINE>
*********************************
* matched records               *
* (logger name, level, message) *
*********************************
('example_1', 10, 'hello')


:Example2: pytest test case expects two log records, only one was issued

>>> from scottbrian_utils.log_verifier import LogVer
>>> import logging
>>> def test_example2(caplog: pytest.CaptureFixture[str]) -> None:
...      logger = logging.getLogger('example_2')
...      log_ver = LogVer('example_2')
...      log_msg1 = 'hello'
...      log_ver.add_msg(log_msg=log_msg1)
...      log_msg2 = 'goodbye'
...      log_ver.add_msg(log_msg=log_msg2)
...      logger.debug(log_msg1)
...      log_ver.get_match_results()
...      log_ver.print_match_results()
<BLANKLINE>
**********************************
* number expected log records: 2 *
* number expected unmatched  : 1 *
* number actual log records  : 1 *
* number actual unmatched    : 0 *
* number of matched records  : 1 *
**********************************
<BLANKLINE>
*********************************
* unmatched expected records    *
* (logger name, level, message) *
*********************************
('example_2', 10, 'goodbye')
<BLANKLINE>
*********************************
* unmatched actual records      *
* (logger name, level, message) *
*********************************
<BLANKLINE>
*********************************
* matched records               *
* (logger name, level, message) *
*********************************
('example_2', 10, 'hello')


:Example3: pytest test case expects one log record, two were issued

>>> from scottbrian_utils.log_verifier import LogVer
>>> import logging
>>> def test_example3(caplog: pytest.CaptureFixture[str]) -> None:
...      logger = logging.getLogger('example_3')
...      log_ver = LogVer('example_3')
...      log_msg1 = 'hello'
...      log_ver.add_msg(log_msg=log_msg1)
...      log_msg2 = 'goodbye'
...      logger.debug(log_msg1)
...      logger.debug(log_msg2)
...      log_ver.get_match_results()
...      log_ver.print_match_results()
<BLANKLINE>
**********************************
* number expected log records: 1 *
* number expected unmatched  : 0 *
* number actual log records  : 2 *
* number actual unmatched    : 1 *
* number of matched records  : 1 *
**********************************
<BLANKLINE>
*********************************
* unmatched expected records    *
* (logger name, level, message) *
*********************************
<BLANKLINE>
*********************************
* unmatched actual records      *
* (logger name, level, message) *
*********************************
('example_3', 10, 'goodbye')
<BLANKLINE>
*********************************
* matched records               *
* (logger name, level, message) *
*********************************
('example_3', 10, 'hello')


:Example4: pytest test case expect two log records, two were issued,
           one different

>>> from scottbrian_utils.log_verifier import LogVer
>>> import logging
>>> def test_example4(caplog: pytest.CaptureFixture[str]) -> None:
...      logger = logging.getLogger('example_4')
...      log_ver = LogVer('example_4')
...      log_msg1 = 'hello'
...      log_ver.add_msg(log_msg=log_msg1)
...      log_msg2a = 'goodbye'
...      log_ver.add_msg(log_msg=log_msg2a)
...      log_msg2b = 'see you soon'
...      logger.debug(log_msg1)
...      logger.debug(log_msg2b)
...      log_ver.get_match_results()
...      log_ver.print_match_results()
<BLANKLINE>
**********************************
* number expected log records: 2 *
* number expected unmatched  : 1 *
* number actual log records  : 2 *
* number actual unmatched    : 1 *
* number of matched records  : 1 *
**********************************
<BLANKLINE>
*********************************
* unmatched expected records    *
* (logger name, level, message) *
*********************************
('example_4', 10, 'goodbye')
<BLANKLINE>
*********************************
* unmatched actual records      *
* (logger name, level, message) *
*********************************
('example_4', 10, 'see you soon')
<BLANKLINE>
*********************************
* matched records               *
* (logger name, level, message) *
*********************************
('example_4', 10, 'hello')


The log_verifier module contains:

    1) LogVer class with methods:

       a. add_call_seq
       b. get_call_seq
       c. add_msg
       d. verify_log_msgs

"""

########################################################################
# Standard Library
########################################################################
from dataclasses import dataclass
import logging
import pytest
import re
from typing import Any, Optional, Union

########################################################################
# Third Party
########################################################################

########################################################################
# Local
########################################################################
from scottbrian_utils.flower_box import print_flower_box_msg

########################################################################
# type aliases
########################################################################
IntFloat = Union[int, float]
OptIntFloat = Optional[IntFloat]


########################################################################
# Msg Exceptions classes
########################################################################
class LogVerError(Exception):
    """Base class for exception in this module."""
    pass


class UnmatchedExpectedMessages(LogVerError):
    """Unmatched expected messages were found during verify."""
    pass


class UnmatchedActualMessages(LogVerError):
    """Unmatched actual messages were found during verify."""
    pass


@dataclass
class MatchResults:
    """Match results returned by get_match_results method."""
    num_exp_records: int
    num_exp_unmatched: int
    num_actual_records: int
    num_actual_unmatched: int
    num_records_matched: int
    unmatched_exp_records: list[tuple[str, int, Any]]
    unmatched_actual_records: list[tuple[str, int, Any]]
    matched_records: list[tuple[str, int, Any]]


########################################################################
# LogVer class
########################################################################
class LogVer:
    """Log Message Verification Class."""

    ####################################################################
    # __init__
    ####################################################################
    def __init__(self,
                 log_name: str = 'root') -> None:
        """Initialize a LogVer object.

        Args:
            log_name: name of the logger

        Example: create a logger and a LogVer instance
        >>> logger = logging.getLogger('example_logger')
        >>> log_ver = LogVer('example_logger')

        """
        self.call_seqs: dict[str, str] = {}
        self.expected_messages: list[tuple[str, int, Any]] = []
        self.log_name = log_name

    ####################################################################
    # add_call_seq
    ####################################################################
    def add_call_seq(self,
                     name: str,
                     seq: str) -> None:
        """Add a call sequence for a given name.

        Args:
            name: name for whom the call sequence represents
            seq: the call sequence in a format as described by
                   get_formatted_call_sequence in diag_msg.py
                   from the scottbrian_utils package

        """
        self.call_seqs[name] = seq + ':[0-9]*'

    ####################################################################
    # add_call_seq
    ####################################################################
    def get_call_seq(self,
                     name: str) -> str:
        """Retrieve a call sequence by name.

        Args:
            name: name for whom the call sequence represents

        Returns:
            the call sequence in a format as described by
              get_formatted_call_sequence in diag_msg.py with the regex
              string ":[0-9]*" appended to represent the source line
              number to match

        """
        return self.call_seqs[name]

    ####################################################################
    # add_msg
    ####################################################################
    def add_msg(self,
                log_msg: str,
                log_level: int = logging.DEBUG,
                log_name: Optional[str] = None) -> None:
        """Add a message to the expected log messages.

        Args:
            log_msg: expected message to add
            log_level: expected logging level
            log_name: expected logger name

        Example: add two messages, each at a different level

        >>> def test_example(caplog: pytest.CaptureFixture[str]
        ...                 ) -> None:
        ...      logger = logging.getLogger('add_msg')
        ...      log_ver = LogVer('add_msg')
        ...      log_msg1 = 'hello'
        ...      log_msg2 = 'goodbye'
        ...      log_ver.add_msg(log_msg=log_msg1)
        ...      log_ver.add_msg(log_msg=log_msg2,
        ...                      log_level=logging.ERROR)
        ...      logger.debug(log_msg1)
        ...      logger.error(log_msg2)
        ...      match_results = log_ver.get_match_results()
        ...      log_ver.print_match_results(match_results)
        ...      log_ver.verify_log_results(match_results)
        <BLANKLINE>
        **********************************
        * number expected log records: 2 *
        * number expected unmatched  : 1 *
        * number actual log records  : 1 *
        * number actual unmatched    : 0 *
        * number of matched records  : 1 *
        **********************************
        <BLANKLINE>
        *********************************
        * unmatched expected records    *
        * (logger name, level, message) *
        *********************************
        <BLANKLINE>
        *********************************
        * unmatched actual records      *
        * (logger name, level, message) *
        *********************************
        <BLANKLINE>
        *********************************
        * matched records               *
        * (logger name, level, message) *
        *********************************
        ('add_msg', 10, 'hello')
        ('add_msg', 40, 'goodbye')

        """
        if log_name:
            log_name_to_use = log_name
        else:
            log_name_to_use = self.log_name
        self.expected_messages.append((log_name_to_use,
                                       log_level,
                                       re.compile(log_msg)
                                       ))

    ####################################################################
    # get_match_results
    ####################################################################
    def get_match_results(self,
                          caplog: pytest.CaptureFixture[str]
                          ) -> MatchResults:
        """Match the expected to actual log records.

        Args:
            caplog: pytest fixture that captures log messages

        Returns:
            Number of expected records, number of actual records,
              number of matching records, list of unmatched expected
              records, list of unmatched actual records, and list
              or matching records

        """
        unmatched_exp_records: list[tuple[str, int, Any]] = []
        unmatched_actual_records: list[tuple[str, int, Any]] = []
        matched_records: list[tuple[str, int, Any]] = []

        # make a work copy of expected records
        for record in self.expected_messages:
            unmatched_exp_records.append(record)

        # make a work copy of actual records
        for record in caplog.record_tuples:
            unmatched_actual_records.append(record)

        # find matches, update working copies to reflect results
        for actual_record in caplog.record_tuples:
            for idx, exp_record in enumerate(unmatched_exp_records):
                # check that the logger name, level, and message match
                if (exp_record[0] == actual_record[0]
                        and exp_record[1] == actual_record[1]
                        and exp_record[2].match(actual_record[2])):
                    unmatched_exp_records.pop(idx)
                    unmatched_actual_records.remove(actual_record)
                    matched_records.append((actual_record[0],
                                            actual_record[1],
                                            actual_record[2]))
                    break

        # convert unmatched expected records to string form
        unmatched_exp_records_2 = []
        for item in unmatched_exp_records:
            unmatched_exp_records_2.append((item[0],
                                            item[1],
                                            item[2].pattern))

        return MatchResults(num_exp_records=len(self.expected_messages),
                            num_exp_unmatched=len(unmatched_exp_records_2),
                            num_actual_records=len(caplog.records),
                            num_actual_unmatched=len(unmatched_actual_records),
                            num_records_matched=len(matched_records),
                            unmatched_exp_records=unmatched_exp_records_2,
                            unmatched_actual_records=unmatched_actual_records,
                            matched_records=matched_records)

    ####################################################################
    # print_match_results
    ####################################################################
    def print_match_results(self,
                            match_results: MatchResults) -> None:
        """Print the match results.

        Args:
            match_results: contains the results to be printed

        """
        max_num = max(match_results.num_exp_records,
                      match_results.num_exp_unmatched,
                      match_results.num_actual_records,
                      match_results.num_actual_unmatched,
                      match_results.num_records_matched)
        max_len = len(str(max_num))
        msg1 = ('number expected log records: '
                f'{match_results.num_exp_records:>{max_len}}')
        msg2 = ('number expected unmatched  : '
                f'{match_results.num_exp_unmatched:>{max_len}}')
        msg3 = ('number actual log records  : '
                f'{match_results.num_actual_records:>{max_len}}')
        msg4 = ('number actual unmatched    : '
                f'{match_results.num_actual_unmatched:>{max_len}}')
        msg5 = ('number matched records     : '
                f'{match_results.num_records_matched:>{max_len}}')

        print_flower_box_msg([msg1, msg2, msg3, msg4, msg5])

        legend_msg = '(logger name, level, message)'
        print_flower_box_msg(['unmatched expected records', legend_msg])
        for log_msg in match_results.unmatched_exp_records:
            print(log_msg)

        print_flower_box_msg(['unmatched actual records', legend_msg])
        for log_msg in match_results.unmatched_actual_records:
            print(log_msg)

        print_flower_box_msg(['matched records', legend_msg])
        for log_msg in match_results.matched_records:
            print(log_msg)

    ####################################################################
    # verify log messages
    ####################################################################
    @staticmethod
    def verify_log_results(match_results: MatchResults) -> None:
        """Verify that each log message issued is as expected.

        Args:
            match_results: contains the results to be verified

        Raises:
            UnmatchedExpectedMessages: There are expected log messages
                that failed to match actual log messages.
            UnmatchedActualMessages: There are actual log messages that
                failed to match expected log messages.

        """
        if match_results.num_exp_unmatched:
            raise UnmatchedExpectedMessages(
                f'There are {match_results.num_exp_unmatched} '
                'expected log messages that failed to match actual log '
                'messages.')

        if match_results.num_actual_unmatched:
            raise UnmatchedActualMessages(
                f'There are {match_results.num_actual_unmatched} '
                'actual log messages that failed to match expected log '
                'messages.')
