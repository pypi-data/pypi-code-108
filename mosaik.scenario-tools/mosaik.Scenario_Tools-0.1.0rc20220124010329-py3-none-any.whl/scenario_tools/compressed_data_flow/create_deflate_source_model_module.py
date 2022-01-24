from mosaik_scenario_tools.scenario_tools.compressed_data_flow.\
    deflate_simulator import DeflateSimulator
from mosaik_scenario_tools.scenario_tools.compressed_data_flow.\
    deflate_source_model import DeflateSourceModel
from mosaik_scenario_tools.scenario_tools.create.create_model_module import \
    create_model


def create_deflate_source_model(world):
    return create_model(
        world=world,
        simulator=DeflateSimulator,
        model=DeflateSourceModel,
    )
