
class AnovaCookerException(Exception):
    pass


class AnovaCookerUpdateFailedException(AnovaCookerException):
    pass


class AnovaCookerOfflineException(AnovaCookerUpdateFailedException):
    pass


class AnovaCookerInvalidIdOrSecretException(AnovaCookerUpdateFailedException):
    pass
