'''
EXCEPTIONS
'''


class TrovoApiException(Exception):
    '''
    API Related Errors
    '''
    @property
    def status(self):
        return self.args[0]["status"]

    @property
    def error(self):
        return self.args[0]["error"]

    @property
    def message(self):
        return self.args[0]["message"]


class MissingArgumentsException(Exception):
    '''
    Library Related Error: Arguments missing
    '''
    pass
