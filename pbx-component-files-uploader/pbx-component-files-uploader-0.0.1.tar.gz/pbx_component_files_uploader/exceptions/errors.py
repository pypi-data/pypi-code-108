class Error(Exception):
    pass


class NotAllowed(Error):

    def __init__(self, message):
        self.message = message


class UploadError(Error):

    def __init__(self, code, message):
        self.code = code
        self.message = message


class EmptyAuthField(Error):

    def __init__(self, field):
        self.message = f'Auth field [{field}] is empty'


class EmptyConfigField(Error):

    def __init__(self, field):
        self.message = f'Config field [{field}] is empty'
