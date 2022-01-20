
import textwrap


def normalize(text):
    return textwrap.dedent(text).strip()


class BaseException(Exception):

    def __init__(self, message=None):

        super(BaseException, self).__init__(normalize(message or ''))


#
# UTILS
#
class BrokenYamlError(BaseException):
    pass


class MissingSubstitutionKeyError(BaseException):
    pass


#
# VALIDATORS
#
class ValidatorError(BaseException):
    pass


#
# CRYPTO
#
class DecryptionError(BaseException):
    pass


class EncryptionKeyFileMissingError(BaseException):
    pass


class EncryptionKeyTooShortError(BaseException):
    pass


class EncryptionKeyBrokenBase64Error(BaseException):
    pass


class EncryptionKeyBrokenJsonError(BaseException):
    pass


#
# GIT
#
class FileNotIgnoredError(BaseException):
    pass
