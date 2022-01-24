from mosaik_scenario_tools.scenario_tools.create.create_model_module import \
    create_model

from mosaik_schedule_flocker.schedule_flocker.mosaik.source.\
    flocker_source_model import FlockerSourceModel
from mosaik_schedule_flocker.schedule_flocker.mosaik.source.\
    flocker_source_simulator import FlockerSourceSimulator


def create_flocker_source_model(world) -> FlockerSourceModel:
    flocker_source_model: FlockerSourceModel = create_model(
        simulator=FlockerSourceSimulator,
        model=FlockerSourceModel,
        world=world,
    )

    return flocker_source_model
