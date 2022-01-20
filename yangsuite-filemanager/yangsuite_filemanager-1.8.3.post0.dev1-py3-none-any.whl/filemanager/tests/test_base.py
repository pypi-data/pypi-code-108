import unittest2 as unittest
import os
import tempfile
import shutil

from yangsuite.paths import set_base_path
from ..base import _YSYangSetBase
from ..utility import list_yang_files


class TestYSYangSetBase(unittest.TestCase):
    """Tests for the _YSYangSetBase semi-abstract class."""

    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'tests', 'data')
    test_dir = os.path.join(base_dir,
                            'users', 'test', 'repositories', 'testrepo')

    cls = _YSYangSetBase

    def setUp(self):
        """Pre-test setup function, called automatically."""
        set_base_path(self.base_dir)
        self.test_yang_files = list_yang_files(self.test_dir)
        self.temp_path = tempfile.mkdtemp()

    def tearDown(self):
        """Post-test cleanup function, called automatically."""
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path)

    def test_equality(self):
        """Test equality checks."""
        ys1 = self.cls("test", [])
        ys2 = self.cls("test", [])
        ys3 = self.cls("test", ["module"])
        ys4 = self.cls("nobody", [])

        self.assertTrue(ys1 == ys2)
        self.assertFalse(ys1 == ys3)
        self.assertFalse(ys1 == ys4)

        # Check inverse as well for python 2's sake.
        self.assertFalse(ys1 != ys2)
        self.assertTrue(ys1 != ys3)
        self.assertTrue(ys1 != ys4)
