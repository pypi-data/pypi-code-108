
class Error(Exception):
    """Base Error"""
    def __init__(self, message):
        super(Error, self).__init__(message)
        self.message = message


class DataError(Error):
    """Error raised when failing to manipulate data.
    """


class InferenceError(Error):
    """Error raised when model inference fails.
    """


class ModelError(Error):
    """Used when the there is an exception associated with the model object"""
    pass


class ExplainerError(Error):
    """Used when the there is an exception associated with the explainer subsystem"""
    pass
