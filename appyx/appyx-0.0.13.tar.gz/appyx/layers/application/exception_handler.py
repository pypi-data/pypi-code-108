from appyx.layers.domain.errors import BaseErrorFactory


class ExceptionHandler:
    """
    Models the policy on how to handle exceptions.
    """
    def handle(self, an_exception, result):
        raise NotImplementedError('Subclass responsibility')


class AddExceptionToResult(ExceptionHandler):
    """
    Models the policy of packaging an exception as an error within a result.
    """
    def handle(self, an_exception, result):
        result_error = BaseErrorFactory().unexpected_error(an_exception)
        result.add_error(result_error)
        return result


class NullExceptionHandler(ExceptionHandler):
    """
    Models the policy of not handling exceptions. Effectively letting them run through.
    """
    def handle(self, an_exception, result):
        raise an_exception
