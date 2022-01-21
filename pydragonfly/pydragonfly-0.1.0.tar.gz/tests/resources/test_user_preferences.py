from . import APIResourceBaseTestCase, APIResource

from tests.mock_utils import generic_200_mock


class UserPreferencesResourceTestCase(APIResourceBaseTestCase):
    @property
    def resource(self) -> APIResource:
        return self.df.UserPreferences

    @generic_200_mock
    def test__update(self, *args, **kwargs):
        response = self.resource.update(
            object_id=self.object_id,
            data=self.resource.UpdateUserPreferencesRequestBody(
                apistructure_ignore_list=["x", "y", "z"]
            ),
        )
        self.assertEqual(200, response.code)
