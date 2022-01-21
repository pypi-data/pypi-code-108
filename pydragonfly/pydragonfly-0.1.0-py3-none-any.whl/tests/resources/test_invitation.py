from . import APIResourceBaseTestCase, APIResource

from tests.mock_utils import generic_204_mock


class InvitationResourceTestCase(APIResourceBaseTestCase):
    @property
    def resource(self) -> APIResource:
        return self.df.Invitation

    @generic_204_mock
    def test__accept(self, *args, **kwargs):
        response = self.resource.accept(object_id=self.object_id)
        self.assertEqual(204, response.code)

    @generic_204_mock
    def test__decline(self, *args, **kwargs):
        response = self.resource.decline(object_id=self.object_id)
        self.assertEqual(204, response.code)
