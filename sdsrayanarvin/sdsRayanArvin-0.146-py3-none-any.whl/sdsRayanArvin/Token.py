class Token:
    def __init__(self):
        self.__token = None

    def setToken(self, token):
        self.__token = token

    def getToken(self):
        return self.__token

    def hasToken(self):
        return self.__token is not None
