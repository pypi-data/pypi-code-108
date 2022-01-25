import unittest
from pathlib import Path


class PuddlTest(unittest.TestCase):
    DATADIR = Path(__file__).parent / "data"

    def setUp(self) -> None:
        self.data1 = self.DATADIR / "data1.json"
        self.data2 = self.DATADIR / "data2"
        self.mkv = self.DATADIR / "2019-11-01_18-26-42.mkv"
