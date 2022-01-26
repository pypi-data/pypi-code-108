class ParseException(Exception):
    def __init__(self, message, token):
        super(ParseException, self).__init__(message)
        self.token = token
