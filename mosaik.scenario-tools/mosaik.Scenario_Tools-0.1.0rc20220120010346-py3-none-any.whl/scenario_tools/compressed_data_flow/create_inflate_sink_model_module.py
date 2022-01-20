from mosaik_scenario_tools.scenario_tools.create.create_model_module import \
    create_model
from mosaik_scenario_tools.scenario_tools.compressed_data_flow.\
    inflate_simulator import InflateSimulator
from mosaik_scenario_tools.scenario_tools.compressed_data_flow.\
    inflate_sink_model import InflateSinkModel


def create_inflate_sink_model(world):
    return create_model(
        world=world,
        simulator=InflateSimulator,
        model=InflateSinkModel,
    )
