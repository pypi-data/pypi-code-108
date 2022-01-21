from . import APIResourceBaseTestCase, APIResource

from tests.mock_utils import generic_200_mock, generic_201_mock


class ProfileResourceTestCase(APIResourceBaseTestCase):
    @property
    def resource(self) -> APIResource:
        return self.df.Profile

    @generic_201_mock
    def test__create(self, *args, **kwargs):
        response = self.resource.create(
            data=self.resource.CreateProfileRequestBody(
                filename="testprofile.ql", emulator="qiling", content=b"test"
            ),
        )
        self.assertEqual(201, response.code)

    @generic_200_mock
    def test__update(self, *args, **kwargs):
        response = self.resource.update(
            object_id=self.object_id,
            data=self.resource.UpdateProfileRequestBody(enabled=False),
        )
        self.assertEqual(200, response.code)
