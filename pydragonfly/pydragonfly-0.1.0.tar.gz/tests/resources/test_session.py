from . import APIResourceBaseTestCase, APIResource


class SessionResourceTestCase(APIResourceBaseTestCase):
    @property
    def resource(self) -> APIResource:
        return self.df.Session
