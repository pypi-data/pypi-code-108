import unittest

from rox.core.entities.flag import Flag
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

class FlagTests(unittest.TestCase):
    def test_flag_without_default_value(self):
        flag = Flag()
        self.assertFalse(flag.is_enabled(None))

    def test_flag_with_default_value(self):
        flag = Flag(True)
        self.assertTrue(flag.is_enabled(None))

    def test_will_invoke_enabled_action(self):
        flag = Flag(True)
        is_called = {'called': False}

        def action():
            is_called['called'] = True

        flag.enabled(None, action)

        self.assertTrue(is_called['called'])

    def test_will_invoke_disabled_action(self):
        flag = Flag()
        is_called = {'called': False}

        def action():
            is_called['called'] = True

        flag.disabled(None, action)

        self.assertTrue(is_called['called'])

    def test_should_return_false_when_flag_dependency_does_not_exist(self):
        flag = Flag(True)
        flag.condition = 'flagValue("fff")'
        flag.parser = Mock()
        self.assertFalse(flag.is_enabled())
