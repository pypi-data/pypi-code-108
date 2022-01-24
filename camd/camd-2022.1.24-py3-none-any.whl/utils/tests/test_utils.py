import unittest
import datetime

from camd.utils import get_new_version


class UtilsTest(unittest.TestCase):
    def test_get_new_version(self):
        today = datetime.datetime.today().strftime("%Y.%-m.%-d")
        # New version is new date
        new_version = get_new_version(current_ver="2020.1.1")
        self.assertEqual(new_version, today)

        # New version is first "post version"
        new_version = get_new_version(current_ver=today)
        self.assertEqual(new_version, "{}-post0".format(today))

        # New version is incrementing "post version"
        new_version = get_new_version(current_ver="{}-post3".format(today))
        self.assertEqual(new_version, "{}-post4".format(today))

        # New version increments multiple digits for "post version"
        new_version = get_new_version(current_ver="{}-post10".format(today))
        self.assertEqual(new_version, "{}-post11".format(today))


if __name__ == '__main__':
    unittest.main()
