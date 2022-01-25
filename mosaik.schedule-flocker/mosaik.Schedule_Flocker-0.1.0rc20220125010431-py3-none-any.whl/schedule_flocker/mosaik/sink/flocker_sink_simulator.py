import mosaik_api

from mosaik_schedule_flocker.schedule_flocker.mosaik.sink.flocker_sink_model \
    import FlockerSinkModel
from mosaik_schedule_flocker.schedule_flocker.mosaik.sink.flocker_sink_meta \
    import FLOCKER_SINK_META


class FlockerSinkSimulator(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(FLOCKER_SINK_META)

        self._models = []

    def init(self, sid, eid_prefix=None):
        if eid_prefix is not None:
            raise NotImplementedError

        return self.meta

    def create(self, num, model, **model_params):
        if num != 1:
            raise NotImplementedError()

        if self._models:
            raise NotImplementedError

        eid = FlockerSinkSimulator.__name__ + '-0'
        self._models.append(FlockerSinkModel(eid=eid))

        return [{'eid': eid, 'type': model}]

    def step(self, time, inputs):
        # Validate model inputs
        print('sink inputs type:', type(inputs))
        assert type(inputs) is dict
        print('sink inputs keys:', inputs.keys())
        assert self._models[0].eid in inputs.keys()

        # Step models with inputs
        for model in self._models:
            model.step(inputs[model.eid])

        return time + 1

    def get_data(self, outputs):
        # This simulator's models only have inputs.
        # So return no outputs here.
        return
