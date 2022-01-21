from . import APIResourceBaseTestCase, APIResource


class ActionResourceTestCase(APIResourceBaseTestCase):
    @property
    def resource(self) -> APIResource:
        return self.df.Action
