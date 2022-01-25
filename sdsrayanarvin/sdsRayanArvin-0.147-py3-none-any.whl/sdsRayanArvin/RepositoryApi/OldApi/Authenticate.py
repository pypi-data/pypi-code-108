from sdsRayanArvin.Dataset.UserData import UserData
from sdsRayanArvin.Repository import Repository


class Authenticate(Repository):
    def Login(self):
        res = self.Request.sendWithOutToken('POST',
                                            'user/authenticate',
                                            {
                                                'phone': '09100518330',
                                                'password': '51905190'
                                            })
        self.Request.setToken(res['token'])

    def UserInformation(self) -> UserData:
        """
        get user information
        :return: :class:`User <User>` object
        """

        res = self.Request.sendWithToken('GET', 'authenticated_user')
        return UserData(res['user'])
