from mosaik_scenario_tools.scenario_tools.create.create_model_module import \
    create_model

from mosaik_schedule_flocker.schedule_flocker.mosaik.flocker.flocker_model \
    import FlockerModel
from mosaik_schedule_flocker.schedule_flocker.mosaik.flocker.\
    flocker_simulator import FlockerSimulator


def create_flocker_model(world) -> FlockerModel:
    flocker_model: FlockerModel = create_model(
        model=FlockerModel,
        simulator=FlockerSimulator,
        world=world,
    )

    return flocker_model
