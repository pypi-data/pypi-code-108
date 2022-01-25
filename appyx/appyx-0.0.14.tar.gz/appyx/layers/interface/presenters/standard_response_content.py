from appyx.layers.interface.presenters.base.presenter import Presenter


class StandardResponseContentPresenter(Presenter):

    def __init__(self, an_object, errors) -> None:
        super().__init__()
        self._an_object = an_object
        self._errors = errors

    def present(self):
        return {
            "object": self._an_object,
            "errors": self._errors
        }
