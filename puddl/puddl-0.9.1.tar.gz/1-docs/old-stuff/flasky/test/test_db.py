import unittest

import puddl.config
from puddl import Datum
from test import PuddlTest


class TestDB(PuddlTest):
    def test_stream(self):
        db = puddl.get_db()
        db.stream_simple("obs@f", {"test": True})

    def test_stream_datum(self):
        db = puddl.get_db()
        datum = Datum(path=self.mkv)
        db.stream_datum("obs@f", datum)


if __name__ == "__main__":
    unittest.main()
