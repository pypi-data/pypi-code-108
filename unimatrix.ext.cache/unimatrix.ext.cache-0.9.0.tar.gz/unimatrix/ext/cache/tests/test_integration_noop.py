# pylint: skip-file
"""This test module exists so that at least one test is collected during
the integration test stage (the command errors when there are no tests that
match the include pattern).
"""
import unittest


class NoopIntegrationTestCase(unittest.TestCase):

    def test_noop(self):
        pass


if __name__ == '__main__':
    unittest.main()
