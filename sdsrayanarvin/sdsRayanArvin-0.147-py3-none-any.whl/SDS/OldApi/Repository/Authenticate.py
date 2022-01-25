from sdsRayanArvin.Dataset.UserData import UserData
from sdsRayanArvin.Request import Request


class Authenticate:
    def __init__(self, requestClass: Request):
        self.Request = requestClass

    def Login(self):
        res = self.Request.sendWithOutToken('POST',
                                            'user/authenticate',
                                            {
                                                'phone': '09368915190',
                                                'password': 'Vahid5190'
                                            })
        self.Request.setToken(res['token'])

    def UserInformation(self) -> UserData:
        """
        get user information
        :return: :class:`User <User>` object
        """

        res = self.Request.sendWithToken('GET', 'authenticated_user')
        return UserData(res['user'])
