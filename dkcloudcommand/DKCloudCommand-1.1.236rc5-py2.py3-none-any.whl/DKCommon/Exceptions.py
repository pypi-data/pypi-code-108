class KitchenPreviewOutdatedException(Exception):
    def __init__(self, message):
        super(KitchenPreviewOutdatedException, self).__init__(message)


class ValidationException(Exception):
    pass
