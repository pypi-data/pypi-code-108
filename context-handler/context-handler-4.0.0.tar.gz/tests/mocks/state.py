import typing


class State:
    _state: typing.Dict[str, typing.Any]

    def __init__(self) -> None:
        super().__setattr__("_state", {})

    def __setattr__(self, name: str, value: typing.Any) -> None:
        self._state[name] = value

    def __getattr__(self, name: str) -> typing.Any:
        try:
            result = self._state[name]
        except KeyError:
            message = "'{}' object has no attribute '{}'"
            raise AttributeError(message.format(self.__class__.__name__, name))
        else:
            return result

    def __delattr__(self, name: str) -> None:
        del self._state[name]
