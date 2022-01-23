import mosaik_api

from mosaik_schedule_flocker.schedule_flocker.mosaik.source.\
    flocker_source_model import FlockerSourceModel
from mosaik_schedule_flocker.schedule_flocker.mosaik.source.\
    flocker_source_meta import FLOCKER_SOURCE_META


class FlockerSourceSimulator(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(FLOCKER_SOURCE_META)

        self._models = []

        self.models_target_schedule = None
        self.models_flexibility_schedules = None

    def init(self, sid, eid_prefix=None):
        if eid_prefix is not None:
            raise NotImplementedError

        return self.meta

    def create(self, num, model, **model_params):
        if num != 1:
            raise NotImplementedError()

        if self._models:
            raise NotImplementedError

        eid = FlockerSourceSimulator.__name__ + '-0'
        self._models.append(FlockerSourceModel(eid=eid))

        return [{'eid': eid, 'type': model}]

    def step(self, time, inputs):
        # The mock source models generate data on their own.
        # So do not step them at all.
        # TODO step them anyway for consistency's sake

        return time + 1

    def get_data(self, outputs):
        for model in self._models:
            assert model.eid in outputs.keys()

        outputs = {model.eid: model.get_data() for model in self._models}

        return outputs
