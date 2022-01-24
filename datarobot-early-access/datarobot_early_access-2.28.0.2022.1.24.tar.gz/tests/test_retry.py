#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import mock
import six

from datarobot.utils import retry

zip = six.moves.zip


def test_wait():
    delay, maxdelay = retry.wait.__defaults__
    assert list(index for index, _ in retry.wait(0)) == [0]
    assert list(index for index, _ in retry.wait(delay)) == [0, 1]
    it = (index for index, _ in retry.wait(float("inf")))
    expected = 0.1, 0.2, 0.4
    with mock.patch("datarobot.utils.retry.time.sleep") as sleep:
        assert next(it) == 0 and not sleep.called
        for index, delay in zip(it, expected):
            assert sleep.call_args[0] == (delay,)
    assert index == len(expected)
