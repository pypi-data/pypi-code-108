from . import APIResourceBaseTestCase, APIResource


from tests.mock_utils import generic_201_mock, generic_204_mock


class OrganizationResourceTestCase(APIResourceBaseTestCase):
    @property
    def resource(self) -> APIResource:
        return self.df.Organization

    @generic_201_mock
    def test__create(self, *args, **kwargs):
        response = self.resource.create(
            data=self.resource.CreateOrgRequestBody(name="test__create"),
        )
        self.assertEqual(201, response.code)

    @generic_201_mock
    def test__invite(self, *args, **kwargs):
        response = self.resource.invite(
            data=self.resource.InviteRequestBody(username="test")
        )
        self.assertEqual(201, response.code)

    @generic_204_mock
    def test__remove_member(self, *args, **kwargs):
        response = self.resource.remove_member(
            data=self.resource.InviteRequestBody(username="test")
        )
        self.assertEqual(204, response.code)
