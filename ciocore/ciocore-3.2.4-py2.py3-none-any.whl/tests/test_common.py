""" test data

   isort:skip_file
"""
import os
import unittest

FILES_PATH = os.path.join(os.path.dirname(__file__), "files")


class TestMd5(unittest.TestCase):
 
    def test_get_base64_md5_is_correct_md5(self):
        from ciocore import common
        fn1 = os.path.join(FILES_PATH, "one")
        md5=common.get_base64_md5(fn1)
        self.assertEqual(md5, "9iVbsBxkj+lncU1SqJ6OnA==")

    def test_get_base64_md5_is_correct_type(self):
        from ciocore import common
        from builtins import str
        fn1 = os.path.join(FILES_PATH, "one")
        md5=common.get_base64_md5(fn1)
        self.assertIsInstance(md5, str)
