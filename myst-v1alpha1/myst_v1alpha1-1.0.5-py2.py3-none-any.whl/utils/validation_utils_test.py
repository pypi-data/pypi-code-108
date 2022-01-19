import unittest
from collections import OrderedDict

from myst_v1alpha1.utils.validation_utils import validate_mutually_exclusive_arguments


class ValidationUtilsTest(unittest.TestCase):
    def test_validate_mutually_exclusive_arguments(self):
        # Test that by default, we don't require one argument to be specified.
        self.assertEqual(
            validate_mutually_exclusive_arguments(
                OrderedDict([("first", None), ("second", None), ("third", None), ("fourth", None)])
            ),
            None,
        )

        # Test that we can require one argument to be specified.
        self.assertEqual(
            validate_mutually_exclusive_arguments(
                OrderedDict([("first", None), ("second", "value_2"), ("third", None), ("fourth", None)]),
                require_one=True,
            ),
            ("second", "value_2"),
        )

        # Test that we can require one argument to be specified, and raise if none are specified.
        with self.assertRaises(ValueError):
            validate_mutually_exclusive_arguments(
                OrderedDict([("first", None), ("second", None), ("third", None), ("fourth", None)]), require_one=True
            )

        # Test that if more than one argument is defined, we raise.
        with self.assertRaises(ValueError):
            validate_mutually_exclusive_arguments(
                OrderedDict([("first", "value_1"), ("second", None), ("third", "value_3"), ("fourth", None)])
            )

        # Test that if more than one argument is defined, we raise.
        with self.assertRaises(ValueError):
            validate_mutually_exclusive_arguments(
                OrderedDict([("first", "value_1"), ("second", None), ("third", "value_3"), ("fourth", None)])
            )
