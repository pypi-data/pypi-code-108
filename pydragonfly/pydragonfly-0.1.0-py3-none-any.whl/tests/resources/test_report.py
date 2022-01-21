from . import APIResourceBaseTestCase, APIResource

from tests.mock_utils import generic_200_mock, generic_204_mock


class ReportResourceTestCase(APIResourceBaseTestCase):
    @property
    def resource(self) -> APIResource:
        return self.df.Report

    @generic_200_mock
    def test__timeline(self, *args, **kwargs):
        response = self.resource.timeline(object_id=self.object_id)
        self.assertEqual(200, response.code)

    @generic_200_mock
    def test__matched_rules(self, *args, **kwargs):
        response = self.resource.matched_rules(object_id=self.object_id)
        self.assertEqual(200, response.code)

    @generic_204_mock
    def test__revoke(self, *args, **kwargs):
        response = self.resource.revoke(object_id=self.object_id)
        self.assertEqual(204, response.code)
