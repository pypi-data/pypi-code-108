class ReadRecordRequest:
    """
    Class for creating read record request objects.
    Creating the request with a class helps ensure that the request body
    conforms to the requirements on the API side.
    """

    def __init__(self):
        """
         Constructor
         """
        self.readRecordRequestType = None
        self.recordCount = None
        self.recordId = None
        self.markAsRead = None
        self.recordTimeStampISO = None

    @property
    def to_json(self):
        """
         returns the class properties as a Dict
         :return: (Dict) class properties
         """
        return self.__dict__
