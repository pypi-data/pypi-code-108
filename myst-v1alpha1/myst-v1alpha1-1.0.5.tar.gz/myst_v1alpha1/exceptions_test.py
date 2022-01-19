import unittest

from myst_v1alpha1.exceptions import MystAPIError
from myst_v1alpha1.exceptions import UnAuthenticatedError


class ErrorsTest(unittest.TestCase):
    def test_un_authenticated_error(self):
        error = UnAuthenticatedError("UnAuthenticated.")

        def _raise_error():
            raise error

        self.assertRaises(UnAuthenticatedError, _raise_error)
        self.assertEqual(error.message, "UnAuthenticated.")

    def test_myst_api_error(self):
        error = MystAPIError(http_status_code=404, code=404, message="Not found.")

        def _raise_error():
            raise error

        self.assertRaises(MystAPIError, _raise_error)
        self.assertEqual(error.http_status_code, 404)
        self.assertEqual(error.code, 404)
        self.assertEqual(error.message, "Not found.")
        self.assertEqual(str(error), "Not found.")
