# -*- coding: utf-8 -*-
from cpskin.core.testing import CPSKIN_CORE_ROBOT_TESTING
# from plone.app.robotframework.utils import disableCSRFProtection
from plone.testing import layered

import robotsuite
import unittest


def test_suite():
    # disableCSRFProtection()
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite('robot'),
                layer=CPSKIN_CORE_ROBOT_TESTING),
    ])
    return suite
