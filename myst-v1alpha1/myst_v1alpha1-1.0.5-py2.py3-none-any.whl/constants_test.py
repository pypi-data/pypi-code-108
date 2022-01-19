import unittest

from myst_v1alpha1.constants import DEFAULT_API_HOST
from myst_v1alpha1.constants import DEFAULT_API_VERSION
from myst_v1alpha1.constants import MYST_APPLICATION_CREDENTIALS_ENVIRONMENT_VARIABLE
from myst_v1alpha1.constants import MYST_CACHE_DIRNAME
from myst_v1alpha1.constants import MYST_USER_CREDENTIALS_FILENAME
from myst_v1alpha1.constants import USER_AGENT_PREFORMAT


class GlobalsTest(unittest.TestCase):
    def test_constants(self):
        # Test global constants to guard against accidental changes.
        self.assertEqual(DEFAULT_API_HOST, "https://api.myst.ai")
        self.assertEqual(DEFAULT_API_VERSION, "v1alpha1")
        self.assertEqual(USER_AGENT_PREFORMAT, "Myst/{api_version} PythonBindings/{package_version}")
        self.assertEqual(MYST_APPLICATION_CREDENTIALS_ENVIRONMENT_VARIABLE, "MYST_APPLICATION_CREDENTIALS")
        self.assertEqual(MYST_USER_CREDENTIALS_FILENAME, "myst_user_credentials.json")
        self.assertEqual(MYST_CACHE_DIRNAME, "myst")
