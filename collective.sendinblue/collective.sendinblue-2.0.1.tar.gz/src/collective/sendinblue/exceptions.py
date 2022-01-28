# -*- coding: utf-8 -*-


class BadResponseError(Exception):
    """
    Raised if Sendinblue responds with incomplete response (keys missing
    from dict) or something we did not expect.
    """

    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        return 'Sendinblue response %s is not complete' % self.obj


class SendinblueException(Exception):
    """
    If Sendinblue returns an exception code as part of their response,
    this exception will be raised. Contains the unmodified ``code`` and
    ``message`` (unicode) attributes returned by Sendinblue.
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return 'Sendinblue {0}: "{1}"'.format(self.code, self.message)
