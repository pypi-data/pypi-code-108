import os
import shutil
import tempfile
import unittest
from collections import OrderedDict

import mock

from myst_v1alpha1.utils.core_utils import format_repr
from myst_v1alpha1.utils.core_utils import get_package_version
from myst_v1alpha1.utils.core_utils import get_pkg_resource_path
from myst_v1alpha1.utils.core_utils import get_user_agent
from myst_v1alpha1.utils.core_utils import make_directory


class CoreUtilsTest(unittest.TestCase):
    @mock.patch("myst_v1alpha1.utils.core_utils.pkg_resources.get_distribution")
    def test_get_package_version(self, get_distribution_mock):
        distribution_mock = mock.Mock()
        distribution_mock.version = "0.0.0"

        get_distribution_mock.return_value = distribution_mock
        # Note that you'll need to bump this version before you release a new version of this package!
        self.assertEqual(get_package_version(), "0.0.0")

    @mock.patch("myst_v1alpha1.utils.core_utils.get_package_version")
    def test_get_user_agent(self, get_package_version_patch):
        # Test with different package and api versions to make sure we are constructing the `User-Agent` string
        # properly.
        for myst_api_version, myst_package_version, expected_user_agent_string in [
            ("v1alpha1", "0.1.2", "Myst/v1alpha1 PythonBindings/0.1.2"),
            ("v1", "0.2.0", "Myst/v1 PythonBindings/0.2.0"),
        ]:
            get_package_version_patch.return_value = myst_package_version
            with mock.patch("myst_v1alpha1.api_version", myst_api_version):
                self.assertEqual(get_user_agent(), expected_user_agent_string)

    def test_get_pkg_resource_path(self):
        # We're using these tests to not only test that `get_pkg_resource_path` works but also to make sure that the
        # expected package resources exist. Any time a package resource is added, add a corresponding test here to
        # test that we can locate it.
        self.assertTrue(os.path.exists(get_pkg_resource_path()))
        self.assertTrue(os.path.exists(get_pkg_resource_path("google_oauth_client_not_so_secret.json")))

    def test_make_directory(self):
        # Test that we can make directory.
        temp_dir = tempfile.mktemp()
        make_directory(temp_dir)

        self.assertTrue(os.path.exists(temp_dir))
        self.assertTrue(os.path.isdir(temp_dir))

        # Clean up.
        shutil.rmtree(temp_dir)

        # Test that we can make nested directories.
        temp_nested_dir = tempfile.mktemp(dir="/tmp/nested")
        make_directory(temp_nested_dir)

        self.assertTrue(os.path.exists(temp_nested_dir))
        self.assertTrue(os.path.isdir(temp_nested_dir))

        # Clean up.
        shutil.rmtree(temp_nested_dir)

    def test_format_repr(self):
        self.assertEqual(format_repr(class_name="class_name"), "<class_name>")
        self.assertEqual(
            format_repr(
                class_name="class_name",
                class_properties=OrderedDict([("property_1", "value_1"), ("property_2", "value_2")]),
            ),
            "<class_name: property_1=value_1, property_2=value_2>",
        )
