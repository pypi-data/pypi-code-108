import unittest
from unittest import mock

from puddl import source
from test import PuddlTest


class Test(PuddlTest):
    def test_from_hostname(self):
        with mock.patch("socket.gethostname", lambda: "foohost"):
            assert source.from_hostname("obs") == "obs@foohost"


if __name__ == "__main__":
    unittest.main()
