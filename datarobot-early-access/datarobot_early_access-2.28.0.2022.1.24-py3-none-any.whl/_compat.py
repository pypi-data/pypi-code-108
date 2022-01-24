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
"""
This module contains compatibility fixes to allow usage of both 1.x and 2.x Trafaret versions
"""
try:
    from trafaret import ToInt as Int
except ImportError:
    from trafaret import Int  # noqa


try:
    from trafaret import AnyString as String
except ImportError:
    from trafaret import String  # noqa
