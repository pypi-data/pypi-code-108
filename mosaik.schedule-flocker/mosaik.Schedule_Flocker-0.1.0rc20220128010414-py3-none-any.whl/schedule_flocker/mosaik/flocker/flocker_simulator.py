from mosaik_api import Simulator

from mosaik_schedule_flocker.schedule_flocker.mosaik.flocker.flocker_meta \
    import FLOCKER_META
from mosaik_schedule_flocker.schedule_flocker.mosaik.flocker.flocker_model \
    import FlockerModel
from mosaik_schedule_flocker.schedule_flocker.mosaik.source.\
    flocker_source_simulator import FlockerSourceSimulator


class FlockerSimulator(Simulator):
    def __init__(self):
        super().__init__(FLOCKER_META)

        self._models = []

    def create(self, num, model, **model_params):
        if num != 1:
            raise  # TODO

        if model != FlockerModel.__name__:
            raise  # TODO

        if len(model_params) != 0:
            print('Flocker model params:', model_params)
            raise  # TODO

        if len(self._models) != 0:
            raise  # TODO

        eid = FlockerModel.__name__ + '-0'
        self._models.append(FlockerModel(eid=eid))

        return [{'eid': eid, 'type': model}]

    def step(self, time, inputs):
        source_name = \
            FlockerSourceSimulator.__name__ + '-0' + \
            '.' + \
            FlockerSourceSimulator.__name__ + '-0'
        for model in self._models:
            inputs = inputs[model.eid]['config'][source_name]
            model.step(inputs=inputs)

        return time + 1

    def get_data(self, outputs):
        for model in self._models:
            assert model.eid in outputs.keys()

        outputs = {model.eid: model.get_data() for model in self._models}

        return outputs
