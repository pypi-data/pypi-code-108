from mosaik_scenario_tools.scenario_tools.create.create_model_module import \
    create_model

from mosaik_schedule_flocker.schedule_flocker.mosaik.sink.flocker_sink_model \
    import FlockerSinkModel
from mosaik_schedule_flocker.schedule_flocker.mosaik.sink.\
    flocker_sink_simulator import FlockerSinkSimulator


def create_flocker_sink_model(world) -> FlockerSinkModel:
    flock_sink_model: FlockerSinkModel = create_model(
        model=FlockerSinkModel,
        simulator=FlockerSinkSimulator,
        world=world,
    )

    return flock_sink_model
