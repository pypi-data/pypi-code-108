from mosaik_simconfig.simconfig.sim_config import SimConfig

from mosaik_scenario_tools.scenario_tools.create.create_world_module \
    import create_world
from mosaik_scenario_tools.scenario_tools.simulator.buffer_inputs.\
    input_buffering_simulator import InputBufferingSimulator


def input_buffering_scenario() -> None:
    sim_config = SimConfig()
    sim_config.add_in_process(simulator=InputBufferingSimulator)
    world = create_world(sim_config=sim_config)
    end = 1
    world.run(until=end)
    world.shutdown()
