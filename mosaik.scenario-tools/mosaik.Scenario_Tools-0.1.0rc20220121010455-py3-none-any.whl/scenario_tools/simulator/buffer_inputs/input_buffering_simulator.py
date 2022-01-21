from mosaik_api import Simulator

from mosaik_scenario_tools.scenario_tools.simulator.buffer_inputs.\
    buffer_inputs_module import buffer_inputs


class InputBufferingSimulator(Simulator):
    def __init__(self, meta):
        super().__init__(meta)
        self._model = None

    def create(self, num, model, **model_params):
        assert num == 1

        self._model = model(model_params)

        return {model, self._model}

    def get_data(self, outputs):
        return outputs

    # The thing under test
    @buffer_inputs
    def step(self, time, inputs):
        pass
