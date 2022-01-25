import unittest

import puddl.config
from test import PuddlTest


class TestConfig(PuddlTest):
    def test(self):
        puddl.config.read()
        puddl.config.to_env()


if __name__ == "__main__":
    unittest.main()
