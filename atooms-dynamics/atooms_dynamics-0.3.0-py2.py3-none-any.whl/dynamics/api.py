import numpy
import random

from atooms.core.utils import setup_logging
from atooms.models import f90
from atooms.simulation import Simulation
from atooms.trajectory import Trajectory, TrajectoryXYZ, change_species
from atooms.simulation.observers import write_config, write_thermo, Scheduler, target_rmsd

from .newtonian import VelocityVerlet, NosePoincare
from .stochastic import LangevinOverdamped


# The two runners differ only because of the backend and the
# corresponding input parameters. To reduce the boilerplate we could
# proceed as for postprocessing or with landscape
# TODO: factory / facade?

def md(file_inp, file_out, method='velocity-verlet', model=None,
       T=-1.0, Q=5.0, nsteps=0, interval_thermostat=5000, config_number=0,
       rmsd=-1.0, thermo_number=0, thermo_interval=0, verbose=False,
       seed=1, skin=0.3, dt=0.002, block=''):
    """
    Molecular dynamics simulation
    """

    # Initialize
    random.seed(seed)
    numpy.random.seed(seed)

    # Always log to file
    setup_logging(level=20, filename=file_out + '.log')
    if verbose:
        setup_logging(level=20)

    # Read initial state
    # with f90.Trajectory(file_inp) as th:
    with Trajectory(file_inp) as th:
        system = th[-1]

    # Setup interaction
    system = change_species(system, 'F')
    system.interaction = f90.Interaction(model)
    system.interaction.neighbor_list = f90.VerletList(skin=skin)

    # Simulation backend
    if method == 'velocity-verlet':
        bck = VelocityVerlet(system, timestep=dt)
    elif method == 'nose-poincare':
        bck = NosePoincare(system, timestep=dt, mass=Q, temperature=T)
    elif method == 'massive-thermostat':
        bck = VelocityVerlet(system, timestep=dt)

        def massive_thermostat(sim, T):
            sim.system.temperature = T
    else:
        raise ValueError('unknown method {}'.format(method))

    # Thermostat
    if T > 0:
        system.temperature = T

    # Fix targeting
    if rmsd > 0 and nsteps == 0:
        nsteps = int(1e7)

    # Simulation
    sim = Simulation(bck, output_path=file_out, steps=nsteps, enable_speedometer=True)
    sim.trajectory_class = TrajectoryXYZ
    if method == 'massive-thermostat':
        sim.add(massive_thermostat, interval_thermostat, T)

    # Writing
    if config_number == 0:
        if len(block) > 0:
            sim.add(write_config, Scheduler(block=[int(_) for _ in block.split(',')]))
    else:
        sim.add(write_config, Scheduler(config_number))

    if thermo_number > 0:
        sim.add(write_thermo, Scheduler(calls=thermo_number))
    elif thermo_interval > 0:
        sim.add(write_thermo, Scheduler(thermo_interval))

    if rmsd > 0:
        sim.add(target_rmsd, Scheduler(50000), rmsd)

    # Run
    sim.run()

    # Write final configuration
    with Trajectory(file_out + '.chk.xyz', 'w', fmt='xyz') as th:
        th.variables = ['id', 'pos', 'vel']
        th.precision = 12
        th.write(sim.system)

    return sim.system


def ld(file_inp, file_out, method='overdamped', model=None, T=-1.0,
       nsteps=0, interval_thermostat=5000, config_number=0, rmsd=-1.0,
       thermo_number=0, thermo_interval=0, verbose=False, skin=0.3,
       dt=0.002, friction=1.0, random='PCG', seed=1, block=''):
    """
    Langevin dynamics simulation
    """

    # Random generator
    numpy.random.seed(seed)
    if random in ['PCG', 'PCG64']:
        random = numpy.random.default_rng(seed=seed)
    elif random in ['MT', 'MT19937']:
        random = numpy.random
    else:
        raise ValueError('unknown random generator {}'.format(random))

    # Always log to file
    setup_logging(level=20, filename=file_out + '.log')
    if verbose:
        setup_logging(level=20)

    # Read initial state
    with Trajectory(file_inp) as th:
        system = th[-1]

    # Setup interaction
    system = change_species(system, 'F')
    system.interaction = f90.Interaction(model)
    system.interaction.neighbor_list = f90.VerletList(skin=skin)

    # BACKEND SPECIFIC
    # Simulation backend
    bck = LangevinOverdamped(system, timestep=dt, friction=friction, temperature=T, random=random)

    # Fix targeting
    if rmsd > 0 and nsteps == 0:
        nsteps = int(1e7)

    # Simulation
    sim = Simulation(bck, output_path=file_out, steps=nsteps, enable_speedometer=True)
    sim.trajectory_class = TrajectoryXYZ

    # Writing
    if config_number == 0:
        if len(block) > 0:
            sim.add(write_config, Scheduler(block=[int(_) for _ in block.split(',')]))
    else:
        sim.add(write_config, Scheduler(config_number))

    if thermo_number > 0:
        sim.add(write_thermo, Scheduler(calls=thermo_number))
    elif thermo_interval > 0:
        sim.add(write_thermo, Scheduler(thermo_interval))

    if rmsd > 0:
        sim.add(target_rmsd, Scheduler(50000), rmsd)

    # Run
    sim.run()

    # Write final configuration
    with Trajectory(file_out + '.chk.xyz', 'w', fmt='xyz') as th:
        th.variables = ['id', 'pos', 'vel']
        th.precision = 12
        th.write(sim.system)

    return sim.system


if __name__ == '__main__':
    import argh
    argh.dispatch_command(md)
