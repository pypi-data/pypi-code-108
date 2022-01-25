import datetime
import unittest

from puddl import Datum
from test import PuddlTest


class Test(PuddlTest):
    def test(self):
        x = Datum()
        assert x.uuid is not None
        assert x["uuid"] is not None
        assert x["load_dt"] is not None
        # make sure we can parse the "load_dt"
        datetime.datetime.fromisoformat(x["load_dt"])
        Datum(foo="bar")
        Datum({"bar": "baz"})

    def test_update(self):
        d = Datum()
        d.update({"foo": "bar"}, x=23)
        assert d["foo"] == "bar"
        assert d["x"] == 23
        # can update with None
        d.update(None)
        assert d["foo"] == "bar"
        assert d["x"] == 23

    def test_file_stuff(self):
        d = Datum(path=self.data1)
        assert d["path"] == str(self.data1)
        assert d.path == self.data1
        assert "filetype" not in d, "magic has no info about this simple text file"
        assert "stat" in d
        s = d.to_json()
        self.assertTrue(s)

    def test_ffprobe(self):
        d = Datum(path=self.mkv)
        assert d["ffprobe"]["format"]["start_time"] == "0.000000"
        assert d["ffprobe"]["format"]["duration"] == "4.934000"
        assert d["ffprobe"]["format"]["format_name"] == "matroska,webm"


if __name__ == "__main__":
    unittest.main()
