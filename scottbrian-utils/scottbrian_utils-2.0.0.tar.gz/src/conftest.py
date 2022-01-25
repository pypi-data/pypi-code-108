#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 19:54:08 2020

@author: Scott Tuttle
"""

from doctest import OutputChecker
from unittest import mock

import pytest


class DateTimeOutputChecker(OutputChecker):
    """This class is used to intercept the output of doctest examples.

    The datetime fields are changed to match the expected datetimes that
    are documented in the module examples.
    """

    def check_output(self, want: str, got: str, optionFlags: int) -> bool:
        """Method to fix up the doctest examples.

        Args:
            want: the expected output specified in the example
            got: the output collected by doctest when the example is run
            optionFlags : provides some customization options - see
                            doctest documentation for details

        Returns:
            True if the example want matches the got, False if not

        """
        new_got = got
        # print(want)
        # print(got)
        # handle starting case
        if (('Starting' in want)
           and ('Starting' in new_got)):
            DT_idx_want_start = want.find('Starting')
            DT_idx_got_start = new_got.find('Starting')
            DT_idx_want_stop = want.find('*', DT_idx_want_start)
            DT_idx_got_stop = new_got.find('*', DT_idx_got_start)

            new_got = new_got[0:DT_idx_got_start] \
                + want[DT_idx_want_start:DT_idx_want_stop] \
                + new_got[DT_idx_got_stop:]

        # handle ending case
        if (('Ending' in want)
           and ('Ending' in new_got)):
            DT_idx_want_start = want.find('Ending')
            DT_idx_got_start = new_got.find('Ending')
            DT_idx_want_stop = want.find('*', DT_idx_want_start)
            DT_idx_got_stop = new_got.find('*', DT_idx_got_start)

            new_got = new_got[0:DT_idx_got_start] \
                + want[DT_idx_want_start:DT_idx_want_stop] \
                + new_got[DT_idx_got_stop:]

        # handle elapsed time case
        if (('Elapsed time:' in want)
           and ('Elapsed time:' in new_got)):
            DT_idx_want_start = want.find('Elapsed time:')
            DT_idx_got_start = new_got.find('Elapsed time:')
            DT_idx_want_stop = want.find('*', DT_idx_want_start)
            DT_idx_got_stop = new_got.find('*', DT_idx_got_start)

            new_got = new_got[0:DT_idx_got_start] \
                + want[DT_idx_want_start:DT_idx_want_stop] \
                + new_got[DT_idx_got_stop:]

        if 'this is a diagnostic message' in want:
            start_of_msg_want = want.find('this is a diagnostic message')
            start_of_msg_got = got.find('this is a diagnostic message')
            new_got = want[0:start_of_msg_want] + new_got[start_of_msg_got:]

        # if 'diagnostic info' in want:
        #     start_of_msg_want = want.find('diagnostic info')
        #     start_of_msg_got = got.find('diagnostic info')
        #     new_got = want[0:start_of_msg_want] + new_got[start_of_msg_got:]

        if 'CallerInfo' in want:
            start_cls_want = want.find('cls_name=')
            start_cls_got = got.find('cls_name=')
            new_got = want[0:start_cls_want] + new_got[start_cls_got:]

        gfcs_suffix = 'get_formatted_call_sequence['
        dm_suffix = 'diag_msg['
        if gfcs_suffix in got or dm_suffix in got:
            brkt1_num = '0'
            brkt2_num = '0'
            brkt3_num = '0'
            brkt1 = got.find('[')
            if brkt1 > 0:
                r_brkt1 = got.find(']', brkt1)
                brkt1_num = got[brkt1+1:r_brkt1]
                brkt2 = got.find('[', brkt1+1)
                if brkt2 > 0:
                    r_brkt2 = got.find(']', brkt2)
                    brkt2_num = got[brkt2+1:r_brkt2]
                    brkt3 = got.find('[', brkt2 + 1)
                    if brkt3 > 0:
                        r_brkt3 = got.find(']', brkt3)
                        brkt3_num = got[brkt3+1:r_brkt3]

            prefix = '<doctest scottbrian_utils.diag_msg.'
            suffix = gfcs_suffix if gfcs_suffix in got else dm_suffix
            old1 = prefix + suffix + brkt1_num + ']>'
            old2 = prefix + suffix + brkt2_num + ']>'
            old3 = prefix + suffix + brkt3_num + ']>'

            new_text = '<input>'
            if old1 in new_got:
                new_got = new_got.replace(old1, new_text)
            if old2 in new_got:
                new_got = new_got.replace(old2, new_text)
            if old3 in new_got:
                new_got = new_got.replace(old3, new_text)

            # handle time stamp
            if dm_suffix in got:  # if diag_msg
                lt_sign_idx = want.find('<')
                if lt_sign_idx > 0:
                    new_got = want[0:lt_sign_idx] + new_got[lt_sign_idx:]

        return OutputChecker.check_output(self, want, new_got, optionFlags)


@pytest.fixture(autouse=True)
def DateTime_out():
    with mock.patch('doctest.OutputChecker', DateTimeOutputChecker):
        yield
