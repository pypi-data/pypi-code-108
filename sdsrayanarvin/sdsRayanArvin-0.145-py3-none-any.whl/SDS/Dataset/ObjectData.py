class ObjectData:
    def __init__(self, objectData):
        self.__ID_object = objectData['ID_object']
        self.__title = objectData['title']
        self.__mode = objectData['mode']
        self.__type = objectData['type']

        if 'data' in objectData:
            if len(objectData['data']) > 0:
                self.__data = objectData['data']

        if 'Reader' in objectData:
            if len(objectData['Reader']) > 0:
                self.__reader = objectData['Reader'][0]

        if 'Process' in objectData:
            if len(objectData['Process']) > 0:
                self.__process = objectData['Process']

    def getIdObject(self):
        return self.__ID_object

    def getTitle(self):
        return self.__title

    def getMode(self):
        return self.__mode

    def getType(self):
        return self.__type

    def getData(self):
        return self.__data

    def getReader(self):
        return self.__reader

    def getProcess(self):
        return self.__process
