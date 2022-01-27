""" test validator

   isort:skip_file
"""

import unittest
from ciocore.validator import Validator

class ValidateAddsError(Validator):
    def run(self, layername):
        self.add_error("There was an error.")

class ValidateAddsWarning(Validator):
    def run(self, layername):
        self.add_warning("There was a warning.")

class ValidateAddsNotice(Validator):
    def run(self, layername):
        self.add_notice("There was a notice.")

class ValidateAddsAll(Validator):
    def run(self, layername):
        self.add_error("There was an error.")
        self.add_warning("There was a warning.")
        self.add_notice("There was a notice.")
        self.add_error("There was another error.")
        self.add_warning("There was another warning.")

class ValidatorTest(unittest.TestCase):

    def test_validator_has_plugins(self):
        self.assertEqual(len(Validator.plugins()), 4)

    def test_validator_splits_title(self):
        self.assertEqual( ValidateAddsError.title(), "Validate Adds Error")

    def test_validator_adds_an_error(self):
        v = ValidateAddsError({})
        v.run("")
        self.assertIn( "There was an error",  list(v.errors)[0])

    def test_validator_adds_all(self):
        v = ValidateAddsAll({})
        v.run("")
        self.assertEqual(  len(list(v.errors|v.warnings|v.notices)), 5)

    def test_ValidateAddsError_is_plugin(self):
        self.assertIn("ValidateAddsError",  (p.__name__ for p in Validator.plugins()) )

if __name__ == "__main__":
    unittest.main()
