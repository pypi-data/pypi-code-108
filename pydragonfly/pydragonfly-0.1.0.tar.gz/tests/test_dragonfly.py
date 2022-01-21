from unittest.mock import patch

from pydragonfly.sdk.const import ANALYZED, MALICIOUS
from tests.mock_utils import MockAPIResponse
from tests.resources import APIResourceBaseTestCase
from tests.resources.test_analysis import AnalysisResultTestCase


class DragonflyTestCase(APIResourceBaseTestCase):
    @property
    def resource(self):
        return self.df

    @patch(
        "pydragonfly.sdk.resources.analysis.Analysis.create",
        return_value=MockAPIResponse({"id": 1}, 200),
    )
    def test_analyze_file(self, *args, **kwargs):
        ret = self.df.analyze_file(
            sample_name="test", sample_buffer=b"test_sample", retrieve_analysis=False
        )
        self.assertEqual(ret, 1)

    @patch(
        "pydragonfly.sdk.resources.analysis.Analysis.retrieve",
        return_value=MockAPIResponse(AnalysisResultTestCase.result_json, 200),
    )
    @patch(
        "pydragonfly.sdk.resources.report.Report.matched_rules",
        return_value=MockAPIResponse(AnalysisResultTestCase.matched_rules_json, 200),
    )
    def test_analysis_result(self, *args, **kwargs):
        result = self.df.analysis_result(12)
        self.assertEqual(result.id, 12)
        self.assertEqual(result.status, ANALYZED)
        self.assertEqual(result.evaluation, MALICIOUS)
        self.assertEqual(result.score, 10)
