from typing import Any


def buffer_inputs(function):
    def wrapper(self, time, inputs):
        try:
            inputs_old = self.__last_inputs
        except AttributeError:
            self.__last_inputs = {}
            inputs_old = self.__last_inputs

        inputs_new = inputs_old
        inputs_new.update(inputs)
        setattr(self, '__inputs', inputs_new)

        value: Any = function(self=self, time=time, inputs=inputs_new)

        return value

    return wrapper
