from typing import Any


def manage_inputs(function):
    def wrapper(self, time, inputs):
        try:
            self.__inputs_future
        except AttributeError:
            self.__inputs_current = {}
            self.__inputs_future = {}
        if inputs['clock_output_dto']['ClockSimulator-0.ClockModel-0'][
             'phase'] == "INGEST":
            # if the phase INGEST is reached, we start a new iteration.
            # Therefore, inputs which refered to the future are now
            # current for the current phase. The new inputs received
            # via mosaik are now refering to the next planning horizon
            # in the future.
            self.__inputs_current = self.__inputs_future
            self.__inputs_future = {}
        self.__inputs_future.update(inputs)
        new_inputs = self.__inputs_future
        setattr(self, '__inputs', new_inputs)

        # inputs new are the ones for the next phase (planning horizon is
        # in the future. Inputs saved in '__
        value: Any = function(self=self, time=time,
                              inputs=new_inputs)

        return value

    return wrapper
