from typing import List

from mosaik_api import Simulator

from mosaik_scenario_tools.scenario_tools.compressed_data_flow.\
    inflate_module import inflate_data
from mosaik_scenario_tools.scenario_tools.compressed_data_flow.\
    inflate_simulator_meta import INFLATE_META
from mosaik_scenario_tools.scenario_tools.compressed_data_flow.\
    inflate_sink_model import InflateSinkModel


class InflateSimulator(Simulator):

    def __init__(self):
        super().__init__(meta=INFLATE_META)

        self._data: dict = {}

        eid = InflateSinkModel.__name__ + '-0'
        self._model: InflateSinkModel = InflateSinkModel(eid=eid)

    def create(
        self, num=1, model=InflateSinkModel.__name__, **model_params
    ) -> List:
        if num != 1:
            raise NotImplementedError()

        if model != InflateSinkModel.__name__:
            raise NotImplementedError()

        if model_params != {}:
            raise NotImplementedError()

        models: List = [{'eid': self._model.eid, 'type': model}]

        return models

    def step(self, time, inputs) -> int:
        if inputs == {}:
            raise NotImplementedError()

        if self._model.eid not in inputs.keys():
            raise NotImplementedError()

        if len(inputs.keys()) != 1:
            raise NotImplementedError()

        data = inputs[self._model.eid]
        print('Length of data to inflate:', len(data))
        data = inflate_data(data=data)
        print('Length of inflated data:', len(data))

        self._model.step(data=data)

        return time + 1

    def get_data(self, outputs) -> dict:
        if self._model.eid not in outputs.keys():
            raise NotImplementedError()
        if len(outputs.keys()) != 1:
            raise NotImplementedError()

        return {}
