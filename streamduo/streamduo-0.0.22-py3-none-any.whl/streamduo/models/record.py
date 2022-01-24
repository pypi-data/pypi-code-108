class Record:
    """
    Class used to aid in the construction of record objects
    Help ensure accuracy of object when sent to API
    """

    def __init__(self):
        self.recordId = None
        self.streamId = None
        self.recordTimeStampISO = None
        self.readStatus = None
        self.dataPayload = None

    def to_json(self):
        return self.__dict__
    