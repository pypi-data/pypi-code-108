from mosaik.scenario import World
from mosaik_simconfig.simconfig.sim_config import SimConfig

from mosaik_schedule_flocker.schedule_flocker.mosaik.create.\
    create_flocker_model_module import create_flocker_model
from mosaik_schedule_flocker.schedule_flocker.mosaik.create.\
    create_flocker_sink_model_module import create_flocker_sink_model
from mosaik_schedule_flocker.schedule_flocker.mosaik.create.\
    create_flocker_source_model_module import create_flocker_source_model
from mosaik_schedule_flocker.schedule_flocker.mosaik.flocker.flocker_simulator \
    import FlockerSimulator
from mosaik_schedule_flocker.schedule_flocker.mosaik.sink.\
    flocker_sink_simulator import FlockerSinkSimulator
from mosaik_schedule_flocker.schedule_flocker.mosaik.source.\
    flocker_source_simulator import FlockerSourceSimulator


def source_flocker_sink_scenario(mosaik_port, end):
    # Configure the simulation
    sim_config = SimConfig()
    sim_config.add_in_process(simulator=FlockerSourceSimulator)
    sim_config.add_in_process(simulator=FlockerSimulator)
    sim_config.add_in_process(simulator=FlockerSinkSimulator)
    mosaik_config = {
        'addr': ('127.0.0.1', mosaik_port),
    }
    world = World(
        sim_config=sim_config,
        mosaik_config=mosaik_config,
    )

    # Instantiate models
    flocker_source_model = create_flocker_source_model(world=world)
    flocker_model = create_flocker_model(world=world)
    flock_sink_model = create_flocker_sink_model(world=world)

    # Connect entities
    world.connect(
        flocker_source_model, flocker_model,
        ('config', 'config'),
    )
    world.connect(
        flocker_model, flock_sink_model,
        ('flexibility_schedules', 'flexibility_schedules'),
    )

    # Run simulation
    world.run(until=end)
    world.shutdown()
