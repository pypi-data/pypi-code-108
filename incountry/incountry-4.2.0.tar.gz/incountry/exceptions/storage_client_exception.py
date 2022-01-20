from .storage_exception import StorageException


class StorageClientException(StorageException):
    def __init__(self, message, original_exception=None):
        super(StorageException, self).__init__(message)

        self.original_exception = original_exception


class StorageConfigValidationException(StorageClientException):
    pass


class SecretsProviderException(StorageClientException):
    pass


class SecretsValidationException(StorageClientException):
    pass


class InputValidationException(StorageClientException):
    pass
