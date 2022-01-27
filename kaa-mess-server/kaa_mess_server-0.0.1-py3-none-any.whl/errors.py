'''
This module contains classes of processing frequently raises errors
'''

class ServerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'Required field "{self.missing_field}" is absent in the received message.'


class IncorrectDataReceivedError(Exception):
    def __str__(self):
        return 'The incorrect message obtained from the server.'

