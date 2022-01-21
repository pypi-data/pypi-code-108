from . import APIResourceBaseTestCase, APIResource

from tests.mock_utils import generic_200_mock


class SampleResourceTestCase(APIResourceBaseTestCase):
    @property
    def resource(self) -> APIResource:
        return self.df.Sample

    @generic_200_mock
    def test__download(self, *args, **kwargs):
        response = self.resource.download(object_id=self.object_id)
        self.assertEqual(200, response.code)
