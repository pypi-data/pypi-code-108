class UserData:
    def __init__(self, userData):
        self.__name = userData['name']
        self.__family = userData['family']
        self.__username = userData['username']
        self.__phone = userData['phone']
        self.__type = userData['type']
        self.__org = userData['org']

    def getName(self):
        return self.__name

    def getFamily(self):
        return self.__family

    def getUsername(self):
        return self.__username

    def getPhone(self):
        return self.__phone

    def getType(self):
        return self.__type

    def getIdOrg(self):
        return self.__org

