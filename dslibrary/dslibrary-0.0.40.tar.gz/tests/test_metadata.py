import unittest
import json

from dslibrary.metadata import Metadata


class TestMetadata(unittest.TestCase):
    def test_json_round_trip(self):
        m = {
            "uri": "u",
            "entry_points": {
                "e1": {
                    "parameters": {"x": {"type": "float", "default": 2}},
                    "command": "python abc.py",
                    "inputs": {"i1": {"columns": [{"name": "a", "type": "integer"}]}},
                    "outputs": {"o1": {"columns": [{"name": "b", "type": "string"}]}}
                }
            }
        }
        j1 = Metadata.from_json(m).to_json()
        j2 = Metadata.from_json(j1).to_json()
        assert j1 == j2
