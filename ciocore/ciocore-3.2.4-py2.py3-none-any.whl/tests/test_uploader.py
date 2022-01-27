import unittest
import sys

try:
    from unittest import mock
except ImportError:
    import mock

PY3 = sys.version_info >= (3, 0)
BUILTIN_OPEN = "builtins.open" if PY3 else "__builtin__.open"

from ciocore import config
from ciocore import uploader

class UploaderResolveArgsTest(unittest.TestCase):
    def up(self, **overrides):
        self.cfg = config.config(force=True)
        self.args = {
            "md5_caching": None,
            "database_filepath": None,
            "location": None,
            "thread_count": None
        }
        self.args.update(overrides)

    # md5_caching
    def test_md5_caching_from_config_when_none(self):
        self.up()
        args = uploader.resolve_args(self.args)
        self.assertTrue(args["md5_caching"])

    def test_md5_caching_ignore_config_when_value(self):
        self.up(md5_caching=False)
        args = uploader.resolve_args(self.args)
        self.assertFalse(args["md5_caching"])

    def test_get_md5_caching_from_config_when_not_set(self):
        self.args = {}
        args = uploader.resolve_args(self.args)
        self.assertTrue(args["md5_caching"])

    # database_filepath
    def test_database_filepath_set_to_none_when_not_set(self):
        self.args = {}
        args = uploader.resolve_args(self.args)
        self.assertEqual(args["database_filepath"], None)

    def test_database_filepath_leave_at_value_when_set(self):
        self.args = {"database_filepath": "foo",}
        args = uploader.resolve_args(self.args)
        self.assertEqual(args["database_filepath"], "foo")

    # location
    def test_location_set_to_none_when_not_set(self):
        self.args = {}
        args = uploader.resolve_args(self.args)
        self.assertEqual(args["location"], None)

    def test_location_leave_at_value_when_set(self):
        self.args = {"location": "foo",}
        args = uploader.resolve_args(self.args)
        self.assertEqual(args["location"], "foo")

    # thread_count
    # Mock the config object in order to reliably set the thread count 
    def test_thread_count_from_config_when_none(self):
        self.up()
        with mock.patch.object(self.cfg , 'config',  {"thread_count":12, "md5_caching":True}):
            args = uploader.resolve_args(self.args)
            self.assertEqual(args["thread_count"], 12)

    def test_thread_count_ignore_config_when_value(self):
        self.up(thread_count=2)
        with mock.patch.object(self.cfg , 'config',  {"thread_count":12, "md5_caching":True}):
            args = uploader.resolve_args(self.args)
            self.assertEqual(args["thread_count"], 2)

    def test_thread_count_from_config_when_not_set(self):
        self.up()
        self.args = {}
        with mock.patch.object(self.cfg , 'config',  {"thread_count":12, "md5_caching":True}):
            args = uploader.resolve_args(self.args)
            self.assertEqual(args["thread_count"], 12)
 
