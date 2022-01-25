from mosaik_simconfig.simconfig.sim_config import SimConfig

from mosaik_scenario_tools.scenario_tools.create.create_world_module \
    import create_world
from mosaik_scenario_tools.scenario_tools.simulator.manage_inputs.\
    input_managing_simulator import \
    InputManagingSimulator


def input_managing_scenario() -> None:
    sim_config = SimConfig()
    sim_config.add_in_process(simulator=InputManagingSimulator)
    world = create_world(sim_config=sim_config)
    end = 1
    world.run(until=end)
    world.shutdown()
