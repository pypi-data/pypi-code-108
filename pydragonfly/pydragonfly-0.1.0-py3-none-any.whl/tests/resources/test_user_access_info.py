from . import APIResourceBaseTestCase, APIResource


class UserAccessInfoResourceTestCase(APIResourceBaseTestCase):
    @property
    def resource(self) -> APIResource:
        return self.df.UserAccessInfo
