from appyx.layers.application.exception_handler import AddExceptionToResult
from appyx.layers.domain.business import Business


class Application:
    """
    Models an application.
    Given a running environment it creates the resources that will be used by the business.
    It also defines and set up the interfaces with which external actors will interact with the business.

    An application also defines how to handle the exceptions those might rise for the resources the business uses.
    """

    def __init__(self, running_context=None, exception_handler=None) -> None:
        super().__init__()
        self._business = None
        self._general_exception_handler = exception_handler or self._default_exception_handler()
        if running_context is None:
            running_context = self.default_running_context()
        self._running_context = running_context

    def general_exception_handler(self):
        return self._general_exception_handler

    def set_general_exception_handler(self, exception_handler):
        self._general_exception_handler = exception_handler

    def _default_exception_handler(self):
        return AddExceptionToResult()

    def current_business(self):
        if self._business is None:
            self._business = self._new_business()
        return self._business

    def _new_business(self):
        return Business()

    def default_running_context(self):
        raise NotImplementedError('Subclass responsibility')
