from mosaik_api import Simulator

from mosaik_scenario_tools.scenario_tools.simulator.manage_inputs.\
    manage_inputs_module import \
    manage_inputs


class InputManagingSimulator(Simulator):
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
    @manage_inputs
    def step(self, time, inputs):
        pass
