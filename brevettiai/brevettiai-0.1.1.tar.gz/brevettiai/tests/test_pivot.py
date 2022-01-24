import json
import unittest

import numpy as np
import pandas as pd

from brevettiai.interfaces.pivot import pivot_fields, pivot_data


class TestPivotIntegration(unittest.TestCase):
    samples = pd.DataFrame({
        "cat": [("A", "B"), ("A",), "B", ("A", "B", "C"), "D", ("A", "B"), pd.NA],
        "idx": np.arange(7)
    })

    def test_fields(self):
        fields = {a: a.upper() for a in "abcdefgh"}

        pfields = pivot_fields(fields)
        self.assertTrue(all(x["key"] in fields and x["label"] == fields[x["key"]] for x in pfields["fields"]))
        self.assertEqual(pfields["colFields"], [])
        self.assertEqual(pfields["rowFields"], [])

        pfields = pivot_fields(fields, rows=["a", "b", "c"], cols=["c", "d", "e"])

        f_ = {a: a.upper() for a in "fgh"}
        self.assertTrue(all(x["key"] in f_ and x["label"] == f_[x["key"]] for x in pfields["fields"]))

        self.assertEqual(json.dumps(pfields["colFields"], sort_keys=True),
                         json.dumps([{"key": a, "label": a.upper()} for a in "de"], sort_keys=True))

        self.assertEqual(json.dumps(pfields["rowFields"], sort_keys=True),
                         json.dumps([{"key": a, "label": a.upper()} for a in "abc"], sort_keys=True))

    def test_data(self):
        df = pivot_data(self.samples, ["cat"])

        self.assertEqual(df.drop_duplicates("id")["count"].sum(),
                         self.samples.shape[0],
                         "Duplicates excluded by dropping duplicate id after grouping")


if __name__ == '__main__':
    unittest.main()
