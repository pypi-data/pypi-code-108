from mosaik_api import Simulator

from mosaik_scenario_tools.scenario_tools.source.source_model import \
    SourceModel
from mosaik_scenario_tools.scenario_tools.source.source_simulator_meta import \
    SOURCE_META


class SourceSimulator(Simulator):
    def __init__(self):
        super().__init__(meta=SOURCE_META)

        self._models = []

    def create(self, num, model, **model_params):
        if num != 1:
            raise NotImplementedError()

        if model != SourceModel.__name__:
            raise NotImplementedError()

        if len(model_params) != 0:
            print('model_params:', model_params)
            raise NotImplementedError()

        if len(self._models) != 0:
            raise NotImplementedError()

        eid = SourceModel.__name__ + '-0'
        self._models.append(SourceModel(eid=eid))

        return [{'eid': eid, 'type': model}]

    def get_data(self, outputs):
        for model in self._models:
            assert model.eid in outputs.keys()

        outputs = {model.eid: model.get_data() for model in self._models}

        return outputs

    def step(self, time, inputs):
        # Request being scheduled for every time step
        return time + 1
