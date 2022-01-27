from typing import List

from mosaik_api import Simulator

from mosaik_scenario_tools.scenario_tools.compressed_data_flow.deflate_module \
    import deflate_data_logged
from mosaik_scenario_tools.scenario_tools.compressed_data_flow.\
    deflate_simulator_meta import DEFLATE_META
from mosaik_scenario_tools.scenario_tools.compressed_data_flow. \
    deflate_source_model import DeflateSourceModel


class DeflateSimulator(Simulator):
    def __init__(self):
        super().__init__(meta=DEFLATE_META)

        self._data: dict = {}
        self._eid: str = DeflateSimulator.__name__

        eid = DeflateSourceModel.__name__ + '-0'
        self._model = DeflateSourceModel(eid=eid)

    def create(
        self, num=1, model=DeflateSourceModel.__name__, **model_params
    ) -> List:
        if num != 1:
            raise NotImplementedError()

        if model != DeflateSourceModel.__name__:
            raise NotImplementedError()

        if model_params != {}:
            raise NotImplementedError()

        models: List = [{'eid': self._model.eid, 'type': model}]

        return models

    def step(self, time, inputs) -> int:
        if inputs != {}:
            raise NotImplementedError()

        self._model.step()

        return time + 1

    def get_data(self, outputs) -> dict:
        if self._model.eid not in outputs.keys():
            raise NotImplementedError()
        if len(outputs.keys()) != 1:
            raise NotImplementedError()

        outputs: dict = {
            self._model.eid: deflate_data_logged(data=self._model.get_data())
        }

        return outputs
